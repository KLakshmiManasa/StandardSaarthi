"""
Phase 12 Integration & Routing Test Suite for SIH 26108 / Product Engine.
Verifies SPA routes, frontend static file serving, REST API endpoints,
and end-to-end user workflows for Mode A, Mode B, Mode C, Catalog, QCO, Reports, and History.
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

def test_01_spa_root_and_static_files():
    """Test SPA Root and static asset serving."""
    root_resp = client.get("/")
    assert root_resp.status_code == 200
    assert "<!DOCTYPE html>" in root_resp.text
    assert "StandardSaarthi" in root_resp.text

    css_resp = client.get("/styles.css")
    assert css_resp.status_code == 200

    js_resp = client.get("/app.js")
    assert js_resp.status_code == 200

def test_02_mode_a_product_description_flow():
    """Test Mode A free-text procurement description endpoint."""
    resp = client.post("/api/analyze", json={
        "description": "Procurement of 1.5 sq mm PVC insulated copper electrical cables for house wiring.",
        "language": "en"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["recommendations"]) > 0
    top_code = data["recommendations"][0]["is_code"]
    assert "IS 694" in top_code or "694" in top_code
    assert "entities" in data

def test_03_mode_b_technical_spec_flow():
    """Test Mode B structured technical specification form analysis."""
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
    rec_codes = [r["is_code"] for r in data["recommendations"]]
    assert any("456" in code or "4926" in code for code in rec_codes)

def test_04_mode_c_document_upload_flow():
    """Test Mode C tender document text extraction."""
    sample_text = """
    TENDER SPECIFICATION NO: ELECT/2026/01
    Item 1: Supply of 1.5 sq mm PVC insulated copper electrical cables for building wiring.
    Item 2: Supply of 11kV/415V 100 kVA outdoor distribution transformers.
    """
    file_bytes = sample_text.encode('utf-8')
    res = tender_parser.parse_tender_document(file_bytes, "tender_sample.txt")
    assert res["status"] == "success"
    assert res["requirement_count"] >= 2

def test_05_standards_catalog_search():
    """Test standards catalog listing and filtering."""
    resp = client.get("/api/standards?q=cable")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    assert any("IS 694" in i["is_code"] for i in items)

def test_06_standard_details_route():
    """Test standard details endpoint."""
    resp = client.get("/api/standards/IS%20694")
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["is_code"] == "IS 694"
    assert detail["status"] == "ACTIVE"
    assert "lifecycle" in detail

def test_07_categorized_relationships_route():
    """Test categorized graph relationships endpoint."""
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

def test_09_pdf_report_generation_stream():
    """Test PDF report generation binary stream."""
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

def test_10_history_and_admin_diagnostics():
    """Test History store and Admin diagnostics endpoints."""
    hist_resp = client.get("/api/history")
    assert hist_resp.status_code == 200

    admin_resp = client.get("/api/admin/metrics")
    assert admin_resp.status_code == 200
    metrics = admin_resp.json()
    assert metrics["system_status"] == "Healthy"
    assert metrics["dataset_statistics"]["total_verified_standards"] >= 100
