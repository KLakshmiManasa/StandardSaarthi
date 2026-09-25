"""
SIH 26108 — Final Phase 3 Multi-Factor Ranking Engine
Combines Cross-Encoder Reranker scores, normalized RRF scores, and structured Metadata scores.
"""

import os
import time
import yaml
from typing import Dict, Any, Optional, List
from phase2.retrieval.bm25_search import BM25SearchEngine
from phase2.retrieval.semantic_search import SemanticSearchEngine
from phase2.retrieval.hybrid_search import min_max_normalize
from phase3.ranking.rrf import reciprocal_rank_fusion
from phase3.ranking.reranker import CrossEncoderReranker
from phase3.ranking.metadata_scoring import MetadataScorer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'phase3_config.yaml')

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

class Phase3FinalRanker:
    def __init__(self, config_dict: Optional[dict] = None):
        if config_dict is None:
            config_dict = load_config()

        ret_cfg = config_dict.get('retrieval', {})
        self.bm25_top_n = ret_cfg.get('bm25_top_n', 50)
        self.semantic_top_n = ret_cfg.get('semantic_top_n', 50)
        self.rrf_k = ret_cfg.get('rrf_k', 60)
        self.candidate_limit = ret_cfg.get('candidate_pool_limit', 100)

        rerank_cfg = config_dict.get('reranker', {})
        self.rerank_top_n = rerank_cfg.get('rerank_top_n', 30)

        meta_weights = config_dict.get('metadata_weights', {})
        self.metadata_scorer = MetadataScorer(meta_weights)

        final_weights = config_dict.get('final_ranking_weights', {})
        self.alpha = final_weights.get('alpha_reranker', 0.60)
        self.beta = final_weights.get('beta_rrf_norm', 0.25)
        self.gamma = final_weights.get('gamma_metadata', 0.15)

        # Ensure weights sum to 1.0
        tot_w = self.alpha + self.beta + self.gamma
        if abs(tot_w - 1.0) > 1e-4 and tot_w > 0:
            self.alpha /= tot_w
            self.beta /= tot_w
            self.gamma /= tot_w

        rel_thresh = config_dict.get('relevance_thresholds', {})
        self.high_thresh = rel_thresh.get('high_relevance', 0.70)
        self.med_thresh = rel_thresh.get('medium_relevance', 0.45)

        # Engines
        self.bm25_engine = BM25SearchEngine()
        self.semantic_engine = SemanticSearchEngine()
        self.reranker = CrossEncoderReranker()

    def search(self, query: str, top_k: int = 10, sector_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes complete Phase 3 search pipeline and measures component latencies.
        """
        start_time = time.time()
        
        if not query or not query.strip():
            return {
                "method": "phase3",
                "query": query,
                "results": [],
                "latency_ms": 0.0
            }

        # Step 1 & 2: BM25 and Semantic Retrieval
        t0 = time.time()
        bm25_res = self.bm25_engine.search(query, top_k=self.bm25_top_n, sector_filter=sector_filter)['results']
        t1 = time.time()
        semantic_res = self.semantic_engine.search(query, top_k=self.semantic_top_n, sector_filter=sector_filter)['results']
        t2 = time.time()

        # Step 3: Reciprocal Rank Fusion
        fused_candidates = reciprocal_rank_fusion(
            bm25_res, semantic_res, rrf_k=self.rrf_k, candidate_limit=self.candidate_limit
        )
        t3 = time.time()

        if not fused_candidates:
            return {
                "method": "phase3",
                "query": query,
                "results": [],
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }

        # Step 4: Cross-Encoder Reranking
        reranked_candidates = self.reranker.rerank(query, fused_candidates, rerank_top_n=self.rerank_top_n)
        t4 = time.time()

        # Step 5: Score Normalization & Metadata-Aware Scoring
        rrf_raw_scores = [c.get('rrf_score', 0.0) for c in reranked_candidates]
        rrf_norm_scores = min_max_normalize(rrf_raw_scores)

        final_candidates = []
        for idx, cand in enumerate(reranked_candidates):
            c_code = cand['is_code']
            rrf_norm = rrf_norm_scores[idx]
            
            # Cross-encoder score (default to rrf_norm if not set)
            reranker_sc = cand.get('reranker_score', rrf_norm)
            
            # Metadata score
            meta_res = self.metadata_scorer.score_candidate(query, c_code, query_sector=sector_filter)
            meta_sc = meta_res['metadata_score']
            matched_fields = meta_res['matched_fields']

            # Multi-factor final score
            final_score = (self.alpha * reranker_sc) + (self.beta * rrf_norm) + (self.gamma * meta_sc)
            
            # Assign relevance category
            if final_score >= self.high_thresh:
                relevance_category = "HIGH_RELEVANCE"
            elif final_score >= self.med_thresh:
                relevance_category = "MEDIUM_RELEVANCE"
            else:
                relevance_category = "LOWER_RELEVANCE"

            final_candidates.append({
                "is_code": c_code,
                "title": cand.get('title', ''),
                "sector": cand.get('sector', ''),
                "product_category": cand.get('product_category', ''),
                "score": round(final_score, 4),
                "reranker_score": round(reranker_sc, 4),
                "rrf_score": round(cand.get('rrf_score', 0.0), 6),
                "normalized_rrf_score": round(rrf_norm, 4),
                "metadata_score": round(meta_sc, 4),
                "relevance_category": relevance_category,
                "matched_fields": matched_fields,
                "bm25_rank": cand.get('bm25_rank'),
                "semantic_rank": cand.get('semantic_rank'),
                "rrf_rank": cand.get('rrf_rank')
            })

        t5 = time.time()

        # Sort descending by final score
        final_candidates.sort(key=lambda x: x['score'], reverse=True)

        # Deduplicate & rank top K
        results = []
        seen = set()
        rank = 1
        for cand in final_candidates:
            if cand['is_code'] in seen:
                continue
            seen.add(cand['is_code'])
            cand['rank'] = rank
            results.append(cand)
            rank += 1
            if len(results) >= top_k:
                break

        total_latency = (time.time() - start_time) * 1000.0

        return {
            "method": "phase3",
            "query": query,
            "weights": {
                "alpha_reranker": self.alpha,
                "beta_rrf": self.beta,
                "gamma_metadata": self.gamma
            },
            "results": results,
            "latencies_ms": {
                "bm25": round((t1 - t0) * 1000, 2),
                "semantic": round((t2 - t1) * 1000, 2),
                "rrf": round((t3 - t2) * 1000, 2),
                "reranker": round((t4 - t3) * 1000, 2),
                "metadata": round((t5 - t4) * 1000, 2),
                "total": round(total_latency, 2)
            }
        }


if __name__ == '__main__':
    ranker = Phase3FinalRanker()
    test_q = "Supply of PVC insulated copper electrical cables suitable for internal wiring of a government hospital."
    res = ranker.search(test_q, top_k=5)
    print(f"[OK] Phase 3 Final Search Results (Total Latency: {res['latencies_ms']['total']} ms):")
    for r in res['results']:
        print(f"Rank {r['rank']}: {r['is_code']} | Final: {r['score']} | Reranker: {r['reranker_score']} | Meta: {r['metadata_score']} | Category: {r['relevance_category']}")
