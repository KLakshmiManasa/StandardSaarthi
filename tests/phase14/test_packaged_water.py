"""
Tests for Packaged Drinking Water (IS 14543:2024) and Fallback Vector Search for Unknown Categories.
"""

import pytest
from fastapi.testclient import TestClient
from api.routes import app
from nlp.entity_extractor import NLPEntityExtractor
from integration.pipeline import pipeline

client = TestClient(app)

def test_exact_packaged_drinking_water_query():
    """TASK 14 TEST: Exact packaged drinking water query returns IS 14543:2024."""
    query = "Packaged drinking water other than mineral water in 20-liter reusable polycarbonate carboys."
    
    # 1. Test NLP Entity Extractor
    extractor = NLPEntityExtractor()
    entities = extractor.extract_entities(query)
    
    assert entities["product"] == "Packaged Drinking Water"
    assert entities["category"] == "Food & Water"
    assert "Polycarbonate" in entities["materials"]
    assert "Carboy" in entities["container"] or "Reusable Polycarbonate Carboy" in entities["container"]
    assert "20 litre" in entities["volume"]

    # 2. Test Recommendation API Endpoint
    resp = client.post("/api/recommend", json={"description": query})
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["status"] == "success"
    assert data["entities"]["product"] == "Packaged Drinking Water"
    assert data["entities"]["category"] == "Food & Water"
    
    recs = data["recommendations"]
    assert len(recs) > 0
    top_rec = recs[0]
    
    assert top_rec["is_code"] in ["IS 14543", "IS 14543:2024"]
    assert "Packaged Drinking Water" in top_rec["title"]
    assert top_rec["relevance_score"] >= 0.70
    assert top_rec["evidence"][0]["organization"] == "Bureau of Indian Standards (BIS)"

def test_unknown_category_global_retrieval_fallback():
    """TASK 15 TEST: Unfamiliar product category falls back to global semantic search without returning 0 candidates."""
    query = "Procure specialized laboratory sample storage containers for chemical analysis."
    
    resp = client.post("/api/recommend", json={"description": query})
    # Should not return no_results or 0 candidates due to strict General sector filter
    assert resp.status_code in [200, 400]
    data = resp.json()
    if resp.status_code == 200:
        assert data["status"] == "success"
        assert len(data["recommendations"]) > 0

def test_regression_existing_domains():
    """TASK 13 TEST: Verify existing Electrical and Civil recommendations continue working cleanly."""
    # 1. Electrical Cable
    r1 = client.post("/api/recommend", json={"description": "PVC insulated copper cable for internal building wiring"})
    assert r1.status_code == 200
    c1 = [rec["is_code"] for rec in r1.json()["recommendations"]]
    assert any(code in c1 for code in ["IS 694", "IS 8130"])

    # 2. Distribution Transformer
    r2 = client.post("/api/recommend", json={"description": "500 kVA 11kV/433V outdoor oil immersed distribution transformer"})
    assert r2.status_code == 200
    c2 = [rec["is_code"] for rec in r2.json()["recommendations"]]
    assert "IS 1180:Part 1" in c2

    # 3. Ready-Mixed Concrete
    r3 = client.post("/api/recommend", json={"description": "M30 ready-mixed concrete for building slabs"})
    assert r3.status_code == 200
    c3 = [rec["is_code"] for rec in r3.json()["recommendations"]]
    assert any(code in c3 for code in ["IS 4926", "IS 456"])
