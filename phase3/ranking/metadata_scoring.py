"""
SIH 26108 — Structured Metadata Scoring Engine
Calculates interpretable metadata alignment scores between query entity slots and standard fields.
"""

import re
from typing import Dict, Any, List, Optional
from phase2.retrieval.dataset_loader import load_standards_dataset

DEFAULT_WEIGHTS = {
    "sector": 0.10,
    "product_category": 0.30,
    "material": 0.20,
    "application": 0.25,
    "technical_parameters": 0.15
}

def tokenize_text(text: str) -> set:
    if not text:
        return set()
    cleaned = re.sub(r'[^a-z0-9]', ' ', str(text).lower())
    return set(cleaned.split())

class MetadataScorer:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights if weights is not None else DEFAULT_WEIGHTS
        # Normalize weights to sum to 1.0
        total_w = sum(self.weights.values())
        if abs(total_w - 1.0) > 1e-4 and total_w > 0:
            self.weights = {k: v / total_w for k, v in self.weights.items()}
            
        self.standards_map = {s['is_code']: s for s in load_standards_dataset()}

    def score_candidate(self, query: str, candidate_code: str, query_sector: Optional[str] = None) -> Dict[str, Any]:
        """
        Computes metadata alignment score for a single candidate standard.
        """
        std = self.standards_map.get(candidate_code, {})
        query_tokens = tokenize_text(query)
        
        matched_fields = []
        
        # 1. Sector match (Binary or explicit query match)
        std_sector = std.get('sector', '')
        if query_sector:
            sector_score = 1.0 if std_sector.lower() == query_sector.lower() else 0.0
        else:
            sector_tokens = tokenize_text(std_sector)
            sector_score = 1.0 if (query_tokens & sector_tokens) else 0.5
            
        if sector_score > 0.5:
            matched_fields.append("sector")

        # 2. Product Category match
        prod_tokens = tokenize_text(std.get('product_category', ''))
        prod_overlap = len(query_tokens & prod_tokens)
        prod_score = min(1.0, prod_overlap / max(1, len(prod_tokens))) if prod_tokens else 0.0
        if prod_overlap > 0:
            matched_fields.append("product_category")

        # 3. Material match
        mat_tokens = tokenize_text(std.get('materials', ''))
        mat_overlap = len(query_tokens & mat_tokens)
        mat_score = min(1.0, mat_overlap / max(1, len(mat_tokens))) if mat_tokens else 0.0
        if mat_overlap > 0:
            matched_fields.append("material")

        # 4. Application match
        app_tokens = tokenize_text(std.get('applications', ''))
        app_overlap = len(query_tokens & app_tokens)
        app_score = min(1.0, app_overlap / max(1, len(app_tokens))) if app_tokens else 0.0
        if app_overlap > 0:
            matched_fields.append("application")

        # 5. Technical Parameters match
        tech_tokens = tokenize_text(std.get('technical_parameters', ''))
        tech_overlap = len(query_tokens & tech_tokens)
        tech_score = min(1.0, tech_overlap / max(1, len(tech_tokens))) if tech_tokens else 0.0
        if tech_overlap > 0:
            matched_fields.append("technical_parameters")

        metadata_score = (
            self.weights['sector'] * sector_score +
            self.weights['product_category'] * prod_score +
            self.weights['material'] * mat_score +
            self.weights['application'] * app_score +
            self.weights['technical_parameters'] * tech_score
        )

        return {
            "metadata_score": round(metadata_score, 4),
            "matched_fields": matched_fields,
            "sub_scores": {
                "sector": round(sector_score, 2),
                "product_category": round(prod_score, 2),
                "material": round(mat_score, 2),
                "application": round(app_score, 2),
                "technical_parameters": round(tech_score, 2)
            }
        }


if __name__ == '__main__':
    scorer = MetadataScorer()
    res = scorer.score_candidate("Supply of PVC insulated copper electrical cables for hospital internal wiring", "IS 694")
    print(f"[OK] Metadata Score Test for IS 694: {res}")
