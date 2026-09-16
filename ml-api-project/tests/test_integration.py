# tests/test_integration.py
import os
import httpx

BASE_URL = os.getenv("INTEGRATION_TEST_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "default_secret_key_change_me")

HEADERS = {"X-API-Key": API_KEY}

VALID_HOUSING_PAYLOAD = {
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.9841,
    "AveBedrms": 1.0238,
    "Population": 322.0,
    "AveOccup": 2.5555,
    "Latitude": 37.88,
    "Longitude": -122.23
}

def test_health_endpoint():
    response = httpx.get(f"{BASE_URL}/api/v1/health", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True

def test_metrics_endpoint():
    response = httpx.get(f"{BASE_URL}/metrics")
    assert response.status_code == 200
    assert "ml_predictions_total" in response.text

def test_single_predict_v1():
    response = httpx.post(f"{BASE_URL}/api/v1/predict", headers=HEADERS, json=VALID_HOUSING_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_price_usd" in data
    assert "request_id" in data

def test_predict_batch_v1():
    batch_payload = {"inputs": [VALID_HOUSING_PAYLOAD, VALID_HOUSING_PAYLOAD]}
    response = httpx.post(f"{BASE_URL}/api/v1/predict-batch", headers=HEADERS, json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["batch_size"] == 2
    assert len(data["predictions"]) == 2