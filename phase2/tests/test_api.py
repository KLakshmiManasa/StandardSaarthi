"""
Unit tests for FastAPI Routes.
"""

from fastapi.testclient import TestClient
from phase2.api.routes import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["dataset_standards_count"] > 0

def test_search_api_hybrid():
    payload = {
        "query": "Supply of PVC insulated copper electrical cables for internal wiring",
        "method": "hybrid",
        "top_k": 5,
        "alpha": 0.5
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["candidates"]) == 5
    assert data["candidates"][0]["is_code"] == "IS 694"

def test_search_api_empty_query():
    payload = {
        "query": "   ",
        "method": "hybrid",
        "top_k": 5
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 400

def test_search_api_invalid_method():
    payload = {
        "query": "copper wire",
        "method": "invalid_method",
        "top_k": 5
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 400
