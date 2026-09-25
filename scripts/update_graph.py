"""
SIH 26108 — Phase 8 Knowledge Graph Updater Script
Populates and refreshes dual-store Knowledge Graph (Neo4j / In-Memory).
"""

import os
from knowledge_graph.ingestion.build_graph import GraphStore

def update_knowledge_graph(use_neo4j: bool = False):
    print(f"[*] Updating Knowledge Graph (Neo4j={use_neo4j})...")
    graph = GraphStore(use_neo4j=use_neo4j)
    graph.populate_graph()
    stats = graph.get_stats()
    print(f"[OK] Knowledge Graph updated: {stats['total_nodes']} nodes, {stats.get('total_relationships', 0)} relationships.")
    return stats

if __name__ == '__main__':
    update_knowledge_graph(use_neo4j=False)
