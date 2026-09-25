"""
SIH 26108 — Phase 5/6 Configurable Hybrid Ranking & Recommendation Engine
Computes transparent relevance scores by combining semantic similarity, entity overlap, graph relevance,
application match, and QCO regulatory presence using weights loaded from config/phase5_config.yaml.
"""

import os
import yaml
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'phase5_config.yaml')

class HybridRanker:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config = self._load_config(config_path)
        self.weights = self.config.get("ranking_weights", {
            "vector_semantic": 0.45,
            "entity_match": 0.30,
            "graph_relevance": 0.15,
            "application_match": 0.10,
            "qco_regulatory": 0.00
        })
        self.thresholds = self.config.get("relevance_thresholds", {
            "high_confidence": 0.70,
            "medium_confidence": 0.45,
            "minimum_cutoff": 0.20
        })

    def _load_config(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def compute_relevance_score(
        self,
        vector_sim: float,
        entity_match_score: float,
        graph_rel_score: float,
        app_match_score: float,
        qco_mandatory: bool
    ) -> Dict[str, Any]:
        """
        Computes weighted recommendation relevance score and decision breakdown.
        """
        w_vec = self.weights.get("vector_semantic", 0.45)
        w_ent = self.weights.get("entity_match", 0.30)
        w_graph = self.weights.get("graph_relevance", 0.15)
        w_app = self.weights.get("application_match", 0.10)
        w_qco = self.weights.get("qco_regulatory", 0.00)

        qco_score = 1.0 if qco_mandatory else 0.0

        raw_score = (
            w_vec * vector_sim +
            w_ent * entity_match_score +
            w_graph * graph_rel_score +
            w_app * app_match_score +
            w_qco * qco_score
        )

        relevance_score = min(1.0, round(raw_score, 4))

        confidence = "LOW"
        if relevance_score >= self.thresholds.get("high_confidence", 0.70):
            confidence = "HIGH"
        elif relevance_score >= self.thresholds.get("medium_confidence", 0.45):
            confidence = "MEDIUM"

        return {
            "relevance_score": relevance_score,
            "confidence_level": confidence,
            "score_breakdown": {
                "vector_semantic": round(w_vec * vector_sim, 4),
                "entity_match": round(w_ent * entity_match_score, 4),
                "graph_relevance": round(w_graph * graph_rel_score, 4),
                "application_match": round(w_app * app_match_score, 4),
                "qco_regulatory": round(w_qco * qco_score, 4)
            }
        }

    def generate_explanation(self, is_code: str, title: str, breakdown: Dict[str, Any], entities: Dict[str, Any], qco_info: Dict[str, Any]) -> str:
        """
        Generates human-readable, transparent explanation for why this standard was recommended.
        """
        reasons = []
        if breakdown.get("vector_semantic", 0) > 0.15:
            reasons.append("High semantic alignment between procurement specification text and standard scope.")
        if entities.get("product_match"):
            reasons.append(f"Direct match on product specifications for '{entities.get('matched_product', 'required item')}'.")
        if entities.get("matched_materials"):
            mats_str = ", ".join(entities.get("matched_materials", []))
            reasons.append(f"Material specification match ({mats_str}).")
        if breakdown.get("graph_relevance", 0) > 0.10:
            reasons.append("Strong Knowledge Graph connectivity (normative references, test procedure clauses).")
        if qco_info.get("qco_mandatory"):
            reasons.append(f"Mandatory QCO compliance requirement ({qco_info.get('qco_id')}).")

        if not reasons:
            reasons.append("General semantic relevance to procurement description domain.")

        return " ".join(reasons)


if __name__ == '__main__':
    ranker = HybridRanker()
    sc = ranker.compute_relevance_score(0.85, 0.90, 0.80, 0.75, True)
    print(f"[OK] Computed Relevance Score: {sc['relevance_score']} ({sc['confidence_level']})")
    print(f"     Breakdown: {sc['score_breakdown']}")
