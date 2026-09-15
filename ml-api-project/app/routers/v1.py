# app/routers/v1.py
from typing import Dict, Any
import json
import os
import uuid
import pandas as pd
from fastapi import APIRouter, HTTPException, Request, Depends

from app.config import settings
from app.logging_config import logger
from app.security import verify_api_key
from app.metrics import PREDICTIONS_COUNTER  # Import directly from metrics
from app.models.schemas import (
    PredictionInput, 
    PredictionOutput, 
    PredictionBatchInput, 
    PredictionBatchOutput,
    ModelInfoOutput
)

router = APIRouter(prefix="/api/v1", tags=["v1"])

@router.get("/health")
def health_check(request: Request) -> Dict[str, Any]:
    from app.main import model_pipeline
    is_loaded = model_pipeline is not None
    return {
        "status": "ok" if is_loaded else "degraded",
        "model_loaded": is_loaded,
        "version": "v1"
    }

@router.get("/model-info", response_model=ModelInfoOutput)
def get_model_info():
    if not os.path.exists(settings.METADATA_PATH):
        raise HTTPException(status_code=404, detail="Model metadata file not found.")
    
    try:
        with open(settings.METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        return metadata
    except Exception as e:
        logger.exception("Failed to read model metadata")
        raise HTTPException(status_code=500, detail="Error loading model metadata.")

@router.post("/predict", response_model=PredictionOutput, dependencies=[Depends(verify_api_key)])
def predict(payload: PredictionInput, request: Request):
    from app.main import model_pipeline  # ONLY import model_pipeline from main
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    if model_pipeline is None:
        PREDICTIONS_COUNTER.labels(version="v1", status="error").inc()
        logger.error(f"[REQ:{req_id}] Prediction attempted before model initialization.")
        raise HTTPException(status_code=500, detail="Model server uninitialized.")

    try:
        input_data = pd.DataFrame([payload.model_dump()])
        prediction_raw = model_pipeline.predict(input_data)[0]
        predicted_usd = prediction_raw * 100000

        PREDICTIONS_COUNTER.labels(version="v1", status="success").inc()
        logger.info(f"[REQ:{req_id}] [v1] Single prediction success: ${predicted_usd:,.2f}")

        return {
            "request_id": req_id,
            "predicted_price_usd": f"${predicted_usd:,.2f}",
            "raw_prediction": float(prediction_raw),
            "confidence_score": None,
            "model_version": settings.API_VERSION
        }
    except Exception as e:
        PREDICTIONS_COUNTER.labels(version="v1", status="error").inc()
        logger.exception(f"[REQ:{req_id}] [v1] Single prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction processing failed: {str(e)}")

@router.post("/predict-batch", response_model=PredictionBatchOutput, dependencies=[Depends(verify_api_key)])
def predict_batch(payload: PredictionBatchInput, request: Request):
    from app.main import model_pipeline  # ONLY import model_pipeline from main
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    if model_pipeline is None:
        PREDICTIONS_COUNTER.labels(version="v1", status="error").inc(len(payload.inputs))
        logger.error(f"[REQ:{req_id}] Batch prediction attempted before model initialization.")
        raise HTTPException(status_code=500, detail="Model server uninitialized.")

    batch_size = len(payload.inputs)

    if batch_size > settings.MAX_BATCH_SIZE:
        PREDICTIONS_COUNTER.labels(version="v1", status="error").inc(batch_size)
        logger.warning(f"[REQ:{req_id}] Batch size {batch_size} exceeds maximum limit of {settings.MAX_BATCH_SIZE}")
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds maximum limit of {settings.MAX_BATCH_SIZE} items. Received {batch_size}."
        )

    try:
        batch_dicts = [item.model_dump() for item in payload.inputs]
        batch_df = pd.DataFrame(batch_dicts)
        raw_predictions = model_pipeline.predict(batch_df)

        results = []
        for raw_val in raw_predictions:
            usd_val = raw_val * 100000
            results.append({
                "request_id": req_id,
                "predicted_price_usd": f"${usd_val:,.2f}",
                "raw_prediction": float(raw_val),
                "confidence_score": None,
                "model_version": settings.API_VERSION
            })

        PREDICTIONS_COUNTER.labels(version="v1", status="success").inc(batch_size)
        logger.info(f"[REQ:{req_id}] [v1] Batch prediction success: Processed {batch_size} samples.")

        return {
            "request_id": req_id,
            "batch_size": batch_size,
            "predictions": results
        }
    except Exception as e:
        PREDICTIONS_COUNTER.labels(version="v1", status="error").inc(batch_size)
        logger.exception(f"[REQ:{req_id}] [v1] Batch prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction processing failed: {str(e)}")