"""
SIH 26108 — Phase 5 Baseline Comparison & Comparative Evaluation Benchmark
Evaluates and benchmarks Mode A (BM25 Keyword Search) vs Mode B (Vector Semantic RAG) vs Mode C (Proposed Graph-RAG + QCO Pipeline)
across Precision@K, Recall@K, MRR, NDCG@K, Entity Extraction Accuracy, QCO Detection Accuracy, and Evidence Coverage.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from phase2.retrieval.bm25_search import BM25SearchEngine
from phase5.retrieval.vector_retriever import Phase5VectorRetriever
from phase5.recommendation_engine import Phase5RecommendationEngine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GROUND_TRUTH_CSV = os.path.join(BASE_DIR, 'data', 'evaluation', 'ground_truth.csv')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
REPORT_JSON = os.path.join(OUTPUTS_DIR, 'phase5_evaluation_report.json')

class PipelineEvaluator:
    def __init__(self):
        self.bm25_engine = BM25SearchEngine()
        self.vector_retriever = Phase5VectorRetriever()
        self.graph_rag_engine = Phase5RecommendationEngine()
        self.ground_truth = pd.read_csv(GROUND_TRUTH_CSV)

    def dcg_at_k(self, r: List[int], k: int) -> float:
        r = np.asarray(r, dtype=float)[:k]
        if not r.size:
            return 0.0
        return np.sum(r / np.log2(np.arange(2, r.size + 2)))

    def ndcg_at_k(self, r: List[int], k: int) -> float:
        dcg_max = self.dcg_at_k(sorted(r, reverse=True), k)
        if not dcg_max:
            return 0.0
        return self.dcg_at_k(r, k) / dcg_max

    def evaluate_all_modes(self, top_k_levels: List[int] = [1, 3, 5, 10]) -> Dict[str, Any]:
        """
        Executes comparative benchmark across Mode A, Mode B, and Mode C.
        """
        results_mode_a = [] # Keyword BM25
        results_mode_b = [] # Vector Semantic RAG
        results_mode_c = [] # Graph-RAG + QCO

        entity_acc_list = []
        qco_acc_list = []
        evidence_cov_list = []

        for idx, row in self.ground_truth.iterrows():
            query_text = row["procurement_description"]
            target_code = str(row["target_is_code"]).strip()
            related_codes = [c.strip() for c in str(row.get("related_is_codes", "")).split(";") if c.strip()]
            all_relevant = set([target_code] + related_codes)

            # --- Mode A: BM25 Keyword Search ---
            bm25_res = self.bm25_engine.search(query_text, top_k=max(top_k_levels))
            retrieved_a = [r["is_code"] for r in bm25_res.get("results", [])]

            # --- Mode B: Vector Semantic RAG ---
            vector_res = self.vector_retriever.retrieve_candidates(query_text, top_k=max(top_k_levels))
            retrieved_b = [r["is_code"] for r in vector_res]

            # --- Mode C: Graph-RAG + QCO Pipeline ---
            graph_res = self.graph_rag_engine.recommend(query_text, top_k=max(top_k_levels), mode="graph_rag")
            retrieved_c = [r["is_code"] for r in graph_res.get("recommended_standards", [])]

            # Evaluate Retrieval Metrics for Mode A, B, C
            results_mode_a.append(self._compute_query_metrics(retrieved_a, target_code, all_relevant, top_k_levels))
            results_mode_b.append(self._compute_query_metrics(retrieved_b, target_code, all_relevant, top_k_levels))
            results_mode_c.append(self._compute_query_metrics(retrieved_c, target_code, all_relevant, top_k_levels))

            # Evaluate Entity & QCO & Evidence Metrics for Mode C
            extracted = graph_res.get("extracted_entities", {})
            entity_found = bool(extracted.get("product") and extracted.get("product") != "General Equipment")
            entity_acc_list.append(1.0 if entity_found else 0.0)

            # QCO detection check
            rec_top1 = graph_res["recommended_standards"][0] if graph_res.get("recommended_standards") else {}
            qco_info = rec_top1.get("qco_information", {})
            qco_valid = bool(qco_info.get("regulatory_notice"))
            qco_acc_list.append(1.0 if qco_valid else 0.0)

            # Evidence coverage check
            evidence = rec_top1.get("evidence", {})
            evidence_valid = bool(evidence.get("source_organization") and evidence.get("source_url"))
            evidence_cov_list.append(1.0 if evidence_valid else 0.0)

        # Aggregate metrics
        mode_a_summary = self._aggregate_metrics(results_mode_a, top_k_levels)
        mode_b_summary = self._aggregate_metrics(results_mode_b, top_k_levels)
        mode_c_summary = self._aggregate_metrics(results_mode_c, top_k_levels)

        report = {
            "evaluation_dataset_query_count": len(self.ground_truth),
            "benchmark_timestamp": "2026-09-22 16:14:00",
            "comparative_summary": {
                "mode_a_keyword_bm25": mode_a_summary,
                "mode_b_vector_rag": mode_b_summary,
                "mode_c_proposed_graph_rag": mode_c_summary
            },
            "pipeline_specific_evaluations": {
                "entity_extraction_accuracy": round(float(np.mean(entity_acc_list)), 4),
                "qco_detection_accuracy": round(float(np.mean(qco_acc_list)), 4),
                "evidence_retrieval_coverage": round(float(np.mean(evidence_cov_list)), 4)
            }
        }

        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        with open(REPORT_JSON, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"[OK] Evaluation completed on {len(self.ground_truth)} ground-truth queries.")
        print(f"Report saved to -> {REPORT_JSON}")
        return report

    def _compute_query_metrics(self, retrieved: List[str], target_code: str, all_relevant: set, top_k_levels: List[int]) -> Dict[str, Any]:
        metrics = {}

        # MRR
        mrr = 0.0
        for rank, code in enumerate(retrieved, start=1):
            if code in all_relevant:
                mrr = 1.0 / rank
                break
        metrics["mrr"] = mrr

        for k in top_k_levels:
            sub = retrieved[:k]
            hits = [1 if code in all_relevant else 0 for code in sub]
            prec = sum(hits) / k if k > 0 else 0.0
            rec = sum(hits) / max(1, len(all_relevant))
            ndcg = self.ndcg_at_k(hits, k)

            metrics[f"precision@{k}"] = round(prec, 4)
            metrics[f"recall@{k}"] = round(rec, 4)
            metrics[f"ndcg@{k}"] = round(ndcg, 4)

        return metrics

    def _aggregate_metrics(self, query_metrics: List[Dict[str, Any]], top_k_levels: List[int]) -> Dict[str, float]:
        df = pd.DataFrame(query_metrics)
        summary = {"mrr": round(float(df["mrr"].mean()), 4)}
        for k in top_k_levels:
            summary[f"precision@{k}"] = round(float(df[f"precision@{k}"].mean()), 4)
            summary[f"recall@{k}"] = round(float(df[f"recall@{k}"].mean()), 4)
            summary[f"ndcg@{k}"] = round(float(df[f"ndcg@{k}"].mean()), 4)
        return summary


if __name__ == '__main__':
    evaluator = PipelineEvaluator()
    rep = evaluator.evaluate_all_modes()
    print("\n=== PHASE 5 COMPARATIVE EVALUATION SUMMARY ===")
    for mode, metrics in rep["comparative_summary"].items():
        print(f"\n{mode.upper()}:")
        print(f"  MRR: {metrics['mrr']} | P@1: {metrics['precision@1']} | P@5: {metrics['precision@5']} | NDCG@5: {metrics['ndcg@5']}")
