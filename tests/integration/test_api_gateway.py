# tests/integration/test_api_gateway.py
import pytest
from fastapi.testclient import TestClient
from src.api_gateway import APIGateway

@pytest.fixture(scope="module")
def test_client():
    config = {
        "redis": {"host": "localhost", "port": 6379, "db": 0},
        "jwt_public_key": "test_key",
        "services": {"test_service": "http://mock-backend"}
    }
    app = APIGateway(config)
    return TestClient(app)

def test_api_routing(test_client):
    response = test_client.get("/test_route")
    assert response.status_code == 200

def test_rate_limiting(test_client):
    for _ in range(11):
        response = test_client.get("/limited_route")
    assert response.status_code == 429

def test_jwt_authentication(test_client):
    response = test_client.get("/secure_route", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
