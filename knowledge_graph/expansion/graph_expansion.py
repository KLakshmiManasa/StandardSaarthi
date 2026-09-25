"""
SIH 26108 — Candidate Graph Expansion Engine
Expands Phase 3 ranked candidate standards with normative references, test methods,
and installation standards retrieved from the Knowledge Graph.
"""

from typing import List, Dict, Any, Optional
from knowledge_graph.ingestion.build_graph import GraphStore
from knowledge_graph.queries.relationship_queries import RelationshipQueries

class CandidateGraphExpander:
    def __init__(self, graph_store: Optional[GraphStore] = None):
        if graph_store is None:
            graph_store = GraphStore(use_neo4j=False)
            graph_store.populate_graph()
        self.graph = graph_store
        self.rel_queries = RelationshipQueries(self.graph)

    def expand_candidates(self, candidate_is_codes: List[str], max_depth: int = 1) -> Dict[str, Any]:
        """
        Expands Phase 3 candidate standards with verified graph dependencies.
        
        Args:
            candidate_is_codes (list): List of primary candidate IS codes (e.g. ['IS 694', 'IS 456']).
            max_depth (int): Traversal depth (default 1).
            
        Returns:
            dict: Expanded candidate evidence bundle grouped by source standard.
        """
        expansion_results = []
        derived_standards_set = set()

        for code in candidate_is_codes:
            code = code.strip()
            if code not in self.graph.nodes["STANDARD"]:
                continue

            src_std = self.graph.nodes["STANDARD"][code]
            refs = self.rel_queries.get_referenced_standards(code)
            amds = self.rel_queries.get_amendments(code)
            qcos = self.rel_queries.get_qco_info(code)

            derived_items = []
            for r in refs:
                target_code = r['target_is_code']
                derived_standards_set.add(target_code)
                derived_items.append({
                    "derived_is_code": target_code,
                    "derived_title": r['target_title'],
                    "sector": r.get('sector', ''),
                    "relationship_type": r['relationship_type'],
                    "graph_depth": 1,
                    "evidence_source": r.get('provenance', {}).get('source_clause', f"{code} Scope Clause"),
                    "verification_status": "VERIFIED"
                })

            expansion_results.append({
                "primary_candidate_is_code": code,
                "primary_title": src_std['title'],
                "primary_sector": src_std.get('sector', ''),
                "active_amendments_count": len(amds),
                "qco_compliance_associated": len(qcos) > 0,
                "graph_derived_standards": derived_items
            })

        return {
            "input_candidate_codes": candidate_is_codes,
            "total_primary_candidates": len(candidate_is_codes),
            "total_graph_derived_standards": len(derived_standards_set),
            "graph_expansion": expansion_results
        }


if __name__ == '__main__':
    expander = CandidateGraphExpander()
    res = expander.expand_candidates(["IS 694", "IS 456"])
    print("[OK] Graph Expansion Test:")
    for item in res['graph_expansion']:
        print(f"\nPrimary: {item['primary_candidate_is_code']} | QCO Associated: {item['qco_compliance_associated']}")
        for d in item['graph_derived_standards']:
            print(f"  - [{d['relationship_type']}] -> {d['derived_is_code']}: {d['derived_title'][:50]}...")
