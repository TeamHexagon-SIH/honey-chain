from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    HoneyBatch,
    Hive,
    Beekeeper,
    Cluster,
    HealthRecord,
    LabTest,
    TraceabilityEvent
)

from ..blockchain import verify_chain


router = APIRouter(
    prefix="/api/verify",
    tags=["Consumer Verification"]
)


@router.get("/{batch_code}")
def verify_batch(
    batch_code: str,
    db: Session = Depends(get_db)
):

    # Find batch
    batch = db.query(HoneyBatch).filter(
        HoneyBatch.batch_code == batch_code
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    # Find hive
    hive = db.query(Hive).filter(
        Hive.id == batch.hive_id
    ).first()

    # Find beekeeper
    beekeeper = None

    if hive:
        beekeeper = db.query(Beekeeper).filter(
            Beekeeper.id == hive.beekeeper_id
        ).first()

    # Find cluster
    cluster = None

    if beekeeper:
        cluster = db.query(Cluster).filter(
            Cluster.id == beekeeper.cluster_id
        ).first()

    # Latest AI health record
    health = None

    if hive:
        health = (
            db.query(HealthRecord)
            .filter(
                HealthRecord.hive_id == hive.id
            )
            .order_by(HealthRecord.id.desc())
            .first()
        )

    # Lab tests
    lab_tests = (
        db.query(LabTest)
        .filter(
            LabTest.batch_id == batch.id
        )
        .order_by(LabTest.id.asc())
        .all()
    )

    # Traceability events
    events = (
        db.query(TraceabilityEvent)
        .filter(
            TraceabilityEvent.batch_id == batch.id
        )
        .order_by(TraceabilityEvent.id.asc())
        .all()
    )

    # Verify cryptographic chain
    chain_result = verify_chain(events)

    return {
        "verified": chain_result["valid"],

        "batch": {
            "batch_id": batch.id,
            "batch_code": batch.batch_code,
            "harvest_date": batch.harvest_date,
            "quantity_kg": batch.quantity_kg,
            "status": batch.status
        },

        "hive": {
            "hive_id": hive.id if hive else None,
            "hive_code": hive.hive_code if hive else None,
            "location": hive.location if hive else None
        },

        "beekeeper": {
            "name": beekeeper.name if beekeeper else None,
            "village": beekeeper.village if beekeeper else None
        },

        "cluster": {
            "name": cluster.name if cluster else None,
            "district": cluster.district if cluster else None,
            "state": cluster.state if cluster else None
        },

        "ai_health": {
            "status": health.health_status if health else None,
            "disease_risk": health.disease_risk if health else None,
            "health_score": health.health_score if health else None
        },

        "lab_tests": [
            {
                "purity_status": test.purity_status,
                "moisture_percent": test.moisture_percent,
                "test_result": test.test_result,
                "tested_at": test.tested_at
            }
            for test in lab_tests
        ],

        "traceability": [
            {
                "event_type": event.event_type,
                "location": event.location,
                "description": event.description,
                "timestamp": event.created_at,
                "hash": event.current_hash
            }
            for event in events
        ],

        "tamper_check": chain_result
    }