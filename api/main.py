from aio_pika import connect_robust, IncomingMessage
import asyncio
from datetime import datetime 
from dotenv import load_dotenv 
from fastapi import Body, FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import LogEntry, Region
import motor.motor_asyncio
import os
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
CONNECTION_STRING = os.getenv("MONGO_CREDETIALS")

client = motor.motor_asyncio.AsyncIOMotorClient(CONNECTION_STRING)
db = client.Nebula
region_collection = db.Region
logs_collection = db.SatelliteLogs 

@app.get("/regions", response_model=List[Region])
async def get_regions():
    regions = await region_collection.find().to_list(100)
    return regions

@app.get("/regions/{region_id}", response_model=Region)
async def get_region(region_id: int):
    region = await region_collection.find_one({"region_number": region_id})
    return region

@app.put("/regions/{region_id}", response_model=Region)
async def update_region(
    region_id: int,
    satellite_providers: Optional[List[str]] = Body(None),
    coverage_flag: Optional[bool] = Body(None)
):
    update_data = {}
    if satellite_providers is not None:
        update_data["satellite_providers"] = satellite_providers
    if coverage_flag is not None:
        update_data["coverage_flag"] = coverage_flag
        
    await region_collection.update_one(
        {"region_number": region_id},
        {"$set": update_data}
    )
    return await region_collection.find_one({"region_number": region_id})


@app.get("/logs", response_model=List[LogEntry])
async def get_logs(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    type: Optional[str] = None,
    limit: int = 100
):
    logs = await logs_collection.find().to_list(limit)
    return logs

@app.get("/logs/{region_id}", response_model=List[LogEntry])
async def get_logs_by_region(
    region_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    type: Optional[str] = None,
    limit: int = 100
):
    cursor = logs_collection.find({"region": region_id})
    logs = await cursor.to_list(length=limit)
    return logs
