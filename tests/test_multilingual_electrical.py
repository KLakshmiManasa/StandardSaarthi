"""
Multilingual Requirement Analysis & Electrical Cable Test Suite for SIH 26108.
Verifies that English, Hindi, Tamil, and Telugu electrical cable queries
all extract the normalized electrical requirement profile and recommend IS 694.
"""

import pytest
from fastapi.testclient import TestClient
from api.routes import app
from services.multilingual import multilingual_service
from nlp.entity_extractor import NLPEntityExtractor

client = TestClient(app)

QUERIES = [
    ("English", "I need cables for electrical wiring inside a building, with copper conductors and PVC insulation."),
    ("Hindi", "मुझे बिल्डिंग के अंदर इलेक्ट्रिकल वायरिंग के लिए केबल चाहिए, जिनमें कॉपर कंडक्टर और PVC इंसुलेशन हो।"),
    ("Tamil", "கட்டிடத்தின் உள்ளே மின்சார வயரிங் செய்ய காப்பர் கண்டக்டர் மற்றும் PVC இன்சுலேஷன் கொண்ட கேபிள்கள் வேண்டும்."),
    ("Telugu", "భవనం లోపల ఎలక్ట్రికల్ వైరింగ్ కోసం కాపర్ కండక్టర్ మరియు PVC ఇన్సులేషన్ ఉన్న కేబుల్స్ కావాలి.")
]

def test_multilingual_entity_extraction_normalization():
    """Verify that entity extraction normalizes Indic terms to Electrical category and Copper/PVC materials."""
    extractor = NLPEntityExtractor()
    for lang, text in QUERIES:
        entities = extractor.extract_entities(text)
        assert entities["category"] == "Electrical", f"Language {lang} failed category classification: {entities['category']}"
        mats = [m.lower() for m in entities["materials"]]
        assert "copper" in mats, f"Language {lang} missed Copper material: {entities['materials']}"
        assert "pvc" in mats, f"Language {lang} missed PVC material: {entities['materials']}"

def test_multilingual_translation_preservation():
    """Verify that multilingual service preserves critical technical entities in normalized English."""
    for lang, text in QUERIES:
        res = multilingual_service.process_query(text)
        assert res["normalized_english"], f"Empty translation for {lang}"
        norm_lower = res["normalized_english"].lower()
        assert "copper" in norm_lower or "conductor" in norm_lower, f"Missing copper in {lang} translation: {res['normalized_english']}"
        assert "pvc" in norm_lower or "insulat" in norm_lower, f"Missing PVC/insulation in {lang} translation: {res['normalized_english']}"

@pytest.mark.parametrize("lang,query", QUERIES)
def test_api_analyze_multilingual_electrical_cables(lang, query):
    """Verify that API /api/analyze returns IS 694 for English, Hindi, Tamil, and Telugu cable queries."""
    response = client.post("/api/analyze", json={
        "description": query,
        "language": "auto"
    })
    assert response.status_code == 200, f"API failed for {lang}: {response.text}"
    data = response.json()

    assert data["status"] == "success", f"Status not success for {lang}: {data}"
    assert data["entities"]["category"] == "Electrical", f"Category was {data['entities']['category']} for {lang}, expected Electrical"
    
    recs = data.get("recommendations", [])
    assert len(recs) > 0, f"No recommendations returned for {lang}"

    top_codes = [r["is_code"] for r in recs[:3]]
    assert any("694" in code for code in top_codes), f"IS 694 not found in top recommendations for {lang}. Returned: {top_codes}"
