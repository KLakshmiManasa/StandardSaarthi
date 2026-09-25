"""
Unit tests for Phase 5 Configurable Hybrid Ranker
"""

import pytest
from phase5.ranking.hybrid_ranker import HybridRanker

def test_hybrid_ranker_scoring():
    ranker = HybridRanker()
    res = ranker.compute_relevance_score(
        vector_sim=0.90,
        entity_match_score=0.80,
        graph_rel_score=0.85,
        app_match_score=0.70,
        qco_mandatory=True
    )
    assert 0.0 <= res["relevance_score"] <= 1.0
    assert res["confidence_level"] in ["HIGH", "MEDIUM", "LOW"]
    assert "score_breakdown" in res
