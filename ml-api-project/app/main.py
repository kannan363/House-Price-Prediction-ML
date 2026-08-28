from contextlib import asynccontextmanager
import time
import uuid
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.logging_config import logger
from app.models.schemas import PredictionInput, PredictionOutput

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
    description="Production-ready FastAPI service for housing valuations with structured logging.",
    version="1.0.0",
    lifespan=lifespan
)

# MIDDLEWARE: REQUEST LOGGING & UUID TRACING ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # 1. Generate unique request_id and store in request state
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    
    # Process the request
    response = await call_next(request)

    # 2. Calculate execution duration in milliseconds
    process_time_ms = (time.time() - start_time) * 1000

    # 3. Log request details
    logger.info(
        f"[REQ:{request_id}] {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Duration: {process_time_ms:.2f}ms"
    )

    # Attach request_id to HTTP response headers for client tracing
    response.headers["X-Request-ID"] = request_id
    return response

# --- CUSTOM EXCEPTION HANDLER ---
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    req_id = getattr(request.state, "request_id", "N/A")
    logger.error(f"[REQ:{req_id}] ValueError on {request.url.path}: {str(exc)}")
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

# --- PREDICT ENDPOINT WITH REQUEST STATE TRACING ---
@app.post("/predict", response_model=PredictionOutput)
def predict(payload: PredictionInput, request: Request):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    if model_pipeline is None:
        logger.error(f"[REQ:{req_id}] Prediction attempted before model initialization.")
        raise HTTPException(status_code=500, detail="Model server uninitialized.")

    try:
        input_data = pd.DataFrame([payload.model_dump()])
        prediction_raw = model_pipeline.predict(input_data)[0]
        predicted_usd = prediction_raw * 100000

        logger.info(f"[REQ:{req_id}] Successful prediction: {prediction_raw:.4f} (${predicted_usd:,.2f})")

        return {
            "request_id": req_id,
            "predicted_price_usd": f"${predicted_usd:,.2f}",
            "raw_prediction": float(prediction_raw),
            "confidence_score": None,
            "model_version": "1.0.0"
        }
    except Exception as e:
        logger.exception(f"[REQ:{req_id}] Prediction failed during execution")
        raise HTTPException(
            status_code=500,
            detail="Prediction processing failed on server. Internal log generated."
        )