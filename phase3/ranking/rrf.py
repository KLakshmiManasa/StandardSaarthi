"""
SIH 26108 — Reciprocal Rank Fusion (RRF) Engine
Merges lexical (BM25) and dense semantic candidate rankings using RRF scoring formula.
"""

from typing import List, Dict, Any, Optional
from phase2.retrieval.bm25_search import BM25SearchEngine
from phase2.retrieval.semantic_search import SemanticSearchEngine

def reciprocal_rank_fusion(
    bm25_results: List[Dict[str, Any]],
    semantic_results: List[Dict[str, Any]],
    rrf_k: int = 60,
    candidate_limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Computes Reciprocal Rank Fusion (RRF) scores over BM25 and Semantic candidate lists.
    
    RRF_score(d) = sum( 1 / (rrf_k + rank(d)) )
    
    Args:
        bm25_results (list): Ranked list of candidates from BM25 search.
        semantic_results (list): Ranked list of candidates from Semantic search.
        rrf_k (int): Smoothing constant (default 60).
        candidate_limit (int): Max candidate pool size (default 100).
        
    Returns:
        list: Fused candidate list sorted by descending RRF score.
    """
    rrf_scores = {}
    bm25_ranks = {}
    semantic_ranks = {}
    metadata = {}

    # Process BM25 ranks
    for r in bm25_results:
        code = r['is_code']
        rank = r['rank']
        bm25_ranks[code] = rank
        rrf_scores[code] = rrf_scores.get(code, 0.0) + (1.0 / (rrf_k + rank))
        if code not in metadata:
            metadata[code] = r

    # Process Semantic ranks
    for r in semantic_results:
        code = r['is_code']
        rank = r['rank']
        semantic_ranks[code] = rank
        rrf_scores[code] = rrf_scores.get(code, 0.0) + (1.0 / (rrf_k + rank))
        if code not in metadata:
            metadata[code] = r

    # Format fused candidates
    fused = []
    for code, score in rrf_scores.items():
        meta = metadata[code]
        fused.append({
            "is_code": code,
            "title": meta.get('title', ''),
            "sector": meta.get('sector', ''),
            "product_category": meta.get('product_category', ''),
            "bm25_rank": bm25_ranks.get(code, 999),
            "semantic_rank": semantic_ranks.get(code, 999),
            "rrf_score": round(score, 6)
        })

    # Sort descending by RRF score
    fused.sort(key=lambda x: x['rrf_score'], reverse=True)
    
    # Assign fused RRF ranks
    for idx, item in enumerate(fused):
        item['rrf_rank'] = idx + 1

    return fused[:candidate_limit]


class RRFEngine:
    def __init__(self, bm25_top_n: int = 50, semantic_top_n: int = 50, rrf_k: int = 60):
        self.bm25_top_n = bm25_top_n
        self.semantic_top_n = semantic_top_n
        self.rrf_k = rrf_k
        self.bm25_search = BM25SearchEngine()
        self.semantic_search = SemanticSearchEngine()

    def search(self, query: str, top_k: int = 10, sector_filter: Optional[str] = None) -> Dict[str, Any]:
        if not query or not query.strip():
            return {"method": "rrf", "rrf_k": self.rrf_k, "query": query, "results": []}

        bm25_res = self.bm25_search.search(query, top_k=self.bm25_top_n, sector_filter=sector_filter)['results']
        semantic_res = self.semantic_search.search(query, top_k=self.semantic_top_n, sector_filter=sector_filter)['results']

        fused = reciprocal_rank_fusion(bm25_res, semantic_res, rrf_k=self.rrf_k, candidate_limit=top_k)

        # Standardize result field name
        for item in fused:
            item['score'] = item['rrf_score']
            item['rank'] = item['rrf_rank']

        return {
            "method": "rrf",
            "rrf_k": self.rrf_k,
            "query": query,
            "results": fused
        }


if __name__ == '__main__':
    rrf_engine = RRFEngine()
    test_query = "Supply of PVC insulated copper electrical cables for hospital internal wiring"
    res = rrf_engine.search(test_query, top_k=5)
    print("[OK] RRF Search Test:")
    for r in res['results']:
        print(f"Rank {r['rank']}: {r['is_code']} | RRF Score: {r['rrf_score']} | BM25 Rank: {r['bm25_rank']} | Sem Rank: {r['semantic_rank']}")
