from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv

from .database import get_db, init_db
from .models import SensorData
from .schemas import SensorDataCreate, SensorDataResponse, MessageResponse

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ESP32 Data Collection API",
    description="Backend API for receiving and storing data from ESP32 devices",
    version="1.0.0"
)

# CORS configuration - adjust origins as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your ESP32 IPs or domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key from environment variable
API_KEY = os.getenv("API_KEY", "dev-key-change-in-production")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key for secure endpoints"""
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return x_api_key

@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint - health check"""
    return MessageResponse(
        message="ESP32 Data Collection API is running",
        status="success"
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "esp32-api"}

@app.post("/api/data", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def receive_sensor_data(
    data: SensorDataCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Receive sensor data from ESP32 device

    Requires API key in X-API-Key header
    """
    try:
        # Create new sensor data entry
        db_sensor_data = SensorData(
            device_id=data.device_id,
            temperature=data.temperature,
            humidity=data.humidity,
            pressure=data.pressure,
            additional_data=data.additional_data
        )
        db.add(db_sensor_data)
        db.commit()
        db.refresh(db_sensor_data)

        return MessageResponse(
            message=f"Data received successfully from device {data.device_id}",
            status="success"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing data: {str(e)}"
        )

@app.get("/api/data", response_model=List[SensorDataResponse])
async def get_sensor_data(
    skip: int = 0,
    limit: int = 100,
    device_id: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Retrieve sensor data with optional filtering

    Query parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - device_id: Filter by specific device ID (optional)
    """
    if limit > 1000:
        limit = 1000

    query = db.query(SensorData)

    if device_id:
        query = query.filter(SensorData.device_id == device_id)

    data = query.order_by(SensorData.timestamp.desc()).offset(skip).limit(limit).all()
    return data

@app.get("/api/data/{data_id}", response_model=SensorDataResponse)
async def get_sensor_data_by_id(
    data_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get specific sensor data entry by ID"""
    data = db.query(SensorData).filter(SensorData.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data with ID {data_id} not found"
        )
    return data

@app.get("/api/devices", response_model=List[str])
async def get_devices(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get list of all unique device IDs"""
    devices = db.query(SensorData.device_id).distinct().all()
    return [device[0] for device in devices]

# Vercel serverless function handler
handler = app
