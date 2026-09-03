# tests/test_predict.py
def test_single_predict_success(client, valid_housing_payload):
    response = client.post("/api/v1/predict", json=valid_housing_payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_price_usd" in data
    assert "raw_prediction" in data
    assert "request_id" in data
    assert data["model_version"] == "1.0.0"

def test_predict_validation_missing_fields(client):
    invalid_payload = {
        "MedInc": 8.3252,
        "HouseAge": 41.0
        # Missing remaining 6 required features
    }
    response = client.post("/api/v1/predict", json=invalid_payload)
    assert response.status_code == 422  # Unprocessable Entity (Validation Error)

def test_predict_out_of_range_coordinates(client, valid_housing_payload):
    invalid_payload = valid_housing_payload.copy()
    invalid_payload["Latitude"] = 99.0  # Invalid latitude outside 32.0 - 42.0
    response = client.post("/api/v1/predict", json=invalid_payload)
    assert response.status_code == 422