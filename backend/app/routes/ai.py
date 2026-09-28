import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import joblib

from ..database import get_db
from ..models import Hive, HealthRecord


router = APIRouter(
    prefix="/api/ai",
    tags=["AI Analytics"]
)


model = joblib.load(
    "ml/hive_health_model.pkl"
)


@router.post("/health")
def analyze_hive_health(
    hive_id: int,
    temperature: float,
    humidity: float,
    hive_weight: float,
    acoustic_level: float,
    db: Session = Depends(get_db)
):

    # -----------------------------------------
    # CHECK HIVE
    # -----------------------------------------

    hive = db.query(Hive).filter(
        Hive.id == hive_id
    ).first()

    if not hive:
        return {
            "error": "Hive not found"
        }


    # -----------------------------------------
    # AI INPUT
    # -----------------------------------------

    features = pd.DataFrame([{
    "temperature": temperature,
    "humidity": humidity,
    "hive_weight": hive_weight,
    "acoustic_level": acoustic_level
}])


    # -----------------------------------------
    # PREDICTION
    # -----------------------------------------

    prediction = model.predict(
        features
    )[0]

    probability = model.predict_proba(
        features
    )[0][1]


    # -----------------------------------------
    # INTERPRETATION
    # -----------------------------------------

    if prediction == 1:

        health_status = "ATTENTION_REQUIRED"
        disease_risk = "POSSIBLE_STRESS_RISK"

        health_score = max(
            0,
            100 - (probability * 100)
        )

    else:

        health_status = "NORMAL"
        disease_risk = "LOW"

        health_score = (
            100 - (probability * 100)
        )


    health_score = round(
        health_score,
        2
    )


    # -----------------------------------------
    # SAVE RESULT
    # -----------------------------------------

    record = HealthRecord(
        hive_id=hive_id,
        health_status=health_status,
        disease_risk=disease_risk,
        health_score=health_score
    )

    db.add(record)
    db.commit()
    db.refresh(record)


    return {
        "hive_id": hive_id,
        "health_status": health_status,
        "risk_indicator": disease_risk,
        "health_score": health_score,
        "stress_probability": round(
            probability,
            4
        ),
        "message": (
            "Prototype AI indicates possible "
            "colony stress. Further inspection "
            "is recommended."
            if prediction == 1
            else
            "Prototype AI indicates normal "
            "conditions."
        )
    }

@router.post("/yield")
def predict_honey_yield(
    hive_id: int,
    temperature: float,
    humidity: float,
    hive_weight: float,
    flowering_score: float,
    health_score: float,
    db: Session = Depends(get_db)
):

    # -----------------------------------------
    # CHECK HIVE
    # -----------------------------------------

    hive = db.query(Hive).filter(
        Hive.id == hive_id
    ).first()

    if not hive:
        return {
            "error": "Hive not found"
        }


    # -----------------------------------------
    # LOAD YIELD MODEL
    # -----------------------------------------

    yield_model = joblib.load(
        "ml/honey_yield_model.pkl"
    )


    # -----------------------------------------
    # MODEL INPUT
    # -----------------------------------------

    features = pd.DataFrame([{
    "temperature": temperature,
    "humidity": humidity,
    "hive_weight": hive_weight,
    "flowering_score": flowering_score,
    "health_score": health_score
}])


    # -----------------------------------------
    # PREDICTION
    # -----------------------------------------

    prediction = yield_model.predict(
        features
    )[0]


    prediction = round(
        max(0, prediction),
        2
    )


    return {
        "hive_id": hive_id,
        "predicted_yield_kg": prediction,
        "model_type": "Prototype Random Forest Regression",
        "message": (
            "Prototype productivity prediction "
            "generated successfully."
        )
    }