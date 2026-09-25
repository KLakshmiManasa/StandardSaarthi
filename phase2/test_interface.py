"""
SIH 26108 — Extended Developer CLI Test Interface (Phase 2 & Phase 3)
Allows testing procurement descriptions across BM25, Semantic, Hybrid, RRF, and Phase 3 Advanced Ranking.
"""

import argparse
from phase2.retrieval.bm25_search import BM25SearchEngine
from phase2.retrieval.semantic_search import SemanticSearchEngine
from phase2.retrieval.hybrid_search import HybridSearchEngine
from phase3.ranking.rrf import RRFEngine
from phase3.ranking.final_ranker import Phase3FinalRanker
from phase2.retrieval.result_formatter import format_search_response

def run_tester():
    parser = argparse.ArgumentParser(description="SIH 26108 Search Engine Developer Tester")
    parser.add_argument("--query", "-q", type=str, default="Supply of PVC insulated copper electrical cables for internal building wiring", help="Procurement query text")
    parser.add_argument("--method", "-m", type=str, default="phase3", choices=["bm25", "semantic", "hybrid", "rrf", "phase3"], help="Search method")
    parser.add_argument("--top_k", "-k", type=int, default=10, help="Number of candidate standards to retrieve")
    parser.add_argument("--alpha", "-a", type=float, default=0.5, help="Hybrid alpha parameter (for baseline hybrid)")
    parser.add_argument("--sector", "-s", type=str, default=None, help="Sector filter ('Electrical' or 'Civil')")

    args = parser.parse_args()

    print("=========================================================================")
    print("      SIH 26108 — DEVELOPER TEST INTERFACE (PHASE 3 ADVANCED RANKING)    ")
    print("=========================================================================")
    print(f"Query  : \"{args.query}\"")
    print(f"Method : {args.method.upper()} | Top K: {args.top_k} | Sector Filter: {args.sector}")
    print("=========================================================================\n")

    if args.method == "bm25":
        engine = BM25SearchEngine()
        raw_res = engine.search(args.query, top_k=args.top_k, sector_filter=args.sector)
    elif args.method == "semantic":
        engine = SemanticSearchEngine()
        raw_res = engine.search(args.query, top_k=args.top_k, sector_filter=args.sector)
    elif args.method == "hybrid":
        engine = HybridSearchEngine()
        raw_res = engine.search(args.query, top_k=args.top_k, alpha=args.alpha, sector_filter=args.sector)
    elif args.method == "rrf":
        engine = RRFEngine()
        raw_res = engine.search(args.query, top_k=args.top_k, sector_filter=args.sector)
    else:
        engine = Phase3FinalRanker()
        raw_res = engine.search(args.query, top_k=args.top_k, sector_filter=args.sector)

    formatted = format_search_response(raw_res)

    print(f"Retrieved {formatted['candidate_count']} Candidate Standards:\n")
    print(f"{'RANK':<5} | {'IS CODE':<15} | {'SCORE':<8} | {'SECTOR':<12} | {'TITLE'}")
    print("-" * 80)
    for c in formatted['candidates']:
        score_val = f"{c['relevance_score']:.4f}"
        title_trunc = c['title'][:45] + "..." if len(c['title']) > 45 else c['title']
        print(f"{c['rank']:<5} | {c['is_code']:<15} | {score_val:<8} | {c['sector']:<12} | {title_trunc}")
    print("-" * 80)
    print(f"\nLegal Disclaimer:\n{formatted['legal_notice']}\n")

if __name__ == '__main__':
    run_tester()
