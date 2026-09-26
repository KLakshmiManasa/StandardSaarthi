"""
SIH 26108 — Test Suite for 9 Supported Official Languages Detection & Multilingual Routing
Verifies accurate classification of Devanagari Hindi (hi), Tamil (ta), Telugu (te), Bengali (bn), Gujarati (gu),
mixed Indic-English prompts, manual selection override, and end-to-end API response.
"""

import pytest
from services.multilingual import multilingual_service, SUPPORTED_LANGUAGES
from nlp.entity_extractor import NLPEntityExtractor
from integration.pipeline import pipeline
from fastapi.testclient import TestClient
from api.routes import app

client = TestClient(app)

def test_pure_hindi_query_detection():
    """TEST 1: Verify pure Hindi query is detected as Hindi (hi)."""
    q = "मुझे बिल्डिंग के अंदर इलेक्ट्रिकल वायरिंग के लिए केबल चाहिए, जिनमें कॉपर कंडक्टर और PVC इंसुलेशन हो।"
    res = multilingual_service.process_query(q)
    
    assert res["detected_language"] == "hi"
    assert "Hindi" in res["language_name"]
    assert res["detection_details"]["method"] == "devanagari_lexical_classification"

def test_mixed_hindi_english_query_detection():
    """TEST 2: Verify mixed Hindi-English query is detected as Hindi (hi)."""
    q = "मुझे building के अंदर electrical wiring के लिए cable चाहिए, जिसमें copper conductor और PVC insulation हो।"
    res = multilingual_service.process_query(q)
    
    assert res["detected_language"] == "hi"
    assert "Hindi" in res["language_name"]

def test_manual_language_override():
    """TEST 3: Verify manual selection overrides auto-detection."""
    q = "Procurement of cables for electrical wiring"
    res = multilingual_service.process_query(q, target_lang="hi")
    
    assert res["detected_language"] == "hi"
    assert res["detection_details"]["method"] == "manual_selection"

def test_other_indic_languages_regression():
    """TEST 4: Regression check for Tamil, Telugu, Bengali, Gujarati, and English."""
    q_ta = "கேபிள் வயரிங் தேவை"
    res_ta = multilingual_service.process_query(q_ta)
    assert res_ta["detected_language"] == "ta"

    q_te = "వైరింగ్ కేబుల్ కావాలి"
    res_te = multilingual_service.process_query(q_te)
    assert res_te["detected_language"] == "te"

    q_bn = "তার ওয়্যারিং প্রয়োজন"
    res_bn = multilingual_service.process_query(q_bn)
    assert res_bn["detected_language"] == "bn"

    q_gu = "વાયરિંગ કેબલ જોઈએ"
    res_gu = multilingual_service.process_query(q_gu)
    assert res_gu["detected_language"] == "gu"

    q_en = "Need copper insulated cable for building wiring"
    res_en = multilingual_service.process_query(q_en)
    assert res_en["detected_language"] == "en"

def test_hindi_api_analyze_endpoint():
    """TEST 5: Verify /api/analyze API endpoint with Hindi query returns HTTP 200 and Hindi language details."""
    q = "इमारत के अंदर विद्युत वायरिंग के लिए मुझे कॉपर कंडक्टर और PVC इंसुलेशन वाली केबल चाहिए।"
    resp = client.post("/api/analyze", json={"description": q, "language": "auto"})
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["multilingual_info"]["detected_language"] == "hi"
    assert "Hindi" in data["multilingual_info"]["language_name"]
    assert len(data["recommendations"]) > 0
