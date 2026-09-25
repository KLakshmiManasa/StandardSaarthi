"""
Unit tests for Cross-Encoder Reranker.
"""

from phase3.ranking.reranker import CrossEncoderReranker

def test_reranker_scores():
    reranker = CrossEncoderReranker()
    candidates = [
        {"is_code": "IS 694", "rrf_score": 0.03},
        {"is_code": "IS 8130", "rrf_score": 0.02}
    ]
    query = "Supply of PVC insulated copper electrical cables"
    reranked = reranker.rerank(query, candidates, rerank_top_n=2)
    assert len(reranked) == 2
    assert "reranker_score" in reranked[0]
    assert 0.0 <= reranked[0]["reranker_score"] <= 1.0
