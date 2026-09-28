from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    ForeignKey
)

from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    district = Column(String, nullable=False)
    state = Column(String, nullable=False)

    beekeepers = relationship(
        "Beekeeper",
        back_populates="cluster"
    )


class Beekeeper(Base):
    __tablename__ = "beekeepers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    phone = Column(String)
    village = Column(String)

    cluster_id = Column(
        Integer,
        ForeignKey("clusters.id")
    )

    cluster = relationship(
        "Cluster",
        back_populates="beekeepers"
    )

    hives = relationship(
        "Hive",
        back_populates="beekeeper"
    )


class Hive(Base):
    __tablename__ = "hives"

    id = Column(Integer, primary_key=True, index=True)

    hive_code = Column(
        String,
        unique=True,
        nullable=False
    )

    location = Column(String)

    beekeeper_id = Column(
        Integer,
        ForeignKey("beekeepers.id")
    )

    beekeeper = relationship(
        "Beekeeper",
        back_populates="hives"
    )

    sensor_readings = relationship(
        "SensorReading",
        back_populates="hive"
    )

    health_records = relationship(
        "HealthRecord",
        back_populates="hive"
    )

    batches = relationship(
        "HoneyBatch",
        back_populates="hive"
    )


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)

    hive_id = Column(
        Integer,
        ForeignKey("hives.id")
    )

    temperature = Column(Float)
    humidity = Column(Float)
    hive_weight = Column(Float)
    acoustic_level = Column(Float)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    hive = relationship(
        "Hive",
        back_populates="sensor_readings"
    )


class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)

    hive_id = Column(
        Integer,
        ForeignKey("hives.id")
    )

    health_status = Column(String)
    disease_risk = Column(String)
    health_score = Column(Float)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    hive = relationship(
        "Hive",
        back_populates="health_records"
    )


class HoneyBatch(Base):
    __tablename__ = "honey_batches"

    id = Column(Integer, primary_key=True, index=True)

    batch_code = Column(
        String,
        unique=True,
        nullable=False
    )

    hive_id = Column(
        Integer,
        ForeignKey("hives.id")
    )

    harvest_date = Column(DateTime)

    quantity_kg = Column(Float)

    status = Column(String, default="HARVESTED")

    hive = relationship(
        "Hive",
        back_populates="batches"
    )

    lab_tests = relationship(
        "LabTest",
        back_populates="batch"
    )

    traceability_events = relationship(
        "TraceabilityEvent",
        back_populates="batch"
    )


class LabTest(Base):
    __tablename__ = "lab_tests"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(
        Integer,
        ForeignKey("honey_batches.id")
    )

    purity_status = Column(String)
    moisture_percent = Column(Float)
    test_result = Column(String)

    tested_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    batch = relationship(
        "HoneyBatch",
        back_populates="lab_tests"
    )


class TraceabilityEvent(Base):
    __tablename__ = "traceability_events"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(
        Integer,
        ForeignKey("honey_batches.id")
    )

    event_type = Column(String)
    location = Column(String)
    description = Column(Text)

    previous_hash = Column(String)
    current_hash = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    batch = relationship(
        "HoneyBatch",
        back_populates="traceability_events"
    )