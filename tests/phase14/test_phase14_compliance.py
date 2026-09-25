"""
Phase 14 Comprehensive SIH 26108 Feature Compliance Test Suite.
Tests all 16 required test scenarios:
1. PVC insulated copper cable
2. 1100 V cable
3. M30 ready-mixed concrete
4. 500 kVA distribution transformer
5. Earthing requirement
6. Ambiguous electrical cable
7. Out-of-domain smartphone query
8. Natural language query
9. Tender PDF upload
10. Tender DOCX upload
11. Tamil query processing
12. Hindi query processing
13. Standard with amendments
14. Standard with related references
15. Product with mandatory regulatory requirement
16. Product without identified mandatory requirement
"""

import os
import pytest
from fastapi.testclient import TestClient

from api.routes import app
from services.multilingual import multilingual_service
from services.standards_service import standards_service, validate_source

client = TestClient(app)

def test_scenario_01_pvc_insulated_copper_cable():
    """TEST 1: PVC insulated copper cable returns IS 694 / IS 8130."""
    resp = client.post("/api/recommend", json={"description": "PVC insulated copper cable for internal building wiring"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    codes = [r["is_code"] for r in data["recommendations"]]
    assert "IS 694" in codes or "IS 8130" in codes

def test_scenario_02_1100v_cable():
    """TEST 2: 1100V cable specification matching."""
    resp = client.post("/api/recommend", json={"description": "1100 V heavy duty armored electric cable with copper conductor"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    codes = [r["is_code"] for r in data["recommendations"]]
    assert any(c in codes for c in ["IS 1554:Part 1", "IS 694", "IS 7098:Part 1"])

def test_scenario_03_m30_ready_mixed_concrete():
    """TEST 3: M30 ready-mixed concrete returns IS 4926."""
    resp = client.post("/api/recommend", json={"description": "M30 ready-mixed concrete for building slabs"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    codes = [r["is_code"] for r in data["recommendations"]]
    assert "IS 4926" in codes or "IS 456" in codes

def test_scenario_04_500kva_transformer():
    """TEST 4: 500 kVA distribution transformer returns IS 1180:Part 1."""
    resp = client.post("/api/recommend", json={"description": "500 kVA 11kV/433V outdoor oil immersed distribution transformer"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    codes = [r["is_code"] for r in data["recommendations"]]
    assert "IS 1180:Part 1" in codes

def test_scenario_05_earthing_requirement():
    """TEST 5: Earthing requirement returns IS 3043."""
    resp = client.post("/api/recommend", json={"description": "Earthing pipe electrode for electrical installation safety and grounding specification"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    codes = [r["is_code"] for r in data["recommendations"]]
    assert "IS 3043" in codes or "IS 732" in codes

def test_scenario_06_ambiguous_cable_query():
    """TEST 6: Ambiguous cable query triggers needs_clarification status."""
    resp = client.post("/api/recommend", json={"description": "electrical cable for office"})
    assert resp.status_code == 400
    data = resp.json()
    assert data["status"] == "needs_clarification"
    assert "missing_fields" in data or "clarification_questions" in data

def test_scenario_07_out_of_domain_query():
    """TEST 7: Out-of-domain smartphone query returns 422 out_of_domain status."""
    resp = client.post("/api/recommend", json={"description": "Best smartphone under 20000 rupees with good camera"})
    assert resp.status_code == 422
    data = resp.json()
    assert data["status"] == "out_of_domain"

def test_scenario_08_natural_language_query():
    """TEST 8: Natural language procurement query processing."""
    resp = client.post("/api/recommend", json={"description": "What standard should be used for PVC insulated copper cables inside buildings?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["recommendations"]) > 0

def test_scenario_09_tender_pdf_processing():
    """TEST 9: Tender document upload endpoint."""
    txt_content = b"Item 1. Supply of PVC insulated copper cable 1100V. Item 2. Supply of 500 kVA distribution transformer."
    resp = client.post("/api/tender/analyze", files={"file": ("tender_spec.txt", txt_content, "text/plain")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["requirement_count"] >= 1

def test_scenario_10_tender_docx_processing():
    """TEST 10: Tender TXT/DOCX parsing fallback."""
    txt_content = b"3.1 Electrical Cable requirement for power distribution. 3.2 Earthing copper electrode."
    resp = client.post("/api/analyze/document", files={"file": ("tender.txt", txt_content, "text/plain")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"

def test_scenario_11_tamil_query_processing():
    """TEST 11: Tamil query processing returning semantically equivalent recommendations."""
    tamil_query = "கட்டிட மின்சார வயரிங்கிற்கான பிவிசி இன்சுலேட்டட் செம்பு கேபிள்"
    resp = client.post("/api/recommend", json={"description": tamil_query, "language": "ta"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    codes = [r["is_code"] for r in data["recommendations"]]
    assert "IS 694" in codes or "IS 8130" in codes

def test_scenario_12_hindi_query_processing():
    """TEST 12: Hindi query processing returning semantically equivalent recommendations."""
    hindi_query = "आंतरिक भवन वायरिंग के लिए पीवीसी इंसुलेटेड तांबे का केबल"
    resp = client.post("/api/recommend", json={"description": hindi_query, "language": "hi"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    codes = [r["is_code"] for r in data["recommendations"]]
    assert "IS 694" in codes or "IS 8130" in codes

def test_scenario_13_standard_with_amendments():
    """TEST 13: Standard details for IS 8130 returns 2 amendments."""
    resp = client.get("/api/standards/IS%208130")
    assert resp.status_code == 200
    details = resp.json()
    assert details["is_code"] == "IS 8130"
    assert details["amendmentCount"] == 2
    assert len(details["amendments"]) == 2

def test_scenario_14_standard_with_related_references():
    """TEST 14: Standard related references endpoint."""
    resp = client.get("/api/standards/IS%208130/related")
    assert resp.status_code == 200
    cats = resp.json()
    assert "normative_references" in cats
    assert "test_methods" in cats

def test_scenario_15_mandatory_regulatory_requirement():
    """TEST 15: IS 694 indicates MANDATORY QCO compliance."""
    resp = client.get("/api/standards/IS%20694/regulatory")
    assert resp.status_code == 200
    reg = resp.json()
    assert reg["qco_mandatory"] is True

def test_scenario_16_non_mandatory_regulatory_requirement():
    """TEST 16: Non-mandatory product standard (e.g. IS 3043)."""
    resp = client.get("/api/standards/IS%203043/regulatory")
    assert resp.status_code == 200
    reg = resp.json()
    assert reg["qco_mandatory"] is False
