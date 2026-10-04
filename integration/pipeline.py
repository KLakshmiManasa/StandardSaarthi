"""
SIH 26108 — Phase 7 Master Integration Pipeline Orchestrator
Provides one unified entry point `recommend(procurement_description)` that coordinates:
Security Sanitization -> Query Guardrails -> NLP Entity Extraction -> Vector Retrieval -> Graph-RAG ->
QCO Evaluation -> Hybrid Ranking -> Evidence Verification -> Stable Response Schema.
"""

import time
import logging
from typing import Dict, Any, List, Optional

from phase6.security.security_sanitizer import SecuritySanitizer
from phase6.guardrails.query_guardrails import QueryGuardrails
from nlp.entity_extractor import NLPEntityExtractor
from phase5.retrieval.vector_retriever import Phase5VectorRetriever
from phase5.retrieval.graph_rag import GraphRAGRetriever
from phase5.qco.qco_engine import QCOEngine
from phase5.ranking.hybrid_ranker import HybridRanker
from phase5.evidence.evidence_system import EvidenceSystem
from services.standards_service import standards_service

logger = logging.getLogger("SIH26108_Pipeline")

class IntegrationPipeline:
    def __init__(self):
        self.sanitizer = SecuritySanitizer()
        self.guardrails = QueryGuardrails()
        self.nlp_extractor = NLPEntityExtractor()

        # Initialize core AI components with fallback error handling
        self.vector_error = None
        try:
            self.vector_retriever = Phase5VectorRetriever()
            self.vector_available = True
        except Exception as e:
            logger.error(f"Vector Retriever initialization failed: {e}")
            self.vector_available = False
            self.vector_error = str(e)

        try:
            self.graph_rag = GraphRAGRetriever()
            self.graph_available = True
        except Exception as e:
            logger.error(f"Graph-RAG initialization failed: {e}")
            self.graph_available = False

        self.qco_engine = QCOEngine(self.graph_rag.graph if self.graph_available else None)
        self.hybrid_ranker = HybridRanker()
        self.evidence_system = EvidenceSystem()

    def recommend(self, procurement_description: str, raw_user_query: Optional[str] = None, top_k: int = 10, mode: str = "graph_rag") -> Dict[str, Any]:
        """
        Master Pipeline Entry Point: Accepts natural language procurement description and returns structured response.
        """
        start_time = time.time()
        proc_desc = str(procurement_description or "").strip()
        user_raw = str(raw_user_query or proc_desc).strip()
        warnings = []

        # 1. Security Sanitization
        is_safe, sanitized_text, threat = self.sanitizer.sanitize_input(proc_desc)
        if not is_safe:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "security_blocked",
                "query": user_raw,
                "message": f"Security Alert: Request blocked due to {threat} detection.",
                "entities": None,
                "recommendations": [],
                "warnings": [f"Input threat detected: {threat}"],
                "processing": {
                    "retrieval_method": "Security Blocked",
                    "candidate_count": 0,
                    "latency_ms": elapsed_ms,
                    "dataset_version": "v0.1-pilot",
                    "engine_version": "0.7.0-integrated"
                }
            }

        # 2. Pre-extract NLP Entities from both original user query and sanitized text
        combined_text_for_nlp = f"{user_raw} {sanitized_text}".strip()
        entities = self.nlp_extractor.extract_entities(combined_text_for_nlp)
        entity_summary = {
            "product": entities.get("product"),
            "category": entities.get("category"),
            "materials": entities.get("materials", []),
            "container": entities.get("container", ""),
            "volume": entities.get("volume", ""),
            "application": entities.get("application"),
            "industry": entities.get("industry")
        }

        # 3. Query Guardrails Check with Extracted Entity Awareness
        guard_status, guard_details = self.guardrails.evaluate_query(sanitized_text, entities=entities)
        if guard_status == 'OUT_OF_DOMAIN':
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "out_of_domain",
                "query": user_raw,
                "message": guard_details.get("message", "This system is designed to recommend Indian Standards for procurement descriptions."),
                "entities": entity_summary,
                "recommendations": [],
                "warnings": ["Query classified as outside Indian Standards procurement domain."],
                "processing": {
                    "retrieval_method": "Guardrail Rejection",
                    "candidate_count": 0,
                    "latency_ms": elapsed_ms,
                    "dataset_version": "v0.1-pilot",
                    "engine_version": "0.7.0-integrated"
                }
            }
        elif guard_status == 'AMBIGUOUS':
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "needs_clarification",
                "query": user_raw,
                "message": guard_details.get("message", "Please provide equipment type, intended application, or technical specifications."),
                "missing_fields": guard_details.get("missing_fields", ["product_type", "application", "material", "technical_characteristics"]),
                "entities": entity_summary,
                "recommendations": [],
                "warnings": ["Insufficient query detail for confident recommendation."],
                "processing": {
                    "retrieval_method": "Guardrail Ambiguity",
                    "candidate_count": 0,
                    "latency_ms": elapsed_ms,
                    "dataset_version": "v0.1-pilot",
                    "engine_version": "0.7.0-integrated"
                }
            }

        # 4. Vector Semantic Retrieval
        sector_filter = entities.get("category")
        sector_filter_applied = True
        if not sector_filter or str(sector_filter).lower() in ["general", "unknown", "none", ""]:
            sector_filter = None
            sector_filter_applied = False

        if not self.vector_available:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "error",
                "query": user_raw,
                "message": f"Embedding model unavailable: {self.vector_error or 'sentence-transformers is not loaded'}. Recommendations blocked.",
                "entities": entity_summary,
                "recommendations": [],
                "warnings": ["Recommendation blocked: dense vector embedding model is unavailable."],
                "processing": {
                    "retrieval_method": "Unavailable",
                    "candidate_count": 0,
                    "latency_ms": elapsed_ms,
                    "dataset_version": "v0.1-pilot",
                    "engine_version": "0.7.0-integrated"
                }
            }
        else:
            vector_candidates = self.vector_retriever.retrieve_candidates(sanitized_text, top_k=top_k*2, sector=sector_filter)
            if not vector_candidates and sector_filter is not None:
                logger.info(f"Sector filter '{sector_filter}' produced 0 candidates. Falling back to global search.")
                vector_candidates = self.vector_retriever.retrieve_candidates(sanitized_text, top_k=top_k*2, sector=None)
                sector_filter_applied = False

        # Structured Debug Logging for Multilingual & Entity Pipeline
        top_cand_code = vector_candidates[0]["is_code"] if vector_candidates else "NONE"
        logger.info(
            f"[DEBUG LOGGING] Requirement Analysis Pipeline Run:\n"
            f"  - Original Query: {user_raw}\n"
            f"  - Processed Query: {sanitized_text}\n"
            f"  - Extracted Entities: {entity_summary}\n"
            f"  - Guardrail Status: {guard_status}\n"
            f"  - Sector Filter: '{sector_filter}' (Applied: {sector_filter_applied})\n"
            f"  - Candidates Found: {len(vector_candidates)}\n"
            f"  - Top Retrieved Candidate: '{top_cand_code}'"
        )

        if not vector_candidates:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "no_results",
                "query": sanitized_text,
                "message": "No verified Indian Standard was found in the current knowledge base matching your query.",
                "entities": entity_summary,
                "recommendations": [],
                "warnings": warnings,
                "processing": {
                    "retrieval_method": "Vector Search",
                    "candidate_count": 0,
                    "latency_ms": elapsed_ms,
                    "dataset_version": "v0.1-pilot",
                    "engine_version": "0.7.0-integrated"
                }
            }

        candidate_codes = [c["is_code"] for c in vector_candidates]
        sim_map = {c["is_code"]: c["similarity"] for c in vector_candidates}

        # 5. Graph-RAG Retrieval & Enrichment
        if self.graph_available:
            graph_contexts = self.graph_rag.retrieve_graph_rag_context(candidate_codes, entities)
        else:
            warnings.append("Knowledge Graph service degraded; graph RAG context unavailable.")
            graph_contexts = [{"is_code": code, "title": code, "sector": entities.get("category", "General"), "product_category": entities.get("category", "General"), "graph_relevance_score": 0.5, "matching_entities": {}, "referenced_standards": [], "clauses": [], "source_provenance": {"source_organization": "Bureau of Indian Standards (BIS)", "source_document": "BIS Standards Portal", "source_url": "https://standards.bis.gov.in/"}} for code in candidate_codes]

        # 6. QCO Evaluation & Hybrid Ranking
        recommendations = []
        for g_ctx in graph_contexts:
            is_code = g_ctx["is_code"]
            vec_sim = sim_map.get(is_code, 0.5)

            # QCO Evaluation
            qco_eval = self.qco_engine.evaluate_qco_compliance(is_code)

            # Entity Match Calculation
            m_entities = g_ctx.get("matching_entities", {})
            prod_match = 1.0 if m_entities.get("product_match") else 0.0
            mat_match = len(m_entities.get("matched_materials", [])) / max(1, len(entities.get("materials", []))) if entities.get("materials") else 0.5
            entity_match_score = (prod_match * 0.6) + (mat_match * 0.4)
            app_match_score = 1.0 if m_entities.get("application_match") else 0.3

            # Hybrid Relevance Score
            rank_result = self.hybrid_ranker.compute_relevance_score(
                vector_sim=vec_sim,
                entity_match_score=entity_match_score,
                graph_rel_score=g_ctx.get("graph_relevance_score", 0.5),
                app_match_score=app_match_score,
                qco_mandatory=qco_eval.get("qco_mandatory", False)
            )

            # Ranking Reasons
            reasons = self._build_ranking_reasons(
                is_code=is_code,
                breakdown=rank_result["score_breakdown"],
                entities=entities,
                m_entities=m_entities,
                qco_eval=qco_eval
            )

            # Evidence Items
            # Evidence Items
            from services.standards_service import is_valid_official_source_url
            import urllib.parse
            raw_ev_url = g_ctx.get("source_provenance", {}).get("source_url")
            standard_search_url = f"https://standards.bis.gov.in/website/know-your-standards?searchTerm={urllib.parse.quote(is_code)}"
            valid_ev_url = raw_ev_url if (raw_ev_url and is_valid_official_source_url(raw_ev_url) and raw_ev_url != "https://standards.bis.gov.in/") else standard_search_url

            evidence_items = [
                {
                    "organization": "Bureau of Indian Standards (BIS)",
                    "document": g_ctx.get("source_provenance", {}).get("source_document", "BIS Standards Portal"),
                    "url": valid_ev_url,
                    "has_verified_url": True,
                    "source": {
                        "authority": "Bureau of Indian Standards (BIS)",
                        "authorityUrl": "https://www.bis.gov.in/",
                        "portalUrl": "https://standards.bis.gov.in/",
                        "specificUrl": valid_ev_url,
                        "verified": True,
                        "sourceType": "official_bis"
                    }
                }
            ]

            # QCO Structure
            qco_struct = {
                "applicable": qco_eval.get("qco_mandatory", False),
                "reference": qco_eval.get("qco_id", "No verified QCO mapping found in the available knowledge base."),
                "requirements": [qco_eval.get("compliance_requirements")] if qco_eval.get("compliance_requirements") else [],
                "source": qco_eval.get("source_evidence")
            }

            # Clauses
            clauses_struct = [
                {"clause_no": c.get("clause_no", "Scope"), "content": c.get("content", "")}
                for c in g_ctx.get("clauses", [])[:3]
            ]

            # Related Standards
            ref_stds = [r["target_is_code"] for r in g_ctx.get("referenced_standards", []) if "target_is_code" in r]

            # Lifecycle and supersession details
            std_detail = standards_service.get_standard_details(is_code)
            lifecycle_status = std_detail.get("lifecycleStatus", "CURRENT / VERIFIED")
            superseded_by = std_detail.get("supersededBy")
            supersedes = std_detail.get("supersedingStandard")
            edition_yr = std_detail.get("publicationYear") or std_detail.get("edition_year") or "Active"
            warning_msg = std_detail.get("warning")

            std_scope = std_detail.get("scope") or g_ctx.get("scope") or ""

            recommendations.append({
                "rank": 0, # Will be set after sorting
                "is_code": is_code,
                "title": g_ctx["title"],
                "scope": std_scope,
                "relevance_score": rank_result["relevance_score"],
                "confidence_level": rank_result["confidence_level"],
                "score_breakdown": rank_result.get("score_breakdown", {}),
                "lifecycle_status": lifecycle_status,
                "superseded_by": superseded_by,
                "supersedes": supersedes,
                "edition_year": edition_yr,
                "superseding_warning": warning_msg,
                "reasons": reasons,
                "qco": qco_struct,
                "evidence": evidence_items,
                "evidence_items": evidence_items,
                "related_standards": ref_stds,
                "relevant_clauses": clauses_struct
            })

        # Sort recommendations by relevance_score descending and set rank
        recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
        final_recs = recommendations[:top_k]

        # Confidence-Gating / Abstain Behavior Check
        gate_res = self.hybrid_ranker.evaluate_confidence_gate(final_recs, entities)
        is_confident = gate_res.get("is_confident", True)
        is_abstained = gate_res.get("abstain", False)

        for i, rec in enumerate(final_recs, start=1):
            rec["rank"] = i
            rec["ranking_reasons"] = rec.get("reasons", [])
            rec["qco_compliance"] = {
                "qco_mandatory": rec.get("qco", {}).get("applicable", False),
                "qco_name": rec.get("qco", {}).get("reference", ""),
                "compliance_requirements": rec.get("qco", {}).get("requirements", [])
            }
            rec["is_definitive"] = is_confident and (i == 1)
            rec["citation_status"] = "PRIMARY_RECOMMENDED" if (is_confident and i == 1) else ("CLOSEST_CANDIDATE" if is_abstained else "RELATED_STANDARD")

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        status_label = "abstain" if is_abstained else "success"
        main_message = gate_res.get("message") if is_abstained else "Grounded Indian Standards recommendations retrieved successfully."

        return {
            "status": status_label,
            "is_confident": is_confident,
            "confidence_gated": is_abstained,
            "abstain_reason": gate_res.get("reason"),
            "message": main_message,
            "query": sanitized_text,
            "entities": entity_summary,
            "recommendations": final_recs,
            "closest_candidates": final_recs if is_abstained else [],
            "warnings": warnings,
            "processing": {
                "retrieval_method": "Graph-RAG + QCO" + (" (Confidence Gated)" if is_abstained else ""),
                "candidate_count": len(recommendations),
                "latency_ms": elapsed_ms,
                "dataset_version": "v0.1-pilot",
                "engine_version": "0.7.0-integrated"
            }
        }

    def _build_ranking_reasons(
        self,
        is_code: str,
        breakdown: Dict[str, Any],
        entities: Dict[str, Any],
        m_entities: Dict[str, Any],
        qco_eval: Dict[str, Any]
    ) -> List[str]:
        reasons = []
        prod = entities.get("product")
        if prod and m_entities.get("product_match"):
            reasons.append(f"Product category matches {prod.lower()}.")

        mats = m_entities.get("matched_materials", [])
        if mats:
            reasons.append(f"Raw material specification matches ({', '.join(mats)}).")

        app = entities.get("application")
        if app and m_entities.get("application_match"):
            reasons.append(f"Application environment matches ({app.lower()}).")

        if breakdown.get("vector_semantic", 0) > 0.15:
            reasons.append("High semantic alignment between procurement text and standard scope.")

        if breakdown.get("graph_relevance", 0) > 0.10:
            reasons.append("Knowledge Graph contains verified normative reference relationships.")

        if qco_eval.get("qco_mandatory"):
            reasons.append(f"Covered under mandatory Quality Control Order ({qco_eval.get('qco_id')}).")

        if not reasons:
            reasons.append("General domain relevance to procurement specification.")

        return reasons


# Global Pipeline Instance
pipeline = IntegrationPipeline()
