# app/main.py
from contextlib import asynccontextmanager
import time
import uuid
import joblib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import logger
#routers
from app.routers.v1 import router as v1_router
from app.routers.v2 import router as v2_router

model_pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_pipeline
    logger.info("==================================================")
    logger.info("============== NEW SERVER SESSION ================")
    logger.info("==================================================")
    logger.info("--- Initializing Server & Loading Model ---")
    try:
        model_pipeline = joblib.load(settings.MODEL_PATH)
        logger.info(f"--- ML Model successfully loaded from {settings.MODEL_PATH} ---")
    except Exception as e:
        logger.error(f"--- FAILED to load model: {e} ---")
    
    yield
    logger.info("--- Shutting down application ---")
    logger.info("==================================================\n")

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# --- INCLUDE ROUTERS ---
app.include_router(v1_router)
app.include_router(v2_router)

# --- MIDDLEWARE: REQUEST LOGGING & TRACING ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    response = await call_next(request)
    process_time_ms = (time.time() - start_time) * 1000

    logger.info(
        f"[REQ:{request_id}] {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Duration: {process_time_ms:.2f}ms"
    )

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
        "message": f"Welcome to {settings.API_TITLE}",
        "docs": "/docs",
        "v1_health": "/api/v1/health",
        "v1_predict": "/api/v1/predict"
    }