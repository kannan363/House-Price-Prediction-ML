# tests/test_versioning_comparison.py

def test_v1_and_v2_side_by_side_contract_isolation(client, valid_housing_payload):
    # 1. Call v1
    response_v1 = client.post("/api/v1/predict", json=valid_housing_payload)
    assert response_v1.status_code == 200
    data_v1 = response_v1.json()

    # 2. Call v2
    response_v2 = client.post("/api/v2/predict", json=valid_housing_payload)
    assert response_v2.status_code == 200
    data_v2 = response_v2.json()

    # --- ASSERT V1 CONTRACT (Untouched) ---
    assert "predicted_price_usd" in data_v1
    assert "price_error_margin_usd" not in data_v1

    # --- ASSERT V2 CONTRACT (New single regression field) ---
    assert "predicted_price_numeric" in data_v2
    assert "price_error_margin_usd" in data_v2
    assert isinstance(data_v2["price_error_margin_usd"], float)
    assert "predicted_price_usd" not in data_v2