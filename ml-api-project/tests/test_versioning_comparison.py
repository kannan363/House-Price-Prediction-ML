from app.config import settings

def test_v1_and_v2_side_by_side_contract_isolation(client, valid_housing_payload):
    headers = {"X-API-Key": settings.API_KEY}

    # 1. Call v1
    response_v1 = client.post("/api/v1/predict", headers=headers, json=valid_housing_payload)
    assert response_v1.status_code == 200
    data_v1 = response_v1.json()

    # 2. Call v2
    response_v2 = client.post("/api/v2/predict", headers=headers, json=valid_housing_payload)
    assert response_v2.status_code == 200
    data_v2 = response_v2.json()

    # --- ASSERT V1 CONTRACT ---
    assert "predicted_price_usd" in data_v1
    assert "price_error_margin_usd" not in data_v1

    # --- ASSERT V2 CONTRACT ---
    assert "predicted_price_numeric" in data_v2
    assert "price_error_margin_usd" in data_v2
    assert isinstance(data_v2["price_error_margin_usd"], float)
    assert "predicted_price_usd" not in data_v2