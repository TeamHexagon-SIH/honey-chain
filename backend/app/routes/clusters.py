from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Cluster


router = APIRouter(
    prefix="/api/clusters",
    tags=["Clusters"]
)


@router.post("/")
def create_cluster(
    name: str,
    district: str,
    state: str,
    db: Session = Depends(get_db)
):
    cluster = Cluster(
        name=name,
        district=district,
        state=state
    )

    db.add(cluster)
    db.commit()
    db.refresh(cluster)

    return {
        "message": "Cluster created successfully",
        "cluster": {
            "id": cluster.id,
            "name": cluster.name,
            "district": cluster.district,
            "state": cluster.state
        }
    }


@router.get("/")
def get_clusters(db: Session = Depends(get_db)):
    clusters = db.query(Cluster).all()

    return [
        {
            "id": cluster.id,
            "name": cluster.name,
            "district": cluster.district,
            "state": cluster.state
        }
        for cluster in clusters
    ]