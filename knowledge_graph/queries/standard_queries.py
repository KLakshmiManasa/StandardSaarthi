"""
SIH 26108 — Reusable Cypher & Graph Queries for Standards & Entities
"""

from typing import Dict, Any, List, Optional
from knowledge_graph.ingestion.build_graph import GraphStore

class StandardQueries:
    def __init__(self, graph_store: Optional[GraphStore] = None):
        if graph_store is None:
            graph_store = GraphStore(use_neo4j=False)
            graph_store.populate_graph()
        self.graph = graph_store

    def get_standard_by_code(self, is_code: str) -> Optional[Dict[str, Any]]:
        """Query 1 — Find standard by IS code."""
        code = is_code.strip()
        return self.graph.nodes["STANDARD"].get(code)

    def find_standards_by_product(self, product_name: str) -> List[Dict[str, Any]]:
        """Query 3 — Find standards for a product."""
        p_norm = product_name.lower().strip().replace(' ', '_')
        matched_standards = []
        for src_id, edges in self.graph.out_edges.items():
            for e in edges:
                if e['type'] == 'SPECIFIES_PRODUCT' and (e['target'] == p_norm or p_norm in e['target']):
                    std = self.get_standard_by_code(src_id)
                    if std and std not in matched_standards:
                        matched_standards.append(std)
        return matched_standards

    def find_standards_by_material(self, material_name: str) -> List[Dict[str, Any]]:
        """Query 4 — Find standards associated with a material."""
        m_norm = material_name.lower().strip().replace(' ', '_')
        matched_standards = []
        for src_id, edges in self.graph.out_edges.items():
            for e in edges:
                if e['type'] == 'USES_MATERIAL' and (e['target'] == m_norm or m_norm in e['target']):
                    std = self.get_standard_by_code(src_id)
                    if std and std not in matched_standards:
                        matched_standards.append(std)
        return matched_standards

    def find_standards_by_application(self, application_name: str) -> List[Dict[str, Any]]:
        """Query 5 — Find application-related standards."""
        a_norm = application_name.lower().strip().replace(' ', '_')
        matched_standards = []
        for src_id, edges in self.graph.out_edges.items():
            for e in edges:
                if e['type'] == 'APPLIES_TO' and (a_norm in e['target']):
                    std = self.get_standard_by_code(src_id)
                    if std and std not in matched_standards:
                        matched_standards.append(std)
        return matched_standards


if __name__ == '__main__':
    sq = StandardQueries()
    std = sq.get_standard_by_code("IS 694")
    print(f"[OK] Found Standard IS 694: {std['title'] if std else 'Not Found'}")
