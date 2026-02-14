from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class SensorDataCreate(BaseModel):
    """Schema for creating sensor data (from ESP32)"""
    device_id: str = Field(..., description="Unique identifier for the ESP32 device")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    pressure: Optional[float] = Field(None, description="Pressure in hPa")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Any additional sensor data")

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "ESP32_001",
                "temperature": 25.5,
                "humidity": 60.0,
                "pressure": 1013.25,
                "additional_data": {"battery": 85, "signal_strength": -45}
            }
        }

class SensorDataResponse(BaseModel):
    """Schema for sensor data response"""
    id: int
    device_id: str
    timestamp: datetime
    temperature: Optional[float]
    humidity: Optional[float]
    pressure: Optional[float]
    additional_data: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    status: str = "success"
