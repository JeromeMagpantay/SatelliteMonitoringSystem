from random import randint
import time

class Satellite:
    def __init__(self, id, classification):
        self.id = id
        self.classification = classification
        self.capacity = self._get_capacity(classification)
        self.status = "INACTIVE - AVAILABLE"
        self.region = None
        self.outage_start_time = None

    def _get_capacity(self, classification):
        return {
            'HIGH': 200000,
            'MEDIUM': 100000,
            'LOW': 50000
        }[classification]

    def assign_to_region(self, region):
        if self.status == "INACTIVE - AVAILABLE":
            self.region = region
            self.status = "ACTIVE"
        else:
            raise ValueError("Satellite not available for assignment.")

    def power_outage(self):
        if self.status == "ACTIVE":
            if randint(1, 100) <= 10:  # 10% chance
                self.status = "INACTIVE - UNAVAILABLE"
                self.region = None
                self.outage_start_time = time.time()
                return True
        return False

    def check_restore(self):
        if self.status == "INACTIVE - UNAVAILABLE" and self.outage_start_time is not None:
            if time.time() - self.outage_start_time >= 5:   # Automated reboot time, assume 5 seconds.
                self.status = "INACTIVE - AVAILABLE"
                self.outage_start_time = None
                return True
        return False

    def broadcast_status(self):
        if self.status == "INACTIVE - AVAILABLE":
            return {"satellite_id": self.id, "status": "INACTIVE", "reason": "AVAILABLE"}
        elif self.status == "INACTIVE - UNAVAILABLE":
            return {"satellite_id": self.id, "status": "INACTIVE", "reason": "UNAVAILABLE"}
        elif self.status == "ACTIVE":
            return {"satellite_id": self.id, "status": "ACTIVE", "assigned_region": self.region['region_number']}