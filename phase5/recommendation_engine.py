"""
SIH 26108 — Phase 5 Master Graph-RAG & Explainable Recommendation Engine
Orchestrates end-to-end procurement intelligence pipeline:
Procurement Description -> NLP Entity Extraction -> Vector Retrieval -> Graph-RAG Traversal ->
QCO Evaluation -> Configurable Hybrid Ranking -> Evidence Verification -> Explainable Recommendation Bundle.
"""

import time
from typing import Dict, Any, List, Optional
from nlp.entity_extractor import NLPEntityExtractor
from phase5.retrieval.vector_retriever import Phase5VectorRetriever
from phase5.retrieval.graph_rag import GraphRAGRetriever
from phase5.qco.qco_engine import QCOEngine
from phase5.ranking.hybrid_ranker import HybridRanker
from phase5.evidence.evidence_system import EvidenceSystem

class Phase5RecommendationEngine:
    def __init__(self):
        self.nlp_extractor = NLPEntityExtractor()
        self.vector_retriever = Phase5VectorRetriever()
        self.graph_rag = GraphRAGRetriever()
        self.qco_engine = QCOEngine(self.graph_rag.graph)
        self.hybrid_ranker = HybridRanker()
        self.evidence_system = EvidenceSystem()

    def recommend(self, query: str, top_k: int = 10, mode: str = "graph_rag") -> Dict[str, Any]:
        """
        Executes end-to-end explainable Indian Standards recommendation pipeline.
        
        Args:
            query (str): Natural language procurement specification text.
            top_k (int): Number of top recommendations to return.
            mode (str): Mode selector ('keyword', 'vector', or 'graph_rag').
            
        Returns:
            dict: Structured recommendation output bundle.
        """
        start_time = time.time()
        query_text = query.strip()

        # 1. NLP Entity Extraction
        entities = self.nlp_extractor.extract_entities(query_text)

        # 2. Vector Semantic Candidate Retrieval
        vector_candidates = self.vector_retriever.retrieve_candidates(query_text, top_k=top_k*2, sector=entities.get("category"))
        candidate_codes = [c["is_code"] for c in vector_candidates]
        sim_map = {c["is_code"]: c["similarity"] for c in vector_candidates}

        # 3. Graph-RAG Traversal & Evidence Retrieval
        graph_contexts = self.graph_rag.retrieve_graph_rag_context(candidate_codes, entities)

        # 4. QCO Evaluation & Hybrid Ranking
        recommendations = []
        for g_ctx in graph_contexts:
            is_code = g_ctx["is_code"]
            vec_sim = sim_map.get(is_code, 0.5)

            # Evaluate QCO status
            qco_eval = self.qco_engine.evaluate_qco_compliance(is_code)

            # Entity Match Scores
            m_entities = g_ctx.get("matching_entities", {})
            prod_match = 1.0 if m_entities.get("product_match") else 0.0
            mat_match = len(m_entities.get("matched_materials", [])) / max(1, len(entities.get("materials", []))) if entities.get("materials") else 0.5
            entity_match_score = (prod_match * 0.6) + (mat_match * 0.4)
            app_match_score = 1.0 if m_entities.get("application_match") else 0.3

            # Compute Hybrid Relevance Score
            rank_result = self.hybrid_ranker.compute_relevance_score(
                vector_sim=vec_sim,
                entity_match_score=entity_match_score,
                graph_rel_score=g_ctx.get("graph_relevance_score", 0.5),
                app_match_score=app_match_score,
                qco_mandatory=qco_eval.get("qco_mandatory", False)
            )

            # Build Explanation
            explanation = self.hybrid_ranker.generate_explanation(
                is_code=is_code,
                title=g_ctx["title"],
                breakdown=rank_result["score_breakdown"],
                entities={
                    "product_match": m_entities.get("product_match"),
                    "matched_product": entities.get("product"),
                    "matched_materials": m_entities.get("matched_materials")
                },
                qco_info=qco_eval
            )

            # Evidence Package
            evidence = self.evidence_system.create_evidence_package(
                std_info={
                    "is_code": is_code,
                    "title": g_ctx["title"],
                    "description": g_ctx.get("scope_text", g_ctx["title"]),
                    "source_organization": g_ctx["source_provenance"]["source_organization"],
                    "source_document": g_ctx["source_provenance"]["source_document"],
                    "source_url": g_ctx["source_provenance"]["source_url"]
                },
                qco_info=qco_eval,
                matching_clauses=g_ctx.get("clauses", [])
            )

            recommendations.append({
                "is_code": is_code,
                "title": g_ctx["title"],
                "sector": g_ctx["sector"],
                "product_category": g_ctx["product_category"],
                "relevance_score": rank_result["relevance_score"],
                "confidence_level": rank_result["confidence_level"],
                "score_breakdown": rank_result["score_breakdown"],
                "explanation": explanation,
                "qco_information": qco_eval,
                "matching_entities": m_entities,
                "referenced_standards": g_ctx.get("referenced_standards", []),
                "evidence": evidence
            })

        # Sort recommendations by relevance_score descending
        recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
        final_recommendations = recommendations[:top_k]

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "query": query_text,
            "pipeline_mode": mode,
            "extracted_entities": entities,
            "total_candidates_evaluated": len(recommendations),
            "recommended_standards_count": len(final_recommendations),
            "recommended_standards": final_recommendations,
            "processing_metadata": {
                "latency_ms": elapsed_ms,
                "dataset_version": "v0.1-pilot",
                "engine_version": "0.5.0-graphrag"
            }
        }


if __name__ == '__main__':
    engine = Phase5RecommendationEngine()
    sample = "Procurement of 1.1kV 3 core 6 sq mm PVC insulated copper flexible cable for control panel wiring with QCO compliance."
    res = engine.recommend(sample, top_k=3)
    print(f"[OK] Recommendation Engine output generated in {res['processing_metadata']['latency_ms']} ms.")
    print(f"Query: {res['query']}")
    print(f"Extracted Entities: {res['extracted_entities']}")
    print("\nTop Recommendations:")
    for r in res['recommended_standards']:
        print(f"\n- [{r['is_code']}] Score: {r['relevance_score']} ({r['confidence_level']}) | {r['title']}")
        print(f"  Explanation: {r['explanation']}")
        print(f"  QCO Status: {r['qco_information']['status']}")
        print(f"  Source Org: {r['evidence']['source_organization']} | URL: {r['evidence']['source_url']}")
