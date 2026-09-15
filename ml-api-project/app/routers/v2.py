# app/routers/v2.py
import uuid
import pandas as pd
from fastapi import APIRouter, HTTPException, Request, Depends

from app.logging_config import logger
from app.security import verify_api_key
from app.models.schemas import PredictionInput, PredictionOutputV2
from app.metrics import PREDICTIONS_COUNTER  # Import directly from metrics

router = APIRouter(prefix="/api/v2", tags=["v2"])

@router.post("/predict", response_model=PredictionOutputV2, dependencies=[Depends(verify_api_key)])
def predict_v2(payload: PredictionInput, request: Request):
    from app.main import model_pipeline  # ONLY import model_pipeline from main
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    if model_pipeline is None:
        PREDICTIONS_COUNTER.labels(version="v2", status="error").inc()
        logger.error(f"[REQ:{req_id}] [v2] Model server uninitialized.")
        raise HTTPException(status_code=500, detail="Model server uninitialized.")

    try:
        input_data = pd.DataFrame([payload.model_dump()])
        prediction_raw = float(model_pipeline.predict(input_data)[0])
        predicted_numeric = round(prediction_raw * 100000, 2)

        error_margin = round(predicted_numeric * 0.05, 2)

        PREDICTIONS_COUNTER.labels(version="v2", status="success").inc()

        return {
            "request_id": req_id,
            "predicted_price_numeric": predicted_numeric,
            "price_error_margin_usd": error_margin,
            "raw_prediction": prediction_raw,
            "model_version": "2.0.0"
        }
    except Exception as e:
        PREDICTIONS_COUNTER.labels(version="v2", status="error").inc()
        logger.exception(f"[REQ:{req_id}] [v2] Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"v2 prediction processing failed: {str(e)}")