# app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="House Price Prediction API",
    description="A minimal API serving machine learning predictions.",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "ML API is alive"}

@app.post("/predict")
def predict():
    return {"prediction": "hardcoded_result"}  # Simple hardcoded response to test POST route