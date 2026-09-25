"""
Unit tests for Structured Metadata Scoring Engine.
"""

from phase3.ranking.metadata_scoring import MetadataScorer

def test_metadata_scorer_weights():
    scorer = MetadataScorer()
    res = scorer.score_candidate("PVC insulated copper cables", "IS 694")
    assert "metadata_score" in res
    assert 0.0 <= res["metadata_score"] <= 1.0
    assert "product_category" in res["matched_fields"]

def test_metadata_weight_validation():
    custom_weights = {"sector": 2.0, "product_category": 3.0, "material": 1.0, "application": 2.0, "technical_parameters": 2.0}
    scorer = MetadataScorer(custom_weights)
    tot = sum(scorer.weights.values())
    assert abs(tot - 1.0) < 1e-4
