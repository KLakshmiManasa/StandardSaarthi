"""
SIH 26108 — Phase 7 End-to-End Test Suite
Verifies full end-to-end communication from REST API input to final structured recommendation response.
"""

import pytest
@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from api.routes import app
    return TestClient(app)

def test_e2e_procurement_recommendation(client):
    payload = {
        "description": "PVC insulated copper electrical cables suitable for internal wiring.",
        "top_k": 5,
        "mode": "graph_rag"
    }
    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["query"] == payload["description"]
    assert "entities" in data
    assert len(data["recommendations"]) > 0

    rec = data["recommendations"][0]
    assert rec["rank"] == 1
    assert "is_code" in rec
    assert "relevance_score" in rec
    assert len(rec["reasons"]) > 0
    assert "qco" in rec
    assert len(rec["evidence"]) > 0
    assert "processing" in data

def test_e2e_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["services"]["api"] is True
    assert "embedding_model" in data
    assert data["embedding_model"]["loaded"] is True
    assert "name" in data["embedding_model"]

def test_e2e_relationships_endpoint(client):
    response = client.get("/api/standards/IS 694:2010/relationships")
    assert response.status_code == 200
    data = response.json()
    assert "normative_references" in data
    assert "test_methods" in data
    assert "safety_standards" in data
    assert "installation_standards" in data
    assert "terminology_standards" in data
    assert "related_product_standards" in data


