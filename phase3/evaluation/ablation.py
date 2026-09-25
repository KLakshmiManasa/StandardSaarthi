"""
SIH 26108 — Phase 3 Ablation Experiment Framework
Evaluates 6 retrieval configurations over the Phase 1 ground-truth dataset:
1. BM25
2. Semantic Search
3. Basic Hybrid (Phase 2)
4. Reciprocal Rank Fusion (RRF)
5. RRF + Cross-Encoder Reranker
6. Full Phase 3 (RRF + Reranker + Structured Metadata)
"""

import os
import csv
from typing import Dict, Any, List
from phase2.retrieval.bm25_search import BM25SearchEngine
from phase2.retrieval.semantic_search import SemanticSearchEngine
from phase2.retrieval.hybrid_search import HybridSearchEngine
from phase3.ranking.rrf import RRFEngine
from phase3.ranking.reranker import CrossEncoderReranker
from phase3.ranking.final_ranker import Phase3FinalRanker
from phase2.evaluation.metrics import precision_at_k, recall_at_k, hit_rate_at_k, reciprocal_rank

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GT_FILE = os.path.join(BASE_DIR, 'data', 'evaluation', 'ground_truth.csv')

def run_ablation_experiments(k: int = 5) -> Dict[str, Any]:
    if not os.path.exists(GT_FILE):
        raise FileNotFoundError(f"Ground truth file not found at {GT_FILE}")

    queries = []
    with open(GT_FILE, 'r', encoding='utf-8') as f:
        queries = list(csv.DictReader(f))

    # Engines
    bm25_eng = BM25SearchEngine()
    sem_eng = SemanticSearchEngine()
    hyb_eng = HybridSearchEngine()
    rrf_eng = RRFEngine()
    reranker = CrossEncoderReranker()
    full_p3_eng = Phase3FinalRanker()

    def get_rrf_plus_reranker_results(query_text: str, top_k: int):
        fused = rrf_eng.search(query_text, top_k=50)['results']
        reranked = reranker.rerank(query_text, fused, rerank_top_n=30)
        return reranked[:top_k]

    configurations = {
        "BM25": lambda q: bm25_eng.search(q, top_k=k)['results'],
        "Semantic": lambda q: sem_eng.search(q, top_k=k)['results'],
        "Basic Hybrid": lambda q: hyb_eng.search(q, top_k=k, alpha=0.5)['results'],
        "RRF": lambda q: rrf_eng.search(q, top_k=k)['results'],
        "RRF + Reranker": lambda q: get_rrf_plus_reranker_results(q, top_k=k),
        "Full Phase 3": lambda q: full_p3_eng.search(q, top_k=k)['results']
    }

    ablation_results = {}

    for config_name, search_fn in configurations.items():
        prec_list, rec_list, hit_list, mrr_list = [], [], [], []
        
        for q in queries:
            q_text = q['procurement_description']
            target = q['target_is_code']
            related = [c.strip() for c in q.get('related_is_codes', '').split(';') if c.strip()]

            res = search_fn(q_text)
            retrieved_codes = [r['is_code'] for r in res]

            prec_list.append(precision_at_k(retrieved_codes, target, related, k))
            rec_list.append(recall_at_k(retrieved_codes, target, related, k))
            hit_list.append(hit_rate_at_k(retrieved_codes, target, k))
            mrr_list.append(reciprocal_rank(retrieved_codes, target))

        n = len(queries)
        ablation_results[config_name] = {
            "precision_at_5": round(sum(prec_list) / n, 4) if n else 0.0,
            "recall_at_5": round(sum(rec_list) / n, 4) if n else 0.0,
            "hit_rate_at_5": round(sum(hit_list) / n, 4) if n else 0.0,
            "mrr": round(sum(mrr_list) / n, 4) if n else 0.0
        }

    return ablation_results


if __name__ == '__main__':
    res = run_ablation_experiments(k=5)
    print("[OK] Ablation Experiment Results (K=5):")
    print(f"{'Method':<20} | {'P@5':<8} | {'R@5':<8} | {'Hit@5':<8} | {'MRR':<8}")
    print("-" * 60)
    for name, metrics in res.items():
        print(f"{name:<20} | {metrics['precision_at_5']:<8} | {metrics['recall_at_5']:<8} | {metrics['hit_rate_at_5']:<8} | {metrics['mrr']:<8}")
