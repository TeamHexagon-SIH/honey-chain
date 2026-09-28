from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Beekeeper, Cluster


router = APIRouter(
    prefix="/api/beekeepers",
    tags=["Beekeepers"]
)


@router.post("/")
def create_beekeeper(
    name: str,
    phone: str,
    village: str,
    cluster_id: int,
    db: Session = Depends(get_db)
):
    cluster = db.query(Cluster).filter(
        Cluster.id == cluster_id
    ).first()

    if not cluster:
        return {
            "error": "Cluster not found"
        }

    beekeeper = Beekeeper(
        name=name,
        phone=phone,
        village=village,
        cluster_id=cluster_id
    )

    db.add(beekeeper)
    db.commit()
    db.refresh(beekeeper)

    return {
        "message": "Beekeeper created successfully",
        "beekeeper": {
            "id": beekeeper.id,
            "name": beekeeper.name,
            "village": beekeeper.village,
            "cluster_id": beekeeper.cluster_id
        }
    }


@router.get("/")
def get_beekeepers(db: Session = Depends(get_db)):
    beekeepers = db.query(Beekeeper).all()

    return [
        {
            "id": beekeeper.id,
            "name": beekeeper.name,
            "phone": beekeeper.phone,
            "village": beekeeper.village,
            "cluster_id": beekeeper.cluster_id
        }
        for beekeeper in beekeepers
    ]