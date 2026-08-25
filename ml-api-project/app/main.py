from contextlib import asynccontextmanager
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

# Import the new Pydantic schema
from app.models.schemas import PredictionInput

model_pipeline = None
MODEL_PATH = "ml/saved_model/model.joblib"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_pipeline
    print(f"--- Loading ML Model from {MODEL_PATH} ---")
    try:
        model_pipeline = joblib.load(MODEL_PATH)
        print("--- Model successfully loaded into memory! ---")
    except Exception as e:
        print(f"--- FAILED to load model: {e} ---")
    
    yield
    print("--- Shutting down application... ---")

app = FastAPI(
    title="House Price Prediction API",
    description="FastAPI application serving real California housing ML predictions.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def root():
    return {"message": "ML API is alive and model is loaded"}

# Change parameter from (payload: dict) to (payload: PredictionInput)
@app.post("/predict")
def predict(payload: PredictionInput):
    if model_pipeline is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")

    try:
        # Convert Pydantic object to dictionary, then into DataFrame
        input_df = pd.DataFrame([payload.model_dump()])

        
        prediction_raw = model_pipeline.predict(input_df)[0]
        actual_usd = prediction_raw * 100000

        return {
            "predicted_price_usd": f"${actual_usd:,.2f}",
            "raw_prediction_unit": float(prediction_raw)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")