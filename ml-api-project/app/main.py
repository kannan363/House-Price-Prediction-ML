from contextlib import asynccontextmanager
import logging
import uuid
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.models.schemas import PredictionInput, PredictionOutput

# Set up logging so real tracebacks stay in your backend server logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml_api")

model_pipeline = None
MODEL_PATH = "ml/saved_model/model.joblib"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_pipeline
    logger.info("--- Initializing Server & Loading Model ---")
    try:
        model_pipeline = joblib.load(MODEL_PATH)
        logger.info("--- ML Model successfully loaded into RAM ---")
    except Exception as e:
        logger.error(f"--- FAILED to load model: {e} ---")
    
    yield
    logger.info("--- Shutting down application ---")

app = FastAPI(
    title="California Housing ML Service",
    description="Production-ready FastAPI service for housing valuations.",
    version="1.0.0",
    lifespan=lifespan
)


# Catches ValueErrors (like feature shape or array mismatch issues) globally
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.error(f"Captured ValueError on path {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "error_type": "ValueError",
            "message": "Invalid values provided for processing.",
            "detail": str(exc)
        }
    )

@app.get("/")
def root():
    return {
        "message": "Welcome to the California Housing Price Prediction API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    is_loaded = model_pipeline is not None
    return {
        "status": "ok" if is_loaded else "degraded",
        "model_loaded": is_loaded
    }

# --- ATTACH response_model HERE ---
@app.post("/predict", response_model=PredictionOutput)
def predict(payload: PredictionInput):
    if model_pipeline is None:
        raise HTTPException(status_code=500, detail="Model is uninitialized or failed to load.")

    try:
        input_data = pd.DataFrame([payload.model_dump()])
        prediction_raw = model_pipeline.predict(input_data)[0]
        predicted_usd = prediction_raw * 100000

        # Return dict matching PredictionOutput schema
        return {
            "request_id": str(uuid.uuid4()),
            "predicted_price_usd": f"${predicted_usd:,.2f}",
            "raw_prediction": float(prediction_raw),
            "confidence_score": None,
            "model_version": "1.0.0"
        }
    except Exception as e:
        # Log the real python traceback on your backend server
        logger.exception("Inference processing error occurred")
        
        # Return a safe, controlled 500 error to the client (no leaked stack traces)
        raise HTTPException(
            status_code=500, 
            detail="Prediction processing failed on server. Internal log generated."
        )