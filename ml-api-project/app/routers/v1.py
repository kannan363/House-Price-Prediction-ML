# app/routers/v1.py
from typing import Dict, Any
import uuid
import pandas as pd
from fastapi import APIRouter, HTTPException, Request

from app.logging_config import logger
from app.models.schemas import PredictionInput, PredictionOutput

# Create APIRouter with /api/v1 prefix and tags for Swagger UI grouping
router = APIRouter(prefix="/api/v1", tags=["v1"])

@router.get("/health")
def health_check(request: Request) -> Dict[str, Any]:
    from app.main import model_pipeline  # Dynamic import to reference loaded model
    is_loaded = model_pipeline is not None
    return {
        "status": "ok" if is_loaded else "degraded",
        "model_loaded": is_loaded,
        "version": "v1"
    }

@router.post("/predict", response_model=PredictionOutput)
def predict(payload: PredictionInput, request: Request):
    from app.main import model_pipeline

    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    if model_pipeline is None:
        logger.error(f"[REQ:{req_id}] Prediction attempted before model initialization.")
        raise HTTPException(status_code=500, detail="Model server uninitialized.")

    try:
        input_data = pd.DataFrame([payload.model_dump()])
        prediction_raw = model_pipeline.predict(input_data)[0]
        predicted_usd = prediction_raw * 100000

        logger.info(f"[REQ:{req_id}] [v1] Prediction success: {prediction_raw:.4f} (${predicted_usd:,.2f})")

        return {
            "request_id": req_id,
            "predicted_price_usd": f"${predicted_usd:,.2f}",
            "raw_prediction": float(prediction_raw),
            "confidence_score": None,
            "model_version": "1.0.0"
        }
    except Exception as e:
        logger.exception(f"[REQ:{req_id}] [v1] Prediction failed during execution")
        raise HTTPException(
            status_code=500,
            detail="Prediction processing failed on server. Internal log generated."
        )

# ==============================================================================
# TASK 10 DESIGN CHALLENGE: Plan for /api/v2/predict
# ==============================================================================
# If we need a /api/v2/predict endpoint tomorrow returning an extra field 
# (e.g., predicted_price_range or price_per_sqft):
#
# 1. Pydantic Schemas (app/models/schemas.py):
#    - Create a PredictionOutputV2 class extending or inheriting from PredictionOutput.
#    - Add the new required field: 
#      predicted_price_range: Dict[str, str] = Field(..., description="Estimated range")
#    - Keep PredictionOutput untouched to ensure v1 clients experience NO breaking changes.
#
# 2. Router Module (app/routers/v2.py):
#    - Create app/routers/v2.py with APIRouter(prefix="/api/v2", tags=["v2"]).
#    - Implement /api/v2/predict using PredictionOutputV2 as the response_model.
#
# 3. Main Application Integration (app/main.py):
#    - Include both routers in app/main.py:
#      app.include_router(v1_router)
#      app.include_router(v2_router)
# ==============================================================================