"""
SIH 26108 — Baseline Hybrid Search Engine
Combines normalized BM25 lexical scores and dense semantic similarity scores.
"""

from typing import Dict, Any, Optional, List
from phase2.retrieval.bm25_search import BM25SearchEngine
from phase2.retrieval.semantic_search import SemanticSearchEngine
from phase2.retrieval.dataset_loader import load_standards_dataset

def min_max_normalize(scores: List[float], eps: float = 1e-6) -> List[float]:
    """
    Min-Max normalizes a list of numerical scores into [0.0, 1.0].
    """
    if not scores:
        return []
    min_val = min(scores)
    max_val = max(scores)
    rng = max_val - min_val
    if rng < eps:
        return [1.0 if max_val > 0 else 0.0 for _ in scores]
    return [(s - min_val) / (rng + eps) for s in scores]

class HybridSearchEngine:
    def __init__(self, standards_dataset: Optional[List[Dict[str, Any]]] = None):
        if standards_dataset is None:
            standards_dataset = load_standards_dataset()
        self.standards = standards_dataset
        self.std_lookup = {s['is_code']: s for s in self.standards}
        self.bm25_engine = BM25SearchEngine(self.standards)
        self.semantic_engine = SemanticSearchEngine()

    def search(self, query: str, top_k: int = 10, alpha: float = 0.5, sector_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes baseline hybrid search combining BM25 and Semantic Retrieval.
        
        Args:
            query (str): Procurement description.
            top_k (int): Number of top candidate standards.
            alpha (float): Interpolation parameter (alpha * BM25 + (1-alpha) * Semantic). Default 0.5.
            sector_filter (str, optional): Sector filter.
            
        Returns:
            dict: Structured hybrid search candidate results.
        """
        if not query or not query.strip():
            return {
                "method": "hybrid",
                "alpha": alpha,
                "query": query,
                "results": []
            }

        # Fetch candidate pool from both branches (retrieve top 30 from each branch for candidate fusion)
        candidate_k = max(top_k * 3, 30)
        bm25_res = self.bm25_engine.search(query, top_k=candidate_k, sector_filter=sector_filter)['results']
        semantic_res = self.semantic_engine.search(query, top_k=candidate_k, sector_filter=sector_filter)['results']

        # Map candidate scores by IS code
        candidate_codes = set([r['is_code'] for r in bm25_res] + [r['is_code'] for r in semantic_res])
        
        bm25_dict = {r['is_code']: r['raw_score'] for r in bm25_res}
        semantic_dict = {r['is_code']: r['similarity'] for r in semantic_res}

        if not candidate_codes:
            return {
                "method": "hybrid",
                "alpha": alpha,
                "query": query,
                "results": []
            }

        codes_list = list(candidate_codes)
        raw_bm25 = [bm25_dict.get(c, 0.0) for c in codes_list]
        raw_semantic = [semantic_dict.get(c, 0.0) for c in codes_list]

        norm_bm25 = min_max_normalize(raw_bm25)
        norm_semantic = min_max_normalize(raw_semantic)

        fused_candidates = []
        for i, code in enumerate(codes_list):
            s_bm25_norm = norm_bm25[i]
            s_sem_norm = norm_semantic[i]
            
            hybrid_score = alpha * s_bm25_norm + (1.0 - alpha) * s_sem_norm
            
            std = self.std_lookup.get(code, {})
            fused_candidates.append({
                "is_code": code,
                "title": std.get('title', ''),
                "sector": std.get('sector', ''),
                "product_category": std.get('product_category', ''),
                "score": round(hybrid_score, 4),
                "raw_bm25_score": round(raw_bm25[i], 4),
                "raw_semantic_score": round(raw_semantic[i], 4),
                "normalized_bm25": round(s_bm25_norm, 4),
                "normalized_semantic": round(s_sem_norm, 4)
            })

        # Sort candidates descending by hybrid score
        fused_candidates.sort(key=lambda x: x['score'], reverse=True)

        # Deduplicate & rank Top K
        results = []
        seen = set()
        rank = 1
        for cand in fused_candidates:
            if cand['is_code'] in seen:
                continue
            seen.add(cand['is_code'])
            cand['rank'] = rank
            results.append(cand)
            rank += 1
            if len(results) >= top_k:
                break

        return {
            "method": "hybrid",
            "alpha": alpha,
            "query": query,
            "results": results
        }

if __name__ == '__main__':
    engine = HybridSearchEngine()
    test_query = "Supply of PVC insulated copper electrical cables suitable for internal wiring of a government hospital."
    res = engine.search(test_query, top_k=5, alpha=0.5)
    print("[OK] Hybrid Search Results:")
    for r in res['results']:
        print(f"Rank {r['rank']}: {r['is_code']} | Hybrid Score: {r['score']} | BM25 Norm: {r['normalized_bm25']} | Sem Norm: {r['normalized_semantic']} | {r['title'][:50]}...")
