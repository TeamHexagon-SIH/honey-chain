from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Hive, Beekeeper


router = APIRouter(
    prefix="/api/hives",
    tags=["Hives"]
)


@router.post("/")
def create_hive(
    hive_code: str,
    location: str,
    beekeeper_id: int,
    db: Session = Depends(get_db)
):
    beekeeper = db.query(Beekeeper).filter(
        Beekeeper.id == beekeeper_id
    ).first()

    if not beekeeper:
        return {
            "error": "Beekeeper not found"
        }

    existing_hive = db.query(Hive).filter(
        Hive.hive_code == hive_code
    ).first()

    if existing_hive:
        return {
            "error": "Hive code already exists"
        }

    hive = Hive(
        hive_code=hive_code,
        location=location,
        beekeeper_id=beekeeper_id
    )

    db.add(hive)
    db.commit()
    db.refresh(hive)

    return {
        "message": "Hive created successfully",
        "hive": {
            "id": hive.id,
            "hive_code": hive.hive_code,
            "location": hive.location,
            "beekeeper_id": hive.beekeeper_id
        }
    }


@router.get("/")
def get_hives(db: Session = Depends(get_db)):
    hives = db.query(Hive).all()

    return [
        {
            "id": hive.id,
            "hive_code": hive.hive_code,
            "location": hive.location,
            "beekeeper_id": hive.beekeeper_id
        }
        for hive in hives
    ]


@router.get("/{hive_id}")
def get_hive(
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

    return {
        "id": hive.id,
        "hive_code": hive.hive_code,
        "location": hive.location,
        "beekeeper_id": hive.beekeeper_id
    }