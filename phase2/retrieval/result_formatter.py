"""
SIH 26108 — Result Formatter Module
Formats retrieval candidate outputs cleanly and enforces clear demarcation between candidate retrieval, ground truth, and legal verification status.
"""

from typing import Dict, Any, List

LEGAL_DISCLAIMER = (
    "INFORMATIONAL AI CANDIDATE RECOMMENDATION — Search results are candidate recommendations "
    "for technical evaluation and require official human/officer verification. High search rank "
    "does not constitute official BIS certification or legal statutory approval."
)

def format_search_response(raw_output: Dict[str, Any], ground_truth_code: str = None) -> Dict[str, Any]:
    """
    Formats raw retrieval search output into a standardized JSON response structure.
    """
    method = raw_output.get('method', 'unknown')
    query = raw_output.get('query', '')
    results = raw_output.get('results', [])

    formatted_candidates = []
    for r in results:
        is_code = r.get('is_code', '')
        cand = {
            "rank": r.get('rank'),
            "is_code": is_code,
            "title": r.get('title', ''),
            "sector": r.get('sector', ''),
            "product_category": r.get('product_category', ''),
            "relevance_score": r.get('score', r.get('raw_score', r.get('similarity', 0.0))),
            "match_details": {
                "raw_bm25_score": r.get('raw_bm25_score', r.get('raw_score')),
                "raw_semantic_similarity": r.get('raw_semantic_score', r.get('similarity')),
                "normalized_bm25": r.get('normalized_bm25'),
                "normalized_semantic": r.get('normalized_semantic'),
                "matched_terms": r.get('matched_terms', [])
            }
        }
        
        # If ground-truth IS code is provided (during evaluation), mark match status explicitly
        if ground_truth_code:
            cand["is_ground_truth_target"] = (is_code.strip() == ground_truth_code.strip())
            
        formatted_candidates.append(cand)

    return {
        "status": "SUCCESS",
        "query": query,
        "retrieval_method": method,
        "candidate_count": len(formatted_candidates),
        "candidates": formatted_candidates,
        "legal_notice": LEGAL_DISCLAIMER
    }
