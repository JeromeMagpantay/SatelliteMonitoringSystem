import time
import requests
from datetime import datetime
from satellite import Satellite
from logging.rabbitmq_logs import StatusLogger

REGION_API_URL = "http://localhost:8000/regions"
UPDATE_INTERVAL = 10  # Check every 10 seconds

# Constants for satellite capacities and reserved spares
CAPACITIES = {"HIGH": 200000, "MEDIUM": 100000, "LOW": 50000}
SPARES = {"HIGH": 5, "MEDIUM": 5, "LOW": 5}

def is_peak_time(peak_start: str, peak_end: str) -> bool:
    """Check if current UTC time is within peak window"""
    try:
        now = datetime.utcnow().time()
        start = datetime.strptime(peak_start, "%H:%M:%S").time()
        end = datetime.strptime(peak_end, "%H:%M:%S").time()
        
        if start < end:
            return start <= now < end
        else:
            return now >= start or now < end
    except ValueError as e:
        print(f"Invalid time format: {e}")
        return False

# Assumption: Load is 20% higher during peak times.
def calculate_required_load(region: dict) -> int:
    base = region["number_of_clients"]
    if is_peak_time(region["peak_usage_start_time"], region["peak_usage_end_time"]):
        return int(base * 1.2)
    return base

# Better to provide service with higher power satellites. Then
# use either a medium or a low power, depending on  the remaining load.
# This way it's less wasted capacity.
def compute_satellite_assignment(required_load: int) -> dict:
    assignment = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    high_count = required_load // CAPACITIES["HIGH"]
    assignment["HIGH"] = high_count
    remaining = required_load - high_count * CAPACITIES["HIGH"]

    if remaining == 0:
        return assignment

    if remaining <= CAPACITIES["LOW"]:
        assignment["LOW"] += 1
    elif remaining <= CAPACITIES["MEDIUM"]:
        assignment["MEDIUM"] += 1
    elif remaining <= (CAPACITIES["MEDIUM"] + CAPACITIES["LOW"]):
        assignment["MEDIUM"] += 1
        assignment["LOW"] += 1
    else:
        assignment["MEDIUM"] += 2

    return assignment

class SatelliteNetwork:
    def __init__(self):
        self.satellites = []
        self.logger = StatusLogger()
        self.initialize_satellites()

    def initialize_satellites(self):
        for i in range(1, 50):
            self.satellites.append(Satellite(f"HIGH-{i}", "HIGH"))
        for i in range(1, 30):
            self.satellites.append(Satellite(f"MEDIUM-{i}", "MEDIUM"))
        for i in range(1, 30):
            self.satellites.append(Satellite(f"LOW-{i}", "LOW"))

    def fetch_regions(self):
        try:
            response = requests.get(REGION_API_URL)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.log("system.error", {"message": f"Region fetch error: {e}"})
            return []

    def assign_initial_satellites(self):
        regions = self.fetch_regions()
        available = {
            "HIGH": [sat for sat in self.satellites 
                    if sat.classification == "HIGH" and sat.status == "INACTIVE - AVAILABLE"],
            "MEDIUM": [sat for sat in self.satellites 
                      if sat.classification == "MEDIUM" and sat.status == "INACTIVE - AVAILABLE"],
            "LOW": [sat for sat in self.satellites 
                   if sat.classification == "LOW" and sat.status == "INACTIVE - AVAILABLE"]
        }
        
        # Reserve spares
        for level in available:
            available[level] = available[level][SPARES[level]:]

        for region in regions:
            required = region["number_of_clients"]
            assignment = compute_satellite_assignment(required)
            for classification, count in assignment.items():
                for _ in range(count):
                    if available[classification]:
                        sat = available[classification].pop(0)
                        sat.assign_to_region(region)
                        self.logger.log("satellite.assigned", {
                            "satellite_id": sat.id,
                            "region": region['region_number'],
                            "capacity": CAPACITIES[classification]
                        })
                    else:
                        self.logger.log("system.warning", {
                            "message": f"Not enough {classification} satellites for region {region['region_number']}"
                        })

    def get_region_capacity(self, region) -> int:
        total = 0
        for sat in self.satellites:
            if sat.region and sat.region['region_number'] == region['region_number'] and sat.status == "ACTIVE":
                total += CAPACITIES[sat.classification]
        return total

    def check_outages(self):
        for sat in self.satellites:
            if sat.power_outage():
                self.logger.log("satellite.outage", {
                    "satellite_id": sat.id,
                    "timestamp": time.time(),
                    "last_region": sat.region['region_number'] if sat.region else None
                })

    def check_restorations(self):
        for sat in self.satellites:
            if sat.check_restore():
                self.logger.log("satellite.restored", {
                    "satellite_id": sat.id,
                    "downtime": time.time() - sat.outage_start_time if sat.outage_start_time else 0
                })

    def replenish_regions(self):
        regions = self.fetch_regions()
        available = {
            "HIGH": [sat for sat in self.satellites 
                    if sat.classification == "HIGH" and sat.status == "INACTIVE - AVAILABLE"],
            "MEDIUM": [sat for sat in self.satellites 
                      if sat.classification == "MEDIUM" and sat.status == "INACTIVE - AVAILABLE"],
            "LOW": [sat for sat in self.satellites 
                   if sat.classification == "LOW" and sat.status == "INACTIVE - AVAILABLE"]
        }

        for region in regions:
            required = calculate_required_load(region)  # Dynamic load calculation
            current_capacity = self.get_region_capacity(region)
            shortfall = required - current_capacity
            
            if shortfall > 0:
                assignment = compute_satellite_assignment(shortfall)
                for classification, count in assignment.items():
                    for _ in range(count):
                        if available[classification]:
                            sat = available[classification].pop(0)
                            sat.assign_to_region(region)
                            self.logger.log("satellite.reassigned", {
                                "satellite_id": sat.id,
                                "region": region['region_number'],
                                "shortfall": shortfall,
                                "new_capacity": current_capacity + CAPACITIES[classification],
                                "peak_boost": is_peak_time(
                                    region["peak_usage_start_time"],
                                    region["peak_usage_end_time"]
                                )
                            })
                        else:
                            self.logger.log("system.warning", {
                                "message": f"Can't replenish region {region['region_number']} with {classification} satellites"
                            })

    def log_satellite_statuses(self):
        for sat in self.satellites:
            self.logger.log("satellite.status", {
                "id": sat.id,
                "status": sat.status,
                "region": sat.region['region_number'] if sat.region else None,
                "timestamp": time.time(),
                "classification": sat.classification
            })

    def start_network(self):
        try:
            self.assign_initial_satellites()
            self.logger.log("system.start", {"message": "Network online..."})
            
            while True:
                self.logger.log("system.cycle", {"message": "New Update Cycle"})
                self.check_outages()
                self.check_restorations()
                self.replenish_regions()
                self.log_satellite_statuses()
                time.sleep(UPDATE_INTERVAL)
                
        except KeyboardInterrupt:
            self.logger.log("system.stop", {"message": "Simulation stopped by user..."})
        except Exception as e:
            print("Error in simulation:", e)
            self.logger.log("system.error", {"message": f"Critical error: {str(e)}"})
        finally:
            self.logger.close()

if __name__ == "__main__":
    network = SatelliteNetwork()
    network.start_satellite_network()