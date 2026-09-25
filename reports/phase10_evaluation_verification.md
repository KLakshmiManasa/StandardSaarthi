# Phase 10 — Evaluation Verification Report

**Verification Date:** 2026-09-23  
**Dataset File:** `data/evaluation/phase8_queries.csv`  
**Dataset Version:** `v0.2-phase8`  
**Total Benchmark Queries:** 195 across 13 Product Sectors  
**Script Executed:** `scripts/evaluate_phase8.py`  

---

## 1. Comparative Metrics Verification Table

| Metric | System A (BM25 Keyword) | System B (Vector Semantic RAG) | System C (Graph-RAG + QCO Pipeline) | Verification Source |
|---|---|---|---|---|
| **MRR (Mean Reciprocal Rank)** | 0.2450 | **0.2655** | 0.1694 | `reports/phase8_evaluation_report.json` |
| **Precision@1** | 0.2205 | **0.2462** | 0.1538 | `reports/phase8_evaluation_report.json` |
| **Precision@3** | 0.1248 | **0.1350** | 0.0786 | `reports/phase8_evaluation_report.json` |
| **Recall@5** | 0.1654 | **0.1679** | 0.1085 | `reports/phase8_evaluation_report.json` |
| **NDCG@5** | 0.2420 | **0.2617** | 0.1662 | `reports/phase8_evaluation_report.json` |

---

## 2. Key Findings & Insights

1. **Top Retrieval Accuracy:** System B (Vector Semantic RAG) achieves the highest raw top-1 retrieval precision (`P@1: 0.2462`, `MRR: 0.2655`) on the expanded 195 multi-sector dataset.
2. **Explainability vs Ranking Tradeoff:** System C (Graph-RAG + QCO) prioritizes multi-hop explainability, normative reference traversals, and gazette compliance verification.
3. **Execution Latency:** System C maintains a P50 execution latency of `17.64 ms` and P95 latency of `24.45 ms`.
4. **QCO Verification Accuracy:** `77.14%` accuracy across gazetted QCO compliance checks.
