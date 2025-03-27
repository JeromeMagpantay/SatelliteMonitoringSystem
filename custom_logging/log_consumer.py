from datetime import datetime
from dotenv import load_dotenv
import json
import os
import pika
from pymongo import MongoClient


def setup_consumer():
    load_dotenv()
    mongo_client = MongoClient(os.getenv("MONGO_CREDETIALS"))
    db = mongo_client.Nebula
    logs_collection = db.SatelliteLogs
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    channel.exchange_declare(
        exchange='satellite_logs',
        exchange_type='topic',
        durable=True
    )
    channel.queue_declare(queue='satellite_logs', durable=True)
    channel.queue_bind(
        exchange='satellite_logs',
        queue='satellite_logs',
        routing_key='satellite.*'
    )
    
    def callback(ch, method, properties, body):
        try:
            log_entry = json.loads(body)
            log_entry["timestamp"] = datetime.now()
            log_entry["routing_key"] = method.routing_key
            
            logs_collection.insert_one(log_entry)
            
            ts = log_entry["timestamp"].strftime('%Y-%m-%d %H:%M:%S')
            if method.routing_key == 'satellite.outage':
                print(f"[OUTAGE][{ts}] {log_entry['satellite_id']} failed")
            elif method.routing_key == 'satellite.assigned':
                print(f"[ASSIGN][{ts}] {log_entry['satellite_id']} to R{log_entry['region']}")
            elif method.routing_key == 'satellite.reassigned':
                peak_note = "PEAK BOOST" if log_entry.get("peak_boost") else ""
                print(f"[REASSIGN][{ts}] {log_entry['satellite_id']} to R{log_entry['region']} {peak_note}")
            elif method.routing_key.startswith('system.'):
                print(f"[SYSTEM][{ts}] {log_entry['message']}")
                
        except Exception as e:
            print(f"Error processing message: {str(e)}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(
        queue='satellite_logs',
        on_message_callback=callback,
        auto_ack=False
    )
    
    print("[*] Waiting for logs. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    setup_consumer()