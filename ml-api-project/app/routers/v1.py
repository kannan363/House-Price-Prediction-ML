from typing import Dict, Any
import json
import os
import uuid
import pandas as pd
from fastapi import APIRouter, HTTPException, Request

from app.logging_config import logger
from app.models.schemas import (
    PredictionInput, 
    PredictionOutput, 
    PredictionBatchInput, 
    PredictionBatchOutput,
    ModelInfoOutput
)

router = APIRouter(prefix="/api/v1", tags=["v1"])
METADATA_PATH = "ml/saved_model/metadata.json"

@router.get("/health")
def health_check(request: Request) -> Dict[str, Any]:
    from app.main import model_pipeline
    is_loaded = model_pipeline is not None
    return {
        "status": "ok" if is_loaded else "degraded",
        "model_loaded": is_loaded,
        "version": "v1"
    }

# ---MODEL INFO ENDPOINT ---
@router.get("/model-info", response_model=ModelInfoOutput)
def get_model_info():
    if not os.path.exists(METADATA_PATH):
        raise HTTPException(status_code=404, detail="Model metadata file not found.")
    
    try:
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        return metadata
    except Exception as e:
        logger.exception("Failed to read model metadata")
        raise HTTPException(status_code=500, detail="Error loading model metadata.")

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

        logger.info(f"[REQ:{req_id}] [v1] Single prediction success: ${predicted_usd:,.2f}")

        return {
            "request_id": req_id,
            "predicted_price_usd": f"${predicted_usd:,.2f}",
            "raw_prediction": float(prediction_raw),
            "confidence_score": None,
            "model_version": "1.0.0"
        }
    except Exception as e:
        logger.exception(f"[REQ:{req_id}] [v1] Single prediction failed")
        raise HTTPException(status_code=500, detail="Prediction processing failed.")

# VECTORIZED BATCH PREDICTION ENDPOINT 
@router.post("/predict-batch", response_model=PredictionBatchOutput)
def predict_batch(payload: PredictionBatchInput, request: Request):
    from app.main import model_pipeline
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    if model_pipeline is None:
        logger.error(f"[REQ:{req_id}] Batch prediction attempted before model initialization.")
        raise HTTPException(status_code=500, detail="Model server uninitialized.")

    batch_size = len(payload.inputs)

    try:
        # Convert list of Pydantic objects into a single multi-row DataFrame for efficient execution
        batch_dicts = [item.model_dump() for item in payload.inputs]
        batch_df = pd.DataFrame(batch_dicts)

        # Call model.predict() ONCE on the entire DataFrame (Vectorized scoring)
        raw_predictions = model_pipeline.predict(batch_df)

        results = []
        for raw_val in raw_predictions:
            usd_val = raw_val * 100000
            results.append({
                "request_id": req_id,
                "predicted_price_usd": f"${usd_val:,.2f}",
                "raw_prediction": float(raw_val),
                "confidence_score": None,
                "model_version": "1.0.0"
            })

        logger.info(f"[REQ:{req_id}] [v1] Batch prediction success: Processed {batch_size} samples.")

        return {
            "request_id": req_id,
            "batch_size": batch_size,
            "predictions": results
        }
    except Exception as e:
        logger.exception(f"[REQ:{req_id}] [v1] Batch prediction failed")
        raise HTTPException(status_code=500, detail="Batch prediction processing failed.")