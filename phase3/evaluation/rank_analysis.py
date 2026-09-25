"""
SIH 26108 — Phase 3 Rank Movement & Difficulty Analysis Module
Measures rank shifts (before vs after Phase 3) and evaluates query performance across difficulty levels (EASY, MEDIUM, HARD).
"""

import os
import csv
import statistics
from typing import Dict, Any, List
from phase2.retrieval.hybrid_search import HybridSearchEngine
from phase3.ranking.final_ranker import Phase3FinalRanker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GT_FILE = os.path.join(BASE_DIR, 'data', 'evaluation', 'ground_truth.csv')

def find_target_rank(results: List[dict], target_code: str) -> int:
    target = target_code.strip()
    for item in results:
        if item['is_code'].strip() == target:
            return item['rank']
    return 999  # Large penalty rank if not found in top candidate pool

def run_rank_analysis() -> Dict[str, Any]:
    if not os.path.exists(GT_FILE):
        raise FileNotFoundError(f"Ground truth dataset not found at {GT_FILE}")

    queries = []
    with open(GT_FILE, 'r', encoding='utf-8') as f:
        queries = list(csv.DictReader(f))

    p2_engine = HybridSearchEngine()
    p3_engine = Phase3FinalRanker()

    ranks_p2 = []
    ranks_p3 = []
    
    improved_count = 0
    unchanged_count = 0
    degraded_count = 0
    
    query_rank_details = []

    # Difficulty tracking
    diff_metrics = {
        "EASY": {"p2_ranks": [], "p3_ranks": [], "p3_hits_5": [], "p3_mrrs": []},
        "MEDIUM": {"p2_ranks": [], "p3_ranks": [], "p3_hits_5": [], "p3_mrrs": []},
        "HARD": {"p2_ranks": [], "p3_ranks": [], "p3_hits_5": [], "p3_mrrs": []}
    }

    for q in queries:
        q_id = q['query_id']
        q_text = q['procurement_description']
        target = q['target_is_code']
        difficulty = q.get('difficulty', 'MEDIUM').upper()
        if difficulty not in diff_metrics:
            difficulty = 'MEDIUM'

        # Retrieve top 20 candidates for rank analysis
        p2_res = p2_engine.search(q_text, top_k=20, alpha=0.5)['results']
        p3_res = p3_engine.search(q_text, top_k=20)['results']

        rank_p2 = find_target_rank(p2_res, target)
        rank_p3 = find_target_rank(p3_res, target)

        ranks_p2.append(rank_p2)
        ranks_p3.append(rank_p3)

        shift = rank_p2 - rank_p3  # Positive shift means rank improved (e.g. from rank 3 to rank 1)
        if shift > 0:
            improved_count += 1
            status = "IMPROVED"
        elif shift < 0:
            degraded_count += 1
            status = "DEGRADED"
        else:
            unchanged_count += 1
            status = "UNCHANGED"

        query_rank_details.append({
            "query_id": q_id,
            "query": q_text,
            "target_is_code": target,
            "difficulty": difficulty,
            "rank_before_phase2": rank_p2,
            "rank_after_phase3": rank_p3,
            "rank_shift": shift,
            "status": status
        })

        # Record difficulty metrics
        diff_metrics[difficulty]["p2_ranks"].append(rank_p2)
        diff_metrics[difficulty]["p3_ranks"].append(rank_p3)
        diff_metrics[difficulty]["p3_hits_5"].append(1.0 if rank_p3 <= 5 else 0.0)
        diff_metrics[difficulty]["p3_mrrs"].append(1.0 / rank_p3 if rank_p3 <= 20 else 0.0)

    n = len(queries)
    avg_rank_p2 = round(sum(ranks_p2) / n, 2) if n else 0.0
    avg_rank_p3 = round(sum(ranks_p3) / n, 2) if n else 0.0
    med_rank_p2 = statistics.median(ranks_p2) if n else 0
    med_rank_p3 = statistics.median(ranks_p3) if n else 0

    difficulty_summary = {}
    for diff, data in diff_metrics.items():
        cnt = len(data["p3_ranks"])
        if cnt > 0:
            difficulty_summary[diff] = {
                "query_count": cnt,
                "avg_rank_before": round(sum(data["p2_ranks"]) / cnt, 2),
                "avg_rank_after": round(sum(data["p3_ranks"]) / cnt, 2),
                "hit_rate_at_5": round(sum(data["p3_hits_5"]) / cnt, 4),
                "mrr": round(sum(data["p3_mrrs"]) / cnt, 4)
            }

    return {
        "total_queries": n,
        "improved_count": improved_count,
        "unchanged_count": unchanged_count,
        "degraded_count": degraded_count,
        "improved_pct": round((improved_count / n) * 100, 1) if n else 0.0,
        "unchanged_pct": round((unchanged_count / n) * 100, 1) if n else 0.0,
        "degraded_pct": round((degraded_count / n) * 100, 1) if n else 0.0,
        "avg_rank_before_phase2": avg_rank_p2,
        "avg_rank_after_phase3": avg_rank_p3,
        "median_rank_before_phase2": med_rank_p2,
        "median_rank_after_phase3": med_rank_p3,
        "difficulty_summary": difficulty_summary,
        "query_rank_details": query_rank_details
    }


if __name__ == '__main__':
    res = run_rank_analysis()
    print("\n================ RANK MOVEMENT ANALYSIS ================")
    print(f"Total Queries Evaluated: {res['total_queries']}")
    print(f"  - Improved Rank: {res['improved_count']} ({res['improved_pct']}%)")
    print(f"  - Unchanged Rank: {res['unchanged_count']} ({res['unchanged_pct']}%)")
    print(f"  - Degraded Rank: {res['degraded_count']} ({res['degraded_pct']}%)")
    print(f"Average Target Rank: {res['avg_rank_before_phase2']} (Phase 2) -> {res['avg_rank_after_phase3']} (Phase 3)")
    print("\nDifficulty Level Performance:")
    for diff, metrics in res['difficulty_summary'].items():
        print(f"  - {diff} (n={metrics['query_count']}): Avg Rank {metrics['avg_rank_before']} -> {metrics['avg_rank_after']} | Hit@5: {metrics['hit_rate_at_5']*100:.1f}% | MRR: {metrics['mrr']}")
    print("========================================================\n")
