"""
Unit tests for Reciprocal Rank Fusion Engine.
"""

from phase3.ranking.rrf import RRFEngine, reciprocal_rank_fusion

def test_rrf_scoring_formula():
    bm25_res = [{"is_code": "IS 694", "rank": 1, "title": "Cables"}]
    semantic_res = [{"is_code": "IS 694", "rank": 2, "title": "Cables"}]
    
    fused = reciprocal_rank_fusion(bm25_res, semantic_res, rrf_k=60)
    expected_score = (1.0 / (60 + 1)) + (1.0 / (60 + 2))
    assert len(fused) == 1
    assert abs(fused[0]['rrf_score'] - round(expected_score, 6)) < 1e-5

def test_rrf_engine_search():
    engine = RRFEngine()
    res = engine.search("PVC insulated copper electrical cable", top_k=5)
    assert res['method'] == "rrf"
    assert len(res['results']) > 0
    codes = [r['is_code'] for r in res['results']]
    assert "IS 694" in codes
