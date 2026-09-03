# tests/test_model_info.py
def test_model_info_success(client):
    response = client.get("/api/v1/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "model_type" in data
    assert "model_version" in data
    assert "features" in data
    assert isinstance(data["features"], list)
    assert len(data["features"]) == 8