"""
Unit tests for BM25 Search Engine.
"""

from phase2.retrieval.bm25_search import BM25SearchEngine

def test_bm25_search_success():
    engine = BM25SearchEngine()
    res = engine.search("Polyvinyl Chloride Insulated Cables for Working Voltages", top_k=5)
    assert res['method'] == "bm25"
    assert len(res['results']) > 0
    codes = [r['is_code'] for r in res['results']]
    assert "IS 694" in codes

def test_bm25_empty_query():
    engine = BM25SearchEngine()
    res = engine.search("", top_k=5)
    assert res['results'] == []

def test_bm25_sector_filter():
    engine = BM25SearchEngine()
    res = engine.search("cables concrete", top_k=10, sector_filter="Electrical")
    for r in res['results']:
        assert r['sector'] == "Electrical"
