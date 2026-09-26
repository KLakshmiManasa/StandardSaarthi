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

    def evaluate_confidence_gate(
        self,
        recommendations: List[Dict[str, Any]],
        entities: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Confidence Gating / Abstain Evaluation:
        If no standard clearly matches with sufficient certainty, the system abstains from forcing
        a top-1 recommendation to protect government procurement against wrong-citation risk.
        Instead, it flags 'not confident enough' and surfaces closest candidates for officer discretion.
        """
        gate_cfg = self.config.get("confidence_gating", {})
        if not gate_cfg.get("enabled", True):
            return {"is_confident": True, "abstain": False, "reason": None}

        if not recommendations:
            return {
                "is_confident": False,
                "abstain": True,
                "reason": "No candidate standards found in database.",
                "message": "Not confident enough: No standards found matching the query."
            }

        top_rec = recommendations[0]
        top_score = top_rec.get("relevance_score", 0.0)
        top_conf = top_rec.get("confidence_level", "LOW")
        min_thresh = gate_cfg.get("min_relevance_threshold", 0.50)

        # 1. Top score below minimum confident citation threshold or LOW confidence
        if top_score < min_thresh or (gate_cfg.get("low_confidence_abstain", True) and top_conf == "LOW"):
            return {
                "is_confident": False,
                "abstain": True,
                "threshold": min_thresh,
                "top_score": top_score,
                "reason": f"Top candidate relevance score ({top_score*100:.1f}%) is below confident citation threshold ({min_thresh*100:.1f}%).",
                "message": "Not confident enough: No standard clearly matches this procurement description. Displaying closest candidates for officer verification instead of forcing a citation."
            }

        # 2. Borderline top score with ambiguous margin between top 1 and top 2
        borderline_thresh = gate_cfg.get("borderline_threshold", 0.55)
        margin_thresh = gate_cfg.get("margin_threshold", 0.03)
        if len(recommendations) > 1 and top_score < borderline_thresh:
            second_score = recommendations[1].get("relevance_score", 0.0)
            score_diff = top_score - second_score
            has_product_match = any("Product category matches" in r for r in top_rec.get("reasons", []))
            if score_diff < margin_thresh and not has_product_match:
                return {
                    "is_confident": False,
                    "abstain": True,
                    "threshold": borderline_thresh,
                    "top_score": top_score,
                    "margin": score_diff,
                    "reason": f"Borderline score ({top_score*100:.1f}%) with ambiguous margin ({score_diff*100:.1f}%) between top candidates.",
                    "message": "Not confident enough: Competing candidate standards show comparable relevance without a decisive differentiator. Displaying closest candidates for officer review."
                }

        return {
            "is_confident": True,
            "abstain": False,
            "threshold": min_thresh,
            "top_score": top_score,
            "reason": None,
            "message": "High-confidence standard match identified."
        }



if __name__ == '__main__':
    ranker = HybridRanker()
    sc = ranker.compute_relevance_score(0.85, 0.90, 0.80, 0.75, True)
    print(f"[OK] Computed Relevance Score: {sc['relevance_score']} ({sc['confidence_level']})")
    print(f"     Breakdown: {sc['score_breakdown']}")
