"""
Unit tests for Phase 5 QCO Regulatory Engine
"""

import pytest
from phase5.qco.qco_engine import QCOEngine, UNVERIFIED_QCO_MESSAGE

def test_qco_evaluation_mandatory():
    engine = QCOEngine()
    res = engine.evaluate_qco_compliance("IS 694")
    assert res["qco_mandatory"] is True
    assert res["status"] == "MANDATORY_QUALITY_CONTROL_ORDER"
    assert res["qco_id"] is not None

def test_qco_evaluation_unverified():
    engine = QCOEngine()
    res = engine.evaluate_qco_compliance("IS 99999") # Non-existent IS code
    assert res["qco_mandatory"] is False
    assert res["regulatory_notice"] == UNVERIFIED_QCO_MESSAGE
