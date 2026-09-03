# tests/test_batch_predict.py
from app.config import settings

def test_predict_batch_success(client, valid_housing_payload):
    batch_payload = {"inputs": [valid_housing_payload, valid_housing_payload]}
    response = client.post("/api/v1/predict-batch", json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["batch_size"] == 2
    assert len(data["predictions"]) == 2

def test_predict_batch_oversized_rejection(client, valid_housing_payload, monkeypatch):
    # Temporarily set MAX_BATCH_SIZE to 2 for testing limit enforcement
    monkeypatch.setattr(settings, "MAX_BATCH_SIZE", 2)
    
    oversized_payload = {
        "inputs": [valid_housing_payload, valid_housing_payload, valid_housing_payload]
    }
    response = client.post("/api/v1/predict-batch", json=oversized_payload)
    assert response.status_code == 400
    assert "Batch size exceeds maximum limit" in response.json()["detail"]