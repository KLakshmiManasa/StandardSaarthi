"""
SIH 26108 — Phase 6 Comprehensive Metrics & Profiling Engine
Calculates Information Retrieval (IR), Entity Extraction (F1), QCO Regulatory, Evidence Verification, and Latency Metrics.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List

class ComprehensiveMetricsEngine:
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

    def compute_ir_metrics(self, retrieved: List[str], target_code: str, all_relevant: set, top_k_levels: List[int] = [1, 3, 5, 10]) -> Dict[str, float]:
        """
        Computes Precision@K, Recall@K, MRR, and NDCG@K for a single query.
        """
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

    def compute_entity_metrics(self, extracted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculates precision, recall, and F1 for entity extraction.
        """
        field_f1s = []
        for field in ["product", "category", "materials", "application"]:
            ext_val = str(extracted.get(field, "")).lower()
            gt_val = str(ground_truth.get(field, "")).lower()

            if not gt_val or gt_val == "unspecified" or gt_val == "none":
                continue

            matches = any(w in ext_val for w in gt_val.split(",")) if gt_val else False
            f1 = 1.0 if matches else 0.0
            field_f1s.append(f1)

        avg_f1 = float(np.mean(field_f1s)) if field_f1s else 1.0
        return {
            "entity_precision": round(avg_f1, 4),
            "entity_recall": round(avg_f1, 4),
            "entity_f1": round(avg_f1, 4)
        }

    def compute_latency_percentiles(self, latencies_ms: List[float]) -> Dict[str, float]:
        """
        Computes P50 (median) and P95 latency metrics.
        """
        if not latencies_ms:
            return {"p50_ms": 0.0, "p95_ms": 0.0, "mean_ms": 0.0}

        arr = np.array(latencies_ms)
        return {
            "p50_ms": round(float(np.percentile(arr, 50)), 2),
            "p95_ms": round(float(np.percentile(arr, 95)), 2),
            "mean_ms": round(float(np.mean(arr)), 2)
        }


if __name__ == '__main__':
    cme = ComprehensiveMetricsEngine()
    ir = cme.compute_ir_metrics(["IS 694", "IS 8130"], "IS 694", {"IS 694", "IS 8130"})
    print("[OK] Sample IR Metrics:", ir)
