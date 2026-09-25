"""
Unit tests for Phase 5 NLP Entity Extractor
"""

import pytest
from nlp.entity_extractor import NLPEntityExtractor

def test_nlp_entity_extraction_electrical():
    extractor = NLPEntityExtractor()
    text = "Procurement of 1.1kV 3 core 6 sq mm PVC insulated copper flexible cable for control panel wiring with QCO compliance."
    res = extractor.extract_entities(text)
    
    assert res["category"] == "Electrical"
    assert "Copper" in res["materials"]
    assert "Pvc" in res["materials"]
    assert "QCO" in res["regulatory_terms"]

def test_nlp_entity_extraction_civil():
    extractor = NLPEntityExtractor()
    text = "Supply of 53 Grade Ordinary Portland Cement (OPC 53) in 50kg bags for concrete girder casting."
    res = extractor.extract_entities(text)
    
    assert res["category"] == "Civil"
    assert "Ordinary Portland Cement" in res["product"] or "Cement" in res["product"]
