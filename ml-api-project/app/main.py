# app/main.py
from fastapi import FastAPI

app = FastAPI(title="House Price ML API")

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "House Price ML API"}