# app/routers/v2.py
import uuid
import pandas as pd
from fastapi import APIRouter, HTTPException, Request

from app.logging_config import logger
from app.models.schemas import PredictionInput, PredictionOutputV2

router = APIRouter(prefix="/api/v2", tags=["v2"])

@router.post("/predict", response_model=PredictionOutputV2)
def predict_v2(payload: PredictionInput, request: Request):
    from app.main import model_pipeline
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    if model_pipeline is None:
        logger.error(f"[REQ:{req_id}] [v2] Model server uninitialized.")
        raise HTTPException(status_code=500, detail="Model server uninitialized.")

    try:
        input_data = pd.DataFrame([payload.model_dump()])
        prediction_raw = float(model_pipeline.predict(input_data)[0])
        predicted_numeric = round(prediction_raw * 100000, 2)

        # Regression margin of error metric (+/- 5% of estimated house valuation)
        error_margin = round(predicted_numeric * 0.05, 2)

        return {
            "request_id": req_id,
            "predicted_price_numeric": predicted_numeric,
            "price_error_margin_usd": error_margin,
            "raw_prediction": prediction_raw,
            "model_version": "2.0.0"
        }
    except Exception as e:
        logger.exception(f"[REQ:{req_id}] [v2] Prediction failed")
        raise HTTPException(status_code=500, detail="v2 prediction processing failed.")