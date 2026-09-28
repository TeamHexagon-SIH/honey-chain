from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models import Hive, SensorReading


router = APIRouter(
    prefix="/api/sensors",
    tags=["IoT Sensors"]
)


@router.post("/readings")
def create_sensor_reading(
    hive_id: int,
    temperature: float,
    humidity: float,
    hive_weight: float,
    acoustic_level: float,
    db: Session = Depends(get_db)
):
    hive = db.query(Hive).filter(
        Hive.id == hive_id
    ).first()

    if not hive:
        return {
            "error": "Hive not found"
        }

    reading = SensorReading(
        hive_id=hive_id,
        temperature=temperature,
        humidity=humidity,
        hive_weight=hive_weight,
        acoustic_level=acoustic_level,
        timestamp=datetime.utcnow()
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return {
        "message": "Sensor reading recorded",
        "reading": {
            "id": reading.id,
            "hive_id": reading.hive_id,
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "hive_weight": reading.hive_weight,
            "acoustic_level": reading.acoustic_level,
            "timestamp": reading.timestamp
        }
    }


@router.get("/hive/{hive_id}")
def get_hive_readings(
    hive_id: int,
    db: Session = Depends(get_db)
):
    hive = db.query(Hive).filter(
        Hive.id == hive_id
    ).first()

    if not hive:
        return {
            "error": "Hive not found"
        }

    readings = (
        db.query(SensorReading)
        .filter(SensorReading.hive_id == hive_id)
        .order_by(SensorReading.timestamp.desc())
        .all()
    )

    return [
        {
            "id": reading.id,
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "hive_weight": reading.hive_weight,
            "acoustic_level": reading.acoustic_level,
            "timestamp": reading.timestamp
        }
        for reading in readings
    ]


@router.get("/latest/{hive_id}")
def get_latest_reading(
    hive_id: int,
    db: Session = Depends(get_db)
):
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.hive_id == hive_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    if not reading:
        return {
            "error": "No sensor data available"
        }

    return {
        "hive_id": hive_id,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "hive_weight": reading.hive_weight,
        "acoustic_level": reading.acoustic_level,
        "timestamp": reading.timestamp
    }