from aio_pika import connect_robust, IncomingMessage
import asyncio
from datetime import datetime 
from dotenv import load_dotenv 
from fastapi import FastAPI, WebSocket
from models import LogEntry, Region
import motor.motor_asyncio
import os
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


@app.get("/logs", response_model=List[LogEntry])
async def get_logs(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    type: Optional[str] = None,
    limit: int = 100
):
    logs = await logs_collection.find().to_list(100)
    return logs

