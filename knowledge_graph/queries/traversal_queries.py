"""
SIH 26108 — Controlled 1-Hop and 2-Hop Graph Traversal Queries
"""

from typing import Dict, Any, List, Optional, Set
from knowledge_graph.ingestion.build_graph import GraphStore

class TraversalQueries:
    def __init__(self, graph_store: Optional[GraphStore] = None):
        if graph_store is None:
            graph_store = GraphStore(use_neo4j=False)
            graph_store.populate_graph()
        self.graph = graph_store

    def traverse_one_hop(self, is_code: str) -> Dict[str, Any]:
        """
        Executes controlled 1-hop graph traversal for a standard node.
        """
        code = is_code.strip()
        std_node = self.graph.nodes["STANDARD"].get(code)
        if not std_node:
            return {"is_code": code, "found": False, "relationships": []}

        out_edges = self.graph.out_edges.get(code, [])
        in_edges = self.graph.in_edges.get(code, [])

        rels = []
        for e in out_edges:
            rels.append({
                "direction": "OUTGOING",
                "relationship": e['type'],
                "target_id": e['target'],
                "target_label": self._get_node_label(e['target']),
                "properties": e.get('properties', {})
            })

        for e in in_edges:
            rels.append({
                "direction": "INCOMING",
                "relationship": e['type'],
                "source_id": e['source'],
                "source_label": self._get_node_label(e['source']),
                "properties": e.get('properties', {})
            })

        return {
            "is_code": code,
            "found": True,
            "standard_title": std_node.get('title', ''),
            "depth": 1,
            "relationship_count": len(rels),
            "relationships": rels
        }

    def traverse_two_hop(self, is_code: str, max_branch: int = 10) -> Dict[str, Any]:
        """
        Executes controlled 2-hop graph traversal with strict branch limits to prevent graph explosion.
        """
        hop1_data = self.traverse_one_hop(is_code)
        if not hop1_data.get("found"):
            return {"is_code": is_code, "found": False, "two_hop_paths": []}

        two_hop_paths = []
        visited = set([is_code])

        branch_count = 0
        for rel1 in hop1_data["relationships"]:
            target_id = rel1.get("target_id") or rel1.get("source_id")
            if not target_id or target_id in visited:
                continue

            rel1_type = rel1["relationship"]

            # Hop 2: look up outgoing edges from target_id
            edges_hop2 = self.graph.out_edges.get(target_id, [])
            if not edges_hop2:
                continue

            visited.add(target_id)
            for e2 in edges_hop2:
                tgt2 = e2['target']
                if tgt2 == is_code:
                    continue
                two_hop_paths.append({
                    "hop1": {"relationship": rel1_type, "target": target_id, "target_label": self._get_node_label(target_id)},
                    "hop2": {"relationship": e2['type'], "target": tgt2, "target_label": self._get_node_label(tgt2)},
                    "path_str": f"{is_code} -[:{rel1_type}]-> {target_id} -[:{e2['type']}]-> {tgt2}"
                })

            branch_count += 1
            if branch_count >= max_branch:
                break

        return {
            "is_code": is_code,
            "found": True,
            "depth": 2,
            "path_count": len(two_hop_paths),
            "two_hop_paths": two_hop_paths
        }

    def _get_node_label(self, node_id: str) -> str:
        for label, node_dict in self.graph.nodes.items():
            if node_id in node_dict:
                return label
        return "UNKNOWN"


if __name__ == '__main__':
    tq = TraversalQueries()
    h1 = tq.traverse_one_hop("IS 694")
    print(f"[OK] 1-Hop Traversal for IS 694: {h1['relationship_count']} edges found.")
    h2 = tq.traverse_two_hop("IS 694")
    print(f"[OK] 2-Hop Traversal for IS 694: {h2['path_count']} 2-step paths found.")
