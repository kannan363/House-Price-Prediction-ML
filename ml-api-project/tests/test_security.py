# tests/test_security.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

# Create a clean client without default headers for testing security boundaries
client = TestClient(app)

VALID_PAYLOAD = {
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.9841,
    "AveBedrms": 1.0238,
    "Population": 322.0,
    "AveOccup": 2.5555,
    "Latitude": 37.88,
    "Longitude": -122.23
}

# 1. Reject Missing API Key (401 Unauthorized)
def test_predict_missing_api_key():
    response = client.post("/api/v1/predict", json=VALID_PAYLOAD)
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing API Key"

# 2. Reject Invalid API Key (401 Unauthorized)
def test_predict_invalid_api_key():
    headers = {"X-API-Key": "invalid_secret_key"}
    response = client.post("/api/v1/predict", headers=headers, json=VALID_PAYLOAD)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API Key"

# 3. Allow Request with Valid API Key (200 OK)
def test_predict_valid_api_key():
    headers = {"X-API-Key": settings.API_KEY}
    response = client.post("/api/v1/predict", headers=headers, json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert "predicted_price_usd" in response.json()

# 4. Reject Extra/Unexpected Fields via extra="forbid" (422 Unprocessable Entity)
def test_predict_extra_forbidden_fields():
    headers = {"X-API-Key": settings.API_KEY}
    malicious_payload = {
        **VALID_PAYLOAD,
        "unexpected_extra_field": "unauthorized_data"
    }
    response = client.post("/api/v1/predict", headers=headers, json=malicious_payload)
    assert response.status_code == 422