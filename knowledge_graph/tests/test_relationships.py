"""
Unit tests for Knowledge Graph Relationships & Edges.
"""

from knowledge_graph.ingestion.build_graph import GraphStore
from knowledge_graph.queries.relationship_queries import RelationshipQueries

def test_relationship_integrity():
    graph = GraphStore(use_neo4j=False)
    graph.populate_graph()
    rq = RelationshipQueries(graph)

    # Check IS 694 references
    refs = rq.get_referenced_standards("IS 694")
    ref_codes = [r['target_is_code'] for r in refs]
    assert "IS 8130" in ref_codes
    assert "IS 10810:Part 62" in ref_codes

def test_qco_relationship():
    graph = GraphStore(use_neo4j=False)
    graph.populate_graph()
    rq = RelationshipQueries(graph)

    qcos = rq.get_qco_info("IS 694")
    assert len(qcos) > 0
    assert qcos[0]['mandatory_status'] == "MANDATORY"
