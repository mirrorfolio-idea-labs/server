from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from .database import Base

class SensorData(Base):
    """Model for storing sensor data from ESP32 devices"""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Common sensor fields - adjust based on your ESP32 sensors
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)

    # Additional data as JSON for flexibility
    additional_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<SensorData(id={self.id}, device_id={self.device_id}, timestamp={self.timestamp})>"
