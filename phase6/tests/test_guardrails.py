"""
Unit tests for Phase 6 Query Guardrails (Ambiguity & Out-of-Domain Detection)
"""

import pytest
from phase6.guardrails.query_guardrails import QueryGuardrails

def test_guardrails_valid_query():
    guard = QueryGuardrails()
    status, details = guard.evaluate_query("Procurement of 1.1kV 3 core 6 sq mm PVC insulated copper flexible cable")
    assert status == "VALID"

def test_guardrails_ambiguous_query():
    guard = QueryGuardrails()
    status, details = guard.evaluate_query("hospital equipment")
    assert status == "AMBIGUOUS"
    assert "missing_fields" in details

def test_guardrails_out_of_domain_query():
    guard = QueryGuardrails()
    status, details = guard.evaluate_query("What is the capital city of France?")
    assert status == "OUT_OF_DOMAIN"
    assert details["status"] == "OUT_OF_DOMAIN_REJECTION"
