"""
SIH 26108 — Test Suite for Marathi Language Detection & Multilingual Routing
Verifies accurate classification of Marathi (mr) vs Hindi (hi) for Devanagari text,
mixed Indic-English prompts, manual selection override, and end-to-end API response.
"""

import pytest
from services.multilingual import multilingual_service, SUPPORTED_LANGUAGES
from nlp.entity_extractor import NLPEntityExtractor
from integration.pipeline import pipeline
from fastapi.testclient import TestClient
from api.routes import app

client = TestClient(app)

def test_pure_marathi_query_detection():
    """TEST 1: Verify pure Marathi query is detected as Marathi (mr)."""
    q = "इमारतीच्या आतील विद्युत वायरिंगच्या कामासाठी, मला तांब्याचा वाहक (copper conductor) आणि पीव्हीसी इन्सुलेशन असलेली केबल हवी आहे."
    res = multilingual_service.process_query(q)
    
    assert res["detected_language"] == "mr"
    assert "Marathi" in res["language_name"]
    assert res["detection_details"]["method"] == "devanagari_lexical_classification"
    assert res["detection_details"]["confidence"] >= 0.80

def test_mixed_marathi_english_query_detection():
    """TEST 2: Verify mixed Marathi-English query is detected as Marathi (mr)."""
    q = "इमारतीच्या आतील electrical wiring साठी copper conductor आणि PVC insulation असलेली cable हवी आहे."
    res = multilingual_service.process_query(q)
    
    assert res["detected_language"] == "mr"
    assert "Marathi" in res["language_name"]

def test_pure_hindi_query_detection():
    """TEST 3: Verify pure Hindi query is detected as Hindi (hi)."""
    q = "मुझे बिल्डिंग के अंदर इलेक्ट्रिकल वायरिंग के लिए केबल चाहिए, जिनमें कॉपर कंडक्टर और PVC इंसुलेशन हो।"
    res = multilingual_service.process_query(q)
    
    assert res["detected_language"] == "hi"
    assert "Hindi" in res["language_name"]

def test_mixed_hindi_english_query_detection():
    """TEST 4: Verify mixed Hindi-English query is detected as Hindi (hi)."""
    q = "मुझे building के अंदर electrical wiring के लिए cable चाहिए, जिसमें copper conductor और PVC insulation हो।"
    res = multilingual_service.process_query(q)
    
    assert res["detected_language"] == "hi"
    assert "Hindi" in res["language_name"]

def test_manual_language_override():
    """TEST 5: Verify manual selection overrides auto-detection."""
    q = "Procurement of cables for electrical wiring"
    res = multilingual_service.process_query(q, target_lang="mr")
    
    assert res["detected_language"] == "mr"
    assert res["detection_details"]["method"] == "manual_selection"

def test_other_indic_languages_regression():
    """TEST 6: Regression check for Tamil, Telugu, and English."""
    q_ta = "கேபிள் வயரிங் தேவை"
    res_ta = multilingual_service.process_query(q_ta)
    assert res_ta["detected_language"] == "ta"

    q_te = "వైరింగ్ కేబుల్ కావాలి"
    res_te = multilingual_service.process_query(q_te)
    assert res_te["detected_language"] == "te"

    q_en = "Need copper insulated cable for building wiring"
    res_en = multilingual_service.process_query(q_en)
    assert res_en["detected_language"] == "en"

def test_marathi_api_analyze_endpoint():
    """TEST 7: Verify /api/analyze API endpoint with Marathi query returns HTTP 200 and Marathi language details."""
    q = "इमारतीच्या आतील विद्युत वायरिंगच्या कामासाठी, मला तांब्याचा वाहक (copper conductor) आणि पीव्हीसी इन्सुलेशन असलेली केबल हवी आहे."
    resp = client.post("/api/analyze", json={"description": q, "language": "auto"})
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["multilingual_info"]["detected_language"] == "mr"
    assert "Marathi" in data["multilingual_info"]["language_name"]
    assert len(data["recommendations"]) > 0
