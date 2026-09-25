"""
Phase 11 Product Transformation Test Suite for SIH 26108 / Product Engine.
Verifies end-to-end product features: Mode A, Mode B, Mode C (PDF/DOCX), Multilingual processing,
Standards Catalog, Standard Lifecycle, Categorized Relationships, QCO Regulatory Portal,
PDF Report Generation, History Store, and Admin Metrics.
"""

import os
import pytest
from fastapi.testclient import TestClient

from api.routes import app
from services.tender_parser import tender_parser
from services.multilingual import multilingual_service
from services.standards_service import standards_service
from services.history_store import history_store
from services.report_generator import report_generator

client = TestClient(app)

def test_01_mode_a_product_description():
    """Test Mode A: Natural-language free-text procurement recommendation."""
    resp = client.post("/api/analyze", json={
        "description": "Procurement of 1.5 sq mm single core PVC insulated copper electrical cables suitable for internal building wiring.",
        "language": "en"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["recommendations"]) > 0
    top_code = data["recommendations"][0]["is_code"]
    assert "IS 694" in top_code or "694" in top_code

def test_02_mode_b_technical_specification():
    """Test Mode B: Structured technical specification form analysis."""
    resp = client.post("/api/analyze/specification", json={
        "product_name": "Ready Mixed Concrete",
        "product_category": "Civil",
        "grade": "M30",
        "application": "Structural concrete works"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["recommendations"]) > 0
    # IS 456 or IS 4926 are both concrete recommendations
    rec_codes = [r["is_code"] for r in data["recommendations"]]
    assert any("456" in code or "4926" in code for code in rec_codes)

def test_03_mode_c_tender_document_parsing():
    """Test Mode C: Text requirement extraction from document file."""
    sample_text = """
    TENDER SPECIFICATION NO: ELECT/2026/01
    Item 1: Supply of 1.5 sq mm PVC insulated copper electrical cables for building wiring.
    Item 2: Supply of 11kV/415V 100 kVA outdoor distribution transformers.
    """
    file_bytes = sample_text.encode('utf-8')
    res = tender_parser.parse_tender_document(file_bytes, "tender_sample.txt")
    assert res["status"] == "success"
    assert res["requirement_count"] >= 2
    req_texts = [r["text"].lower() for r in res["extracted_requirements"]]
    assert any("cables" in t or "pvc" in t for t in req_texts)

def test_04_multilingual_processing():
    """Test Multilingual normalization for Hindi query."""
    hindi_text = "बिजली के तारों के लिए पीवीसी इंसुलेटेड तांबे के केबल की खरीद"
    norm_res = multilingual_service.process_query(hindi_text, target_lang="hi")
    assert norm_res["original_text"] == hindi_text
    assert len(norm_res["normalized_english"]) > 0

    # API test
    resp = client.post("/api/analyze", json={
        "description": hindi_text,
        "language": "hi"
    })
    assert resp.status_code in [200, 400, 422]

def test_05_standards_catalog_search():
    """Test standards catalog listing and filtering."""
    resp = client.get("/api/standards?q=cable")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    assert any("IS 694" in i["is_code"] for i in items)

def test_06_standard_details_and_lifecycle():
    """Test single standard detail lookup and lifecycle metadata."""
    resp = client.get("/api/standards/IS%20694")
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["is_code"] == "IS 694"
    assert detail["status"] == "ACTIVE"
    assert "lifecycle" in detail
    assert detail["lifecycle"]["is_latest_version"] is True

def test_07_categorized_relationships():
    """Test categorized graph relationships retrieval."""
    resp = client.get("/api/standards/IS%20694/relationships")
    assert resp.status_code == 200
    cats = resp.json()
    assert "normative_references" in cats
    assert "test_methods" in cats
    assert "safety_standards" in cats

def test_08_qco_regulatory_portal():
    """Test QCO & BIS certification scheme finder."""
    resp = client.get("/api/regulatory")
    assert resp.status_code == 200
    qco_records = resp.json()
    assert len(qco_records) > 0
    assert any(q["qco_applicability"] == "MANDATORY" for q in qco_records)

def test_09_pdf_report_generation():
    """Test PDF report generation stream."""
    resp = client.post("/api/reports/generate", json={
        "query": "Procurement of 1.5 sq mm PVC copper cable",
        "entities": {"product": "Cable", "category": "Electrical", "materials": ["Copper", "PVC"]},
        "recommendations": [
            {
                "is_code": "IS 694",
                "title": "PVC Insulated Cables for Working Voltages Up to 1100V",
                "relevance_score": 0.964,
                "scope": "Covers PVC insulated cables",
                "qco_compliance": {"qco_mandatory": True, "qco_name": "Electrical Wires QCO"}
            }
        ]
    })
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 1000

def test_10_history_and_saved_projects():
    """Test history store saving and retrieval."""
    entry = history_store.add_entry(
        query="Test cable query",
        mode="product_description",
        result_summary={"status": "success", "recommendations": [{"is_code": "IS 694", "title": "PVC Cable"}]}
    )
    assert entry["id"].startswith("ANALYSIS_")

    history_list = client.get("/api/history").json()
    assert len(history_list) > 0

def test_11_admin_metrics():
    """Test Admin system diagnostics endpoint."""
    resp = client.get("/api/admin/metrics")
    assert resp.status_code == 200
    metrics = resp.json()
    assert metrics["system_status"] == "Healthy"
    assert metrics["dataset_statistics"]["total_verified_standards"] >= 100
