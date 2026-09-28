from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    HoneyBatch,
    Hive,
    HealthRecord,
    LabTest,
    TraceabilityEvent
)

from ..blockchain import (
    calculate_event_hash,
    verify_chain,
    simulate_tampering,
    restore_demo_chain,
    GENESIS_HASH
)

from ..qr import generate_qr


router = APIRouter(
    prefix="/api/batches",
    tags=["Honey Traceability"]
)


@router.post("/")
def create_batch(
    hive_id: int,
    batch_code: str,
    quantity_kg: float,
    harvest_date: datetime | None = None,
    db: Session = Depends(get_db)
):

    hive = db.query(Hive).filter(
        Hive.id == hive_id
    ).first()

    if not hive:
        raise HTTPException(
            status_code=404,
            detail="Hive not found"
        )

    existing_batch = db.query(HoneyBatch).filter(
        HoneyBatch.batch_code == batch_code
    ).first()

    if existing_batch:
        raise HTTPException(
            status_code=400,
            detail="Batch code already exists"
        )

    if harvest_date is None:
        harvest_date = datetime.utcnow()

    batch = HoneyBatch(
        batch_code=batch_code,
        hive_id=hive_id,
        harvest_date=harvest_date,
        quantity_kg=quantity_kg,
        status="HARVESTED"
    )

    db.add(batch)
    db.commit()
    db.refresh(batch)

    latest_health = (
        db.query(HealthRecord)
        .filter(HealthRecord.hive_id == hive_id)
        .order_by(HealthRecord.id.desc())
        .first()
    )

    health_info = "No AI health record available."

    if latest_health:
        health_info = (
            f"Latest AI health status: "
            f"{latest_health.health_status}, "
            f"health score: {latest_health.health_score}"
        )

    event_type = "HARVEST"
    location = hive.location

    description = (
        f"Honey harvested from hive "
        f"{hive.hive_code}. {health_info}"
    )

    previous_hash = GENESIS_HASH
    created_at = datetime.utcnow()

    current_hash = calculate_event_hash(
        batch.id,
        event_type,
        location,
        description,
        previous_hash,
        created_at
    )

    event = TraceabilityEvent(
        batch_id=batch.id,
        event_type=event_type,
        location=location,
        description=description,
        previous_hash=previous_hash,
        current_hash=current_hash,
        created_at=created_at
    )

    db.add(event)
    db.commit()

    return {
        "message": "Honey batch created successfully.",
        "batch_id": batch.id,
        "batch_code": batch.batch_code,
        "status": batch.status,
        "traceability_event": "HARVEST",
        "hash": current_hash
    }


@router.get("/")
def get_batches(
    db: Session = Depends(get_db)
):
    return db.query(HoneyBatch).all()


@router.get("/{batch_id}")
def get_batch(
    batch_id: int,
    db: Session = Depends(get_db)
):

    batch = db.query(HoneyBatch).filter(
        HoneyBatch.id == batch_id
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    return batch


@router.post("/{batch_id}/events")
def add_traceability_event(
    batch_id: int,
    event_type: str,
    location: str,
    description: str,
    db: Session = Depends(get_db)
):

    batch = db.query(HoneyBatch).filter(
        HoneyBatch.id == batch_id
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    latest_event = (
        db.query(TraceabilityEvent)
        .filter(
            TraceabilityEvent.batch_id == batch_id
        )
        .order_by(TraceabilityEvent.id.desc())
        .first()
    )

    if latest_event:
        previous_hash = latest_event.current_hash
    else:
        previous_hash = GENESIS_HASH

    created_at = datetime.utcnow()

    current_hash = calculate_event_hash(
        batch_id,
        event_type,
        location,
        description,
        previous_hash,
        created_at
    )

    event = TraceabilityEvent(
        batch_id=batch_id,
        event_type=event_type,
        location=location,
        description=description,
        previous_hash=previous_hash,
        current_hash=current_hash,
        created_at=created_at
    )

    db.add(event)

    status_map = {
        "HARVEST": "HARVESTED",
        "LAB_TEST": "LAB_TESTED",
        "PACKAGING": "PACKAGED",
        "DISTRIBUTION": "DISTRIBUTED",
        "RETAIL": "AT_RETAIL"
    }

    if event_type in status_map:
        batch.status = status_map[event_type]

    db.commit()
    db.refresh(event)

    return {
        "message": "Traceability event added.",
        "event_id": event.id,
        "event_type": event.event_type,
        "previous_hash": event.previous_hash,
        "current_hash": event.current_hash
    }


@router.post("/{batch_id}/lab-test")
def add_lab_test(
    batch_id: int,
    purity_status: str,
    moisture_percent: float,
    test_result: str,
    location: str,
    db: Session = Depends(get_db)
):

    batch = db.query(HoneyBatch).filter(
        HoneyBatch.id == batch_id
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    lab_test = LabTest(
        batch_id=batch_id,
        purity_status=purity_status,
        moisture_percent=moisture_percent,
        test_result=test_result,
        tested_at=datetime.utcnow()
    )

    db.add(lab_test)
    db.commit()
    db.refresh(lab_test)

    latest_event = (
        db.query(TraceabilityEvent)
        .filter(
            TraceabilityEvent.batch_id == batch_id
        )
        .order_by(TraceabilityEvent.id.desc())
        .first()
    )

    previous_hash = (
        latest_event.current_hash
        if latest_event
        else GENESIS_HASH
    )

    event_type = "LAB_TEST"

    description = (
        f"Laboratory test completed. "
        f"Purity status: {purity_status}. "
        f"Moisture: {moisture_percent}%. "
        f"Result: {test_result}"
    )

    created_at = datetime.utcnow()

    current_hash = calculate_event_hash(
        batch_id,
        event_type,
        location,
        description,
        previous_hash,
        created_at
    )

    event = TraceabilityEvent(
        batch_id=batch_id,
        event_type=event_type,
        location=location,
        description=description,
        previous_hash=previous_hash,
        current_hash=current_hash,
        created_at=created_at
    )

    db.add(event)

    batch.status = "LAB_TESTED"

    db.commit()

    return {
        "message": "Lab test recorded successfully.",
        "batch_id": batch_id,
        "purity_status": purity_status,
        "moisture_percent": moisture_percent,
        "test_result": test_result,
        "traceability_event": "LAB_TEST",
        "hash": current_hash
    }


@router.get("/{batch_id}/history")
def get_batch_history(
    batch_id: int,
    db: Session = Depends(get_db)
):

    batch = db.query(HoneyBatch).filter(
        HoneyBatch.id == batch_id
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    events = (
        db.query(TraceabilityEvent)
        .filter(
            TraceabilityEvent.batch_id == batch_id
        )
        .order_by(TraceabilityEvent.id.asc())
        .all()
    )

    verification = verify_chain(events)

    return {
        "batch_id": batch.id,
        "batch_code": batch.batch_code,
        "chain_verification": verification,
        "events": events
    }


@router.post("/{batch_id}/qr")
def create_batch_qr(
    batch_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    batch = db.query(HoneyBatch).filter(
        HoneyBatch.id == batch_id
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    result = generate_qr(
        batch.batch_code,
        request
    )

    return {
        "message": "QR code generated successfully.",
        "batch_id": batch.id,
        "batch_code": batch.batch_code,
        "verification_url": result["verification_url"],
        "qr_file": result["qr_file"],
        "qr_image_url": result["qr_image_url"]
    }


@router.post("/{batch_id}/tamper-demo")
def tamper_demo(
    batch_id: int,
    db: Session = Depends(get_db)
):

    batch = db.query(HoneyBatch).filter(
        HoneyBatch.id == batch_id
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    event = (
        db.query(TraceabilityEvent)
        .filter(
            TraceabilityEvent.batch_id == batch_id
        )
        .order_by(TraceabilityEvent.id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="No traceability events found"
        )

    simulate_tampering(event)

    db.commit()
    db.refresh(event)

    events = (
        db.query(TraceabilityEvent)
        .filter(
            TraceabilityEvent.batch_id == batch_id
        )
        .order_by(TraceabilityEvent.id)
        .all()
    )

    verification = verify_chain(events)

    return {
        "message": "Demo tampering applied.",
        "tampered_event": event.id,
        "chain_verification": verification
    }


@router.post("/{batch_id}/restore-demo")
def restore_demo(
    batch_id: int,
    db: Session = Depends(get_db)
):

    batch = db.query(HoneyBatch).filter(
        HoneyBatch.id == batch_id
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    events = (
        db.query(TraceabilityEvent)
        .filter(
            TraceabilityEvent.batch_id == batch_id
        )
        .order_by(TraceabilityEvent.id.asc())
        .all()
    )

    if not events:
        raise HTTPException(
            status_code=404,
            detail="No traceability events found"
        )

    verification = restore_demo_chain(events)

    db.commit()

    return {
        "message": "Demo chain restored successfully.",
        "batch_id": batch_id,
        "chain_verification": verification
    }