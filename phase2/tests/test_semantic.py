"""
Unit tests for Semantic and Hybrid Search Engine.
"""

from phase2.retrieval.semantic_search import SemanticSearchEngine
from phase2.retrieval.hybrid_search import HybridSearchEngine

def test_semantic_search():
    engine = SemanticSearchEngine()
    res = engine.search("Underground HT power cable", top_k=5)
    assert res['method'] == "semantic"
    assert len(res['results']) > 0

def test_hybrid_search():
    engine = HybridSearchEngine()
    res = engine.search("Fe 500D TMT steel rebar for RCC column", top_k=5, alpha=0.5)
    assert res['method'] == "hybrid"
    assert len(res['results']) > 0
    assert res['results'][0]['is_code'] == "IS 1786"
    assert 'normalized_bm25' in res['results'][0]
    assert 'normalized_semantic' in res['results'][0]
