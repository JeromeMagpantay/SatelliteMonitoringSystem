import json
import pika

class StatusLogger:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        
        self.channel.exchange_declare(
            exchange='satellite_logs', 
            exchange_type='topic',
            durable=True
        )
        
    def log(self, routing_key, message):
        self.channel.basic_publish(
            exchange='satellite_logs',
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  
            ))
        
    def close(self):
        self.connection.close()