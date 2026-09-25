"""
SIH 26108 — Phase 5 Graph-RAG Retrieval & Traversal Module
Combines extracted procurement query entities with Knowledge Graph traversals to retrieve multi-hop context,
clauses, related standards, QCO obligations, and supporting evidence.
"""

from typing import Dict, Any, List, Optional
from knowledge_graph.ingestion.build_graph import GraphStore
from knowledge_graph.queries.standard_queries import StandardQueries
from knowledge_graph.queries.relationship_queries import RelationshipQueries
from knowledge_graph.queries.traversal_queries import TraversalQueries

class GraphRAGRetriever:
    def __init__(self, graph_store: Optional[GraphStore] = None):
        if graph_store is None:
            graph_store = GraphStore(use_neo4j=False)
            graph_store.populate_graph()
        self.graph = graph_store
        self.std_queries = StandardQueries(self.graph)
        self.rel_queries = RelationshipQueries(self.graph)
        self.trav_queries = TraversalQueries(self.graph)

    def retrieve_graph_rag_context(
        self,
        candidate_is_codes: List[str],
        extracted_entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Performs Graph-RAG context retrieval for candidate standards based on extracted query entities.
        
        Args:
            candidate_is_codes (list): List of candidate IS codes (e.g. ['IS 694', 'IS 456']).
            extracted_entities (dict): Extracted query entities from NLP module.
            
        Returns:
            list: List of candidate standards enriched with Graph-RAG evidence packages.
        """
        query_prod = extracted_entities.get("product", "").lower()
        query_mats = [m.lower() for m in extracted_entities.get("materials", [])]
        query_app = extracted_entities.get("application", "").lower()

        graph_candidates = []

        for is_code in candidate_is_codes:
            std_node = self.std_queries.get_standard_by_code(is_code)
            if not std_node:
                continue

            # 1. Traversal: Get outgoing relationships, normative references, amendments, and QCOs
            outgoing = self.rel_queries.get_outgoing_relationships(is_code)
            referenced_stds = self.rel_queries.get_referenced_standards(is_code)
            amendments = self.rel_queries.get_amendments(is_code)
            qco_info = self.rel_queries.get_qco_info(is_code)
            hop2_paths = self.trav_queries.traverse_two_hop(is_code, max_branch=5)

            # 2. Entity Overlap & Graph Matching
            std_prod = std_node.get("product_category", "").lower()
            std_mats = [m.strip().lower() for m in std_node.get("materials", "").split(",")]
            std_apps = std_node.get("applications", "").lower()

            product_match = any(w in std_prod or std_prod in w for w in query_prod.split()) if query_prod else False
            mat_matches = [m for m in query_mats if any(m in sm or sm in m for sm in std_mats)]
            material_match_score = len(mat_matches) / max(1, len(query_mats)) if query_mats else 0.5
            app_match = any(w in std_apps for w in query_app.split()) if query_app else False

            # 3. Clauses Retrieval
            clauses = std_node.get("clauses", [
                {"clause_no": "Scope & Field of Application", "content": std_node.get("scope_text", "")},
                {"clause_no": "Normative References", "content": std_node.get("normative_references", "")},
                {"clause_no": "Technical Requirements", "content": std_node.get("technical_parameters", "")}
            ])

            # 4. Graph Relevance Score Computation
            graph_relevance = 0.0
            if product_match:
                graph_relevance += 0.35
            graph_relevance += material_match_score * 0.25
            if app_match:
                graph_relevance += 0.20
            if qco_info:
                graph_relevance += 0.10
            if len(referenced_stds) > 0:
                graph_relevance += 0.10

            graph_relevance = min(1.0, round(graph_relevance, 4))

            graph_candidates.append({
                "is_code": is_code,
                "title": std_node.get("title", ""),
                "sector": std_node.get("sector", ""),
                "product_category": std_node.get("product_category", ""),
                "graph_relevance_score": graph_relevance,
                "matching_entities": {
                    "product_match": product_match,
                    "matched_materials": mat_matches,
                    "application_match": app_match
                },
                "referenced_standards": referenced_stds,
                "amendments_count": len(amendments),
                "qco_info": qco_info,
                "clauses": clauses,
                "two_hop_graph_paths": hop2_paths.get("two_hop_paths", [])[:3],
                "source_provenance": {
                    "source_organization": std_node.get("source_organization", "Bureau of Indian Standards (BIS)"),
                    "source_document": std_node.get("source_document", "BIS Standards Portal"),
                    "source_url": std_node.get("source_url") or "https://standards.bis.gov.in/"
                }
            })

        return graph_candidates


if __name__ == '__main__':
    rag = GraphRAGRetriever()
    extracted = {
        "product": "Pvc Insulated Cable",
        "category": "Electrical",
        "materials": ["Copper", "Pvc"],
        "application": "Control Panel Wiring",
        "industry": "Electrical"
    }
    candidates = rag.retrieve_graph_rag_context(["IS 694", "IS 1554:Part 1"], extracted)
    print(f"[OK] Graph-RAG retrieved context for {len(candidates)} standards:")
    for c in candidates:
        print(f"  Standard {c['is_code']} | Graph Relevance: {c['graph_relevance_score']} | Referenced Standards: {len(c['referenced_standards'])}")
