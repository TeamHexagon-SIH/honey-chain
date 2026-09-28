from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from . import models

from .routes.clusters import router as cluster_router
from .routes.beekeepers import router as beekeeper_router
from .routes.hives import router as hive_router
from .routes.sensors import router as sensor_router
from .routes.ai import router as ai_router
from .routes.batches import router as batch_router
from .routes.verification import router as verification_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Honey Chain API",
    description="Blockchain-based honey traceability and smart beekeeping system",
    version="1.0.0"
)

from pathlib import Path

QR_DIRECTORY = Path(__file__).resolve().parents[1] / "data" / "qr"

QR_DIRECTORY.mkdir(parents=True, exist_ok=True)

app.mount(
    "/qr",
    StaticFiles(directory=str(QR_DIRECTORY)),
    name="qr"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_origin_regex=(
        r"^https?://"
        r"(10\.\d+\.\d+\.\d+|"
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|"
        r"192\.168\.\d+\.\d+)"
        r":5500$"
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(cluster_router)
app.include_router(beekeeper_router)
app.include_router(hive_router)
app.include_router(sensor_router)
app.include_router(ai_router)
app.include_router(batch_router)
app.include_router(verification_router)


@app.get("/")
def root():
    return {
        "message": "Honey Chain API is running!",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/system")
def system_status():
    return {
        "project": "Honey Chain",
        "version": "1.0.0",
        "database": "SQLite",
        "status": "operational"
    }