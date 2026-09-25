"""
SIH 26108 — Phase 2 Retrieval Evaluation Metrics
Computes Precision@K, Recall@K, Hit Rate@K, and Mean Reciprocal Rank (MRR).
"""

from typing import List, Set

def hit_rate_at_k(retrieved_codes: List[str], target_code: str, k: int) -> float:
    """
    Hit Rate@K: Returns 1.0 if the primary ground-truth target standard is present in top K, else 0.0.
    """
    top_k_retrieved = set([code.strip() for code in retrieved_codes[:k]])
    return 1.0 if target_code.strip() in top_k_retrieved else 0.0

def reciprocal_rank(retrieved_codes: List[str], target_code: str) -> float:
    """
    Reciprocal Rank (RR): 1 / rank of the primary ground-truth target standard in the retrieved list (1-indexed).
    Returns 0.0 if not found.
    """
    target = target_code.strip()
    for rank_idx, code in enumerate(retrieved_codes):
        if code.strip() == target:
            return 1.0 / (rank_idx + 1)
    return 0.0

def precision_at_k(retrieved_codes: List[str], target_code: str, related_codes: List[str], k: int) -> float:
    """
    Precision@K: Fraction of top-K retrieved standards that are ground-truth target or related standards.
    """
    top_k_retrieved = [code.strip() for code in retrieved_codes[:k]]
    ground_truth_set = set([target_code.strip()] + [c.strip() for c in related_codes if c.strip()])
    
    if not top_k_retrieved:
        return 0.0
        
    relevant_retrieved = sum(1 for code in top_k_retrieved if code in ground_truth_set)
    return relevant_retrieved / float(k)

def recall_at_k(retrieved_codes: List[str], target_code: str, related_codes: List[str], k: int) -> float:
    """
    Recall@K: Fraction of total ground-truth target & related standards retrieved in top-K.
    """
    top_k_retrieved = set([code.strip() for code in retrieved_codes[:k]])
    ground_truth_set = set([target_code.strip()] + [c.strip() for c in related_codes if c.strip()])
    
    if not ground_truth_set:
        return 0.0
        
    relevant_retrieved = sum(1 for code in ground_truth_set if code in top_k_retrieved)
    return relevant_retrieved / float(len(ground_truth_set))
