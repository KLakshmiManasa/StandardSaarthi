"""
Unit tests for Knowledge Graph Node Creation & Properties.
"""

from knowledge_graph.ingestion.build_graph import GraphStore

def test_node_creation_and_counts():
    graph = GraphStore(use_neo4j=False)
    graph.populate_graph()
    stats = graph.get_stats()

    assert stats['node_counts']['STANDARD'] == 120
    assert stats['node_counts']['PRODUCT'] > 0
    assert stats['node_counts']['MATERIAL'] > 0
    assert stats['node_counts']['APPLICATION'] > 0
    assert stats['node_counts']['TEST_METHOD'] > 0
    assert stats['node_counts']['QCO'] == 42

def test_duplicate_standard_node_prevention():
    graph = GraphStore(use_neo4j=False)
    graph.populate_graph()
    initial_count = len(graph.nodes["STANDARD"])
    
    # Attempt duplicate insert
    graph.add_node("STANDARD", "IS 694", {"title": "Duplicate IS 694"})
    assert len(graph.nodes["STANDARD"]) == initial_count
