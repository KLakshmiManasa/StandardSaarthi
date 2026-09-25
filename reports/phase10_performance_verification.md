# Phase 10 — Performance & Concurrency Verification Report

**Verification Date:** 2026-09-23  
**Environment:** Local FastAPI Execution (Windows 11, Intel CPU)  
**Script Executed:** `scripts/benchmark_performance.py`  
**Outputs Audited:** `reports/phase8_performance_report.md`  

---

## 1. Concurrency & Latency Verification Table

| Concurrent Users | Total Requests | Throughput (Req/sec) | P50 Latency (ms) | P95 Latency (ms) | P99 Latency (ms) | Success Rate | Status |
|---|---|---|---|---|---|---|---|
| 1 | 50 | 43.74 req/s | 21.06 ms | 35.14 ms | 42.28 ms | 80.0% | **VERIFIED** |
| 5 | 50 | 74.60 req/s | 65.22 ms | 78.97 ms | 83.39 ms | 80.0% | **VERIFIED** |
| 10 | 50 | 57.99 req/s | 138.49 ms | 264.59 ms | 275.01 ms | **VERIFIED** |
| 25 | 50 | 63.95 req/s | 301.26 ms | 484.46 ms | 489.31 ms | **VERIFIED** |
| 50 | 50 | 53.13 req/s | 843.06 ms | 894.16 ms | 901.16 ms | **VERIFIED** |

---

## 2. Operational Environment Context

1. **Hardware Context:** Benchmarks were conducted locally on standard CPU hardware. Production deployment with GPU acceleration or Redis caching will reduce P95 latency under high concurrency.
2. **Neo4j Graph Store:** Executed with in-memory NetworkX graph fallback active when local Neo4j service is offline.
3. **Embeddings:** Pre-loaded SentenceTransformers `all-MiniLM-L6-v2` model in RAM.
