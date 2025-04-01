from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_core import core_schema
from typing import Any, Literal, List, Optional


# Needed  to handle Mongo's ObjectIDs.
# Ref: https://docs.pydantic.dev/latest/api/pydantic_core_schema/#pydantic_core.core_schema.simple_ser_schema
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),

            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectID format")
        return ObjectId(value)

class Region(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None) 
    name: str = Field(...)                                      
    region_number: int = Field(...)
    number_of_clients: int = Field(...)
    peak_usage_start_time: str = Field(...)             # Format: HH:MM:SS, so the time is in UTC 
    peak_usage_end_time: str = Field(...)               # makes sense in reference to EST as per Ontario
    coverage_flag: bool = Field(...)                    # Is the region coverage?
    satellite_providers: List[str] | List[None] = Field(...)

    class Config:
        json_encoders = {ObjectId: str}

class LogEntry(BaseModel):
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    status: Optional[Literal["INACTIVE - AVAILABLE", "INACTIVE - UNAVAILABLE", "ACTIVE"]] = None
    classification: Optional[Literal["HIGH", "MEDIUM", "LOW"]] = None
    routing_key: Optional[str] = None
    satellite_id: Optional[str] = Field(alias="id")
    region: Optional[int] = None  
    peak_boost: Optional[bool] = None
    object_id: Optional[PyObjectId] = Field(alias="_id", default=None) 

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        arbitrary_types_allowed = True
        populate_by_name = True