"""
Unit tests for Query Preprocessing Module.
"""

from phase2.retrieval.preprocess import preprocess_query

def test_empty_query():
    res = preprocess_query("")
    assert res['original_query'] == ""
    assert res['normalized_query'] == ""
    assert res['tokens'] == []

def test_whitespace_and_lowercase():
    res = preprocess_query("  SUPPLY OF   PVC   CABLES  ")
    assert res['normalized_query'] == "supply of pvc cables"
    assert "pvc" in res['tokens']
    assert "cables" in res['tokens']

def test_domain_term_preservation():
    res = preprocess_query("1.5 sq mm single core PVC insulated copper cable")
    assert "pvc" in res['tokens']
    assert "copper" in res['tokens']
    assert "cable" in res['tokens']
