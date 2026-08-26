from contextlib import asynccontextmanager
import uuid
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

from app.models.schemas import PredictionInput

# Global holder for loaded model
model_pipeline = None
MODEL_PATH = "ml/saved_model/model.joblib"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_pipeline
    print("--- Initializing Server & Loading Model ---")
    try:
        model_pipeline = joblib.load(MODEL_PATH)
        print("--- ML Model successfully loaded into RAM ---")
    except Exception as e:
        print(f"--- Warning: Could not load model: {e} ---")
    
    yield
    print("--- Shutting down application ---")

app = FastAPI(
    title="California Housing ML Service",
    description="Production-ready FastAPI service for housing valuations.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def root():
    return {
        "message": "Welcome to the California Housing Price Prediction API",
    }


@app.get("/health")
def health_check():
    # Safely checks if the model object exists in memory
    is_loaded = model_pipeline is not None
    return {
        "status": "ok" if is_loaded else "degraded",
        "model_loaded": is_loaded
    }


@app.post("/predict")
def predict(payload: PredictionInput):
    if model_pipeline is None:
        raise HTTPException(status_code=500, detail="Model server uninitialized.")

    try:
        # 1. Convert validated Pydantic object to Pandas DataFrame
        input_data = pd.DataFrame([payload.model_dump()])

        # 2. Compute inference using trained pipeline
        prediction_raw = model_pipeline.predict(input_data)[0]
        predicted_usd = prediction_raw * 100000

        # 3. Generate unique request ID for tracking
        request_id = str(uuid.uuid4())

        
        #(regression models do not return classification probability scores).
        return {
            "request_id": request_id,
            "predicted_price_usd": f"${predicted_usd:,.2f}",
            "raw_prediction": float(prediction_raw),
            "confidence_score": None  # Regression targets do not support predict_proba
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")