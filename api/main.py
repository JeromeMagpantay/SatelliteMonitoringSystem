import asyncio
from datetime import datetime 
from dotenv import load_dotenv 
from fastapi import FastAPI, WebSocket
from models import Region
import motor.motor_asyncio
import os
import pika
from typing import List, Optional

app = FastAPI()

load_dotenv()
CONNECTION_STRING = os.getenv("MONGO_CREDETIALS")

client = motor.motor_asyncio.AsyncIOMotorClient(CONNECTION_STRING)
db = client.Nebula
region_collection = db.Region
logs_collection = db.Logs 

@app.get("/regions", response_model=List[Region])
async def get_regions():
    regions = await region_collection.find().to_list(100)
    return regions

@app.get("/region/{region_id}", response_model=Region)
async def get_region(region_id: str):
    region = await region_collection.find_one({"_id": region_id})
    return region

@app.websocket("/ws/regions")
async def region_updates(websocket: WebSocket):
    await websocket.accept()
    while True:
        regions = await region_collection.find().to_list(100)
        await websocket.send_json(regions)
        await asyncio.sleep(5)

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    def on_message(ch, method, properties, body):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(websocket.send_text(body.decode()))
    
    channel.basic_consume(
        queue='satellite_logs',
        on_message_callback=on_message,
        auto_ack=True
    )
    
    try:
        channel.start_consuming()
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        channel.stop_consuming()
        connection.close()

@app.get("/logs")
async def get_logs(
    limit: int = 100,
    type: Optional[str] = None, 
    start: Optional[datetime] = None, 
    end: Optional[datetime] = None
):
    query = {}
    if type:
        query["routing_key"] = type
    if start and end:
        query["timestamp"] = {"$gte": start, "$lte": end}
    
    logs = await logs_collection.find(query).sort("timestamp", -1).to_list(limit)
    return logs