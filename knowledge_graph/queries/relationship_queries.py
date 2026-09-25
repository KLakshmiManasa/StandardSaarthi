"""
SIH 26108 — Reusable Relationship & Reference Queries
"""

from typing import Dict, Any, List, Optional
from knowledge_graph.ingestion.build_graph import GraphStore

class RelationshipQueries:
    def __init__(self, graph_store: Optional[GraphStore] = None):
        if graph_store is None:
            graph_store = GraphStore(use_neo4j=False)
            graph_store.populate_graph()
        self.graph = graph_store

    def get_outgoing_relationships(self, is_code: str) -> List[Dict[str, Any]]:
        """Query 2 — Find outgoing relationships for an IS code."""
        code = is_code.strip()
        edges = self.graph.out_edges.get(code, [])
        results = []
        for e in edges:
            results.append({
                "source": e['source'],
                "target": e['target'],
                "relationship_type": e['type'],
                "properties": e.get('properties', {})
            })
        return results

    def get_referenced_standards(self, is_code: str) -> List[Dict[str, Any]]:
        """Query 6 — Find standards referenced by a given IS code."""
        code = is_code.strip()
        edges = self.graph.out_edges.get(code, [])
        referenced = []
        for e in edges:
            if e['target'] in self.graph.nodes["STANDARD"]:
                target_std = self.graph.nodes["STANDARD"][e['target']]
                referenced.append({
                    "relationship_type": e['type'],
                    "target_is_code": target_std['is_code'],
                    "target_title": target_std['title'],
                    "sector": target_std.get('sector', ''),
                    "provenance": e.get('properties', {})
                })
        return referenced

    def get_referencing_standards(self, is_code: str) -> List[Dict[str, Any]]:
        """Query 7 — Find standards that reference a given target IS code."""
        code = is_code.strip()
        edges = self.graph.in_edges.get(code, [])
        referencing = []
        for e in edges:
            if e['source'] in self.graph.nodes["STANDARD"]:
                src_std = self.graph.nodes["STANDARD"][e['source']]
                referencing.append({
                    "relationship_type": e['type'],
                    "source_is_code": src_std['is_code'],
                    "source_title": src_std['title'],
                    "provenance": e.get('properties', {})
                })
        return referencing

    def get_amendments(self, is_code: str) -> List[Dict[str, Any]]:
        """Query 8 — Find active amendments for an IS code."""
        code = is_code.strip()
        edges = self.graph.out_edges.get(code, [])
        amds = []
        for e in edges:
            if e['type'] == 'AMENDED_BY' and e['target'] in self.graph.nodes["AMENDMENT"]:
                amds.append(self.graph.nodes["AMENDMENT"][e['target']])
        return amds

    def get_qco_info(self, is_code: str) -> List[Dict[str, Any]]:
        """Query 9 — Find QCO information associated with an IS code."""
        code = is_code.strip()
        edges = self.graph.out_edges.get(code, [])
        qcos = []
        for e in edges:
            if e['type'] == 'ASSOCIATED_WITH_QCO' and e['target'] in self.graph.nodes["QCO"]:
                qcos.append(self.graph.nodes["QCO"][e['target']])
        return qcos


if __name__ == '__main__':
    rq = RelationshipQueries()
    refs = rq.get_referenced_standards("IS 694")
    print(f"[OK] Standard IS 694 references {len(refs)} standards:")
    for r in refs:
        print(f"  - [{r['relationship_type']}] -> {r['target_is_code']}: {r['target_title'][:50]}...")
