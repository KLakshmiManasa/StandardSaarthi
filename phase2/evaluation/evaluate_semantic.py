"""
SIH 26108 — Standalone Semantic Search Evaluation Module
Runs retrieval evaluation for Semantic Vector method over Phase 1 ground-truth test queries.
"""

import os
import csv
from phase2.retrieval.semantic_search import SemanticSearchEngine
from phase2.evaluation.metrics import precision_at_k, recall_at_k, hit_rate_at_k, reciprocal_rank

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GT_FILE = os.path.join(BASE_DIR, 'data', 'evaluation', 'ground_truth.csv')

def evaluate_semantic(k: int = 5):
    engine = SemanticSearchEngine()
    queries = []
    with open(GT_FILE, 'r', encoding='utf-8') as f:
        queries = list(csv.DictReader(f))

    prec_list, rec_list, hit_list, mrr_list = [], [], [], []

    for q in queries:
        query_text = q['procurement_description']
        target_code = q['target_is_code']
        related = [c.strip() for c in q.get('related_is_codes', '').split(';') if c.strip()]

        res = engine.search(query_text, top_k=k)['results']
        retrieved_codes = [r['is_code'] for r in res]

        prec_list.append(precision_at_k(retrieved_codes, target_code, related, k))
        rec_list.append(recall_at_k(retrieved_codes, target_code, related, k))
        hit_list.append(hit_rate_at_k(retrieved_codes, target_code, k))
        mrr_list.append(reciprocal_rank(retrieved_codes, target_code))

    n = len(queries)
    return {
        "method": "Semantic",
        "query_count": n,
        "k": k,
        "precision_at_k": round(sum(prec_list) / n, 4) if n else 0.0,
        "recall_at_k": round(sum(rec_list) / n, 4) if n else 0.0,
        "hit_rate_at_k": round(sum(hit_list) / n, 4) if n else 0.0,
        "mrr": round(sum(mrr_list) / n, 4) if n else 0.0
    }

if __name__ == '__main__':
    res = evaluate_semantic(k=5)
    print(f"[OK] Semantic Evaluation Results (K=5): {res}")
