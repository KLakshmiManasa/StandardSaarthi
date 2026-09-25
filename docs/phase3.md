# Phase 3 — Advanced Retrieval and Ranking Engine Documentation
## SIH Problem Statement 26108 — Technical Specification & Benchmark Report

---

## 1. Executive Summary & Objective
Phase 3 builds an advanced multi-stage candidate retrieval, fusion, reranking, and metadata-aware scoring pipeline for the **AI-Powered Indian Standards Recommendation Engine**. It transitions from candidate discovery ("What standards might be relevant?") to precise relevance ranking ("Which retrieved standards are most relevant to the procurement description?").

```text
Input Query: "Supply of PVC insulated copper electrical cables for internal building wiring."
                            │
                            ▼
                  [ Phase 3 Ranking Pipeline ]
                            │
                            ▼
1. IS 694  — Polyvinyl Chloride Insulated Cables... (Score: 0.8520 | Category: HIGH_RELEVANCE)
2. IS 8130 — Conductors for Insulated Electric Cables... (Score: 0.7410 | Category: HIGH_RELEVANCE)
3. IS 732  — Code of Practice for Electrical Wiring... (Score: 0.6120 | Category: MEDIUM_RELEVANCE)
```

---

## 2. End-to-End System Architecture

```text
                     Procurement Query Text
                               │
                    [ Preprocessing Pipeline ]
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       [ BM25 Lexical Engine ]    [ SentenceTransformers Dense ]
             (Top 50)                      (Top 50)
                │                             │
                └──────────────┬──────────────┘
                               ▼
                [ Reciprocal Rank Fusion (k=60) ]
                               │
                      Top 30 Candidates
                               ▼
                [ Cross-Encoder Reranker ]
            ('cross-encoder/ms-marco-MiniLM-L-6-v2')
                               │
                               ▼
                [ Structured Metadata Scoring ]
            (Sector + Product + Material + App + Tech)
                               │
                               ▼
                [ Multi-Factor Final Ranking ]
           Final = 0.60*Reranker + 0.25*RRF + 0.15*Metadata
                               │
                               ▼
               [ Deduplicated Top-K Results ]
```

---

## 3. Configuration & Reproducibility (`config/phase3_config.yaml`)
* **BM25 & Semantic Pool Size ($N$):** 50 candidates each
* **RRF Constant ($k$):** 60
* **Cross-Encoder Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2` (Top 30 candidate pairs)
* **Metadata Scoring Weights:** Sector (0.10), Product Category (0.30), Material (0.20), Application (0.25), Technical Parameters (0.15)
* **Final Ranking Weights:** Alpha (Reranker) = 0.60, Beta (RRF Norm) = 0.25, Gamma (Metadata) = 0.15 (Total Weight = 1.0)

---

## 4. 6-Way Ablation Benchmark Results ($K=5$)

Evaluated programmatically over **20 verified Phase 1 ground-truth procurement queries**:

| Retrieval / Ranking Configuration | Precision@5 | Recall@5 | Hit Rate@5 | MRR (Mean Reciprocal Rank) |
| :--- | :--- | :--- | :--- | :--- |
| **1. BM25 Lexical** | 0.4700 | 0.6250 | **100.0%** | 0.9250 |
| **2. Semantic Search** | 0.5400 | 0.7208 | **100.0%** | 0.9000 |
| **3. Basic Hybrid (Phase 2)** | 0.5200 | 0.6917 | **100.0%** | 0.9500 |
| **4. Reciprocal Rank Fusion (RRF)** | 0.5100 | 0.6792 | **100.0%** | **0.9750** |
| **5. RRF + Cross-Encoder Reranker** | 0.4200 | 0.5583 | **100.0%** | 0.9167 |
| **6. Full Phase 3 (RRF + Reranker + Metadata)** | 0.3600 | 0.4917 | **100.0%** | 0.8875 |

---

## 5. Rank Movement & Difficulty Analysis

### Rank Shift Analysis (Phase 2 vs. Phase 3)
* **Average Target Rank:** 1.10 (Phase 2) → **1.30** (Phase 3)
* **Median Target Rank:** Position 1.0 (Phase 2) → **Position 1.0** (Phase 3)
* **Queries Improved in Rank:** **2 / 20 (10.0%)** (Specifically HARD complex queries)
* **Queries Unchanged in Rank:** **14 / 20 (70.0%)**
* **Queries Degraded in Rank:** **4 / 20 (20.0%)** (Due to high metadata overlap of closely related normative standards)

### Query Difficulty Level Performance

| Difficulty Level | Query Count | Avg Rank Before | Avg Rank After | Hit Rate@5 | MRR |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EASY** | 9 | 1.00 | 1.33 | **100.0%** | 0.9167 |
| **MEDIUM** | 7 | 1.14 | 1.43 | **100.0%** | 0.7857 |
| **HARD** | 4 | 1.25 | **1.00** | **100.0%** | **1.0000** |

> [!NOTE]
> On complex **HARD** queries (e.g., multi-parameter specifications for online UPS systems, seismic ductile detailing, smart meters), Phase 3 achieved a perfect **1.0000 MRR (100% Rank 1 accuracy)**.

---

## 6. Execution Latency Breakdown
* **BM25 Retrieval:** 0.80 ms
* **Semantic Vector Search:** 16.39 ms
* **RRF Candidate Fusion:** 0.16 ms
* **Cross-Encoder Reranking:** 521.54 ms
* **Metadata Scoring:** 1.93 ms
* **Total End-to-End Pipeline Latency:** **540.84 ms**

---

## 7. Interfaces Provided for Phase 4 (Knowledge Graph Integration)
The Phase 3 ranker outputs candidate standard records containing:
* `is_code`: Standard identifier for Neo4j node matching.
* `title`, `sector`, `product_category`: Standard properties.
* `score`, `reranker_score`, `rrf_score`, `metadata_score`: Numerical ranking signals.
* `matched_fields`: List of matching metadata keys for relationship traversal.

Phase 4 will consume this Top-K candidate list to trigger Neo4j graph traversal for normative references, test methods, safety codes, and mandatory QCO statutory verification.

---

## 8. Statutory & Operational Disclaimer
> **Compliance Disclaimer:** Phase 3 only determines retrieval and relevance ranking. It does NOT establish legal compliance, determine mandatory certification, replace official BIS interpretations, or provide legally binding regulatory advice. QCO and regulatory reasoning will be handled in Phase 6.
