# Phase 8 — Comprehensive Comparative Evaluation Report

**Evaluation Date:** 2026-09-23 14:00:36  
**Total Benchmark Queries:** 195 across 13 Product Sectors  
**Dataset Version:** v0.2-phase8  

---

## 1. Comparative Metrics (BM25 vs Vector RAG vs Graph-RAG + QCO)

| Metric | System A (BM25 Keyword) | System B (Vector Semantic RAG) | System C (Graph-RAG + QCO Pipeline) |
|---|---|---|---|
| **MRR (Mean Reciprocal Rank)** | 0.2450 | 0.2655 | **0.1610** |
| **Precision@1** | 0.2205 | 0.2462 | **0.1487** |
| **Precision@3** | 0.1248 | 0.1350 | **0.0718** |
| **Recall@5** | 0.1654 | 0.1679 | **0.1000** |
| **NDCG@5** | 0.2420 | 0.2617 | **0.1579** |

---

## 2. Execution Latency & Intelligence Profile

- **P50 Latency:** `21.36 ms`
- **P95 Latency:** `28.71 ms`
- **QCO Detection Accuracy:** `79.1%`
- **Ambiguity Detection Accuracy:** `100.0%`
- **Out-of-Domain Rejection Accuracy:** `100.0%`
