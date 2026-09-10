# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

@pytest.fixture(scope="module")
def auth_headers():
    """Provides valid API key authentication headers."""
    return {"X-API-Key": settings.API_KEY}

@pytest.fixture(scope="module")
def client(auth_headers):
    """Provides a reusable FastAPI TestClient configured with default auth headers."""
    test_client = TestClient(app)
    test_client.headers.update(auth_headers)
    with test_client:
        yield test_client

@pytest.fixture
def valid_housing_payload():
    """Fixture providing a standard valid California housing sample."""
    return {
        "MedInc": 8.3252,
        "HouseAge": 41.0,
        "AveRooms": 6.9841,
        "AveBedrms": 1.0238,
        "Population": 322.0,
        "AveOccup": 2.5555,
        "Latitude": 37.88,
        "Longitude": -122.23
    }