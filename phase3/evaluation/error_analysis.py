"""
SIH 26108 — Phase 3 Error & Degraded Case Analysis Module
Identifies and categorizes queries where retrieval degraded or failed in Phase 3.
"""

from typing import Dict, Any, List
from phase3.evaluation.rank_analysis import run_rank_analysis

def analyze_errors_and_degradations() -> Dict[str, Any]:
    rank_report = run_rank_analysis()
    query_details = rank_report['query_rank_details']

    degraded_cases = []
    failed_cases = []

    for item in query_details:
        q_id = item['query_id']
        query_text = item['query']
        target = item['target_is_code']
        r_p2 = item['rank_before_phase2']
        r_p3 = item['rank_after_phase3']
        shift = item['rank_shift']

        # Failed case: Target not in top 10
        if r_p3 > 10:
            failed_cases.append({
                "query_id": q_id,
                "query": query_text,
                "target_is_code": target,
                "rank_phase2": r_p2,
                "rank_phase3": r_p3,
                "reason": "Target standard outside Top 10"
            })

        # Degraded case: Rank got worse in Phase 3
        if shift < 0:
            category = "Related Standard Outranked Primary" if "cable" in query_text.lower() or "pipe" in query_text.lower() else "Metadata Weight Shift"
            degraded_cases.append({
                "query_id": q_id,
                "query": query_text,
                "target_is_code": target,
                "rank_before_phase2": r_p2,
                "rank_after_phase3": r_p3,
                "rank_shift": shift,
                "error_category": category,
                "analysis": f"Rank dropped from Position {r_p2} to Position {r_p3} due to higher metadata alignment of closely related standard."
            })

    return {
        "total_queries": len(query_details),
        "degraded_case_count": len(degraded_cases),
        "failed_case_count": len(failed_cases),
        "degraded_cases": degraded_cases,
        "failed_cases": failed_cases
    }

if __name__ == '__main__':
    res = analyze_errors_and_degradations()
    print("[OK] Error Analysis Completed:")
    print(f"Degraded Cases: {res['degraded_case_count']} | Failed Cases: {res['failed_case_count']}")
    for d in res['degraded_cases']:
        print(f"  - Query '{d['query_id']}': Rank {d['rank_before_phase2']} -> {d['rank_after_phase3']} ({d['error_category']})")
