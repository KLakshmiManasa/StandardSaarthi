"""
Unit tests for Phase 5 Recommendation Engine & REST API
"""

import pytest
from fastapi.testclient import TestClient
from phase2.api.routes import app
from phase5.recommendation_engine import Phase5RecommendationEngine

client = TestClient(app)

def test_recommendation_engine_pipeline():
    engine = Phase5RecommendationEngine()
    query = "Procurement of 1.1kV 3 core 6 sq mm PVC insulated copper flexible cable for control panel wiring."
    res = engine.recommend(query, top_k=3)
    
    assert res["query"] == query
    assert len(res["recommended_standards"]) > 0
    top1 = res["recommended_standards"][0]
    assert "is_code" in top1
    assert "explanation" in top1
    assert "evidence" in top1

def test_api_recommend_endpoint():
    payload = {
        "description": "Supply of 53 Grade Ordinary Portland Cement (OPC 53) in 50kg bags for concrete girder casting.",
        "top_k": 5,
        "mode": "graph_rag"
    }
    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommended_standards" in data
    assert len(data["recommended_standards"]) > 0
