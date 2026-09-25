"""
Unit tests for Graph Traversal & Phase 3 Candidate Expansion.
"""

from knowledge_graph.queries.traversal_queries import TraversalQueries
from knowledge_graph.expansion.graph_expansion import CandidateGraphExpander

def test_one_hop_traversal():
    tq = TraversalQueries()
    res = tq.traverse_one_hop("IS 694")
    assert res['found'] is True
    assert res['relationship_count'] > 0

def test_two_hop_traversal():
    tq = TraversalQueries()
    res = tq.traverse_two_hop("IS 694", max_branch=5)
    assert res['found'] is True
    assert res['depth'] == 2
    assert len(res['two_hop_paths']) > 0

def test_candidate_graph_expansion():
    expander = CandidateGraphExpander()
    res = expander.expand_candidates(["IS 694", "IS 456"])
    assert res['total_primary_candidates'] == 2
    assert res['total_graph_derived_standards'] > 0
