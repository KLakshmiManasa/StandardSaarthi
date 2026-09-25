"""
Unit tests for Final Phase 3 Multi-Factor Ranking Engine.
"""

from phase3.ranking.final_ranker import Phase3FinalRanker

def test_final_ranker_search():
    ranker = Phase3FinalRanker()
    res = ranker.search("PVC insulated copper electrical cable for hospital internal wiring", top_k=5)
    assert res['method'] == "phase3"
    assert len(res['results']) > 0
    assert res['results'][0]['is_code'] == "IS 694"
    assert "reranker_score" in res['results'][0]
    assert "metadata_score" in res['results'][0]
    assert "relevance_category" in res['results'][0]

def test_final_ranker_weight_sum():
    ranker = Phase3FinalRanker()
    weight_sum = ranker.alpha + ranker.beta + ranker.gamma
    assert abs(weight_sum - 1.0) < 1e-4

def test_final_ranker_empty_query():
    ranker = Phase3FinalRanker()
    res = ranker.search("", top_k=5)
    assert res['results'] == []
