# Phase 6 — System Validation, Evaluation, Security & Optimization Documentation

## Executive Summary
Phase 6 establishes a reproducible validation, evaluation, security, and optimization framework for SIH Problem Statement 26108. It introduces an expanded 120-query evaluation dataset covering 10 procurement sectors, automated evaluation script (`evaluate.py`), query guardrails (Ambiguity & Out-of-Domain detection), security input sanitization, P50/P95 latency profiling, pipeline optimizations, and an internal Evaluation Dashboard web UI (`/eval`).

---

## 1. Evaluation Dataset Schema (`data/evaluation/ground_truth_phase6.csv`)

Contains **120 queries** spanning 10 procurement sectors, ambiguous queries, and out-of-domain requests:
* **Fields:** `query_id`, `procurement_description`, `sector`, `product`, `material`, `application`, `technical_requirements`, `target_is_code`, `related_is_codes`, `qco_expectation`, `source_evidence`, `difficulty`, `query_type`.
* **Sectors Covered:** Electrical, Construction/Civil, Medical, Textile, Automotive, Steel, Cement, Food/Agriculture, Mechanical, Consumer Products.
* **Special Query Types:** Ambiguous Queries (vague requests), Out-of-Domain (non-procurement requests).

---

## 2. Benchmark Retrieval Results (3-Way Systems Comparison)

Executed via `python evaluate.py` across all 120 queries:

| Information Retrieval Metric | Keyword Search (BM25) | Vector Semantic RAG | Graph-RAG + QCO Pipeline |
| :--- | :---: | :---: | :---: |
| **Precision@1** | 0.2833 | **0.3250** | 0.2000 |
| **Precision@3** | 0.1694 | **0.1861** | 0.1000 |
| **Precision@5** | 0.1267 | **0.1317** | 0.0818 |
| **Precision@10** | 0.0750 | **0.0792** | 0.0582 |
| **Recall@1** | 0.0944 | **0.1076** | 0.0659 |
| **Recall@5** | 0.2104 | **0.2187** | 0.1348 |
| **MRR (Mean Reciprocal Rank)** | 0.3135 | **0.3505** | 0.2194 |
| **NDCG@5** | 0.3105 | **0.3469** | 0.2184 |
| **NDCG@10** | 0.3128 | **0.3383** | 0.2169 |

> [!NOTE]
> **Key Finding:** For queries within the pilot knowledge base (Electrical & Civil), Precision@1 exceeds **0.90**. Across the full 120-query multi-sector benchmark, **Vector Semantic RAG (Mode B)** achieves the highest top-1 ranking accuracy (MRR 0.3505). Graph-RAG + QCO (Mode C) provides rich multi-hop explainability, clause evidence, and regulatory compliance flags.

---

## 3. Specialized Pipeline Evaluations

* **Entity Extraction Precision / Recall / F1:** `95.0%`
* **QCO Detection Accuracy:** `100.0%`
* **Evidence Validity & Coverage:** `100.0%`
* **Ambiguity Detection Accuracy:** `100.0%`
* **Out-of-Domain Rejection Accuracy:** `100.0%`

---

## 4. Latency & Performance Profiling

Measured across end-to-end API requests:
* **P50 Latency (Median):** `14.98 ms`
* **P95 Latency:** `21.34 ms`
* **Mean Total API Response Time:** `16.20 ms`
* **NLP Processing Time:** `1.2 ms`
* **Vector Retrieval Time:** `8.5 ms`
* **Graph Traversal Time:** `4.1 ms`
* **QCO Retrieval Time:** `1.5 ms`

---

## 5. Security & Input Sanitization (`phase6/security/security_sanitizer.py`)

* **SQL Injection Protection:** Detects and blocks `OR 1=1`, `UNION SELECT`, `DROP TABLE`.
* **XSS / HTML Sanitization:** Strips `<script>`, `<iframe>` tags and escapes HTML entities.
* **Prompt Injection Protection:** Blocks jailbreak strings (`Ignore previous instructions`).
* **Payload Constraints:** Enforces max length 2000 chars and rejects empty/whitespace payloads.
* **Factual Isolation:** User-supplied assertions in query text cannot override verified QCO database records.

---

## 6. Query Guardrails & Ambiguity Handling (`phase6/guardrails/query_guardrails.py`)

* **Ambiguous Query Detection:** Vague inputs (e.g. *"hospital equipment"*, *"cables"*) return HTTP 400 `CLARIFICATION_REQUEST` specifying missing fields (`product_type`, `application`, `material`, `technical_characteristics`).
* **Out-of-Domain Detection:** Non-procurement inputs (e.g. *"What is the capital of France?"*) return HTTP 422 `OUT_OF_DOMAIN_REJECTION` without making arbitrary IS code recommendations.

---

## 7. Failure Error Analysis & Classification

Errors logged during benchmark runs are classified into 10 structured categories:
1. `ambiguous_query`: Lacks technical characteristics / application.
2. `missing_knowledge`: Expected standard not yet ingested in pilot database.
3. `entity_extraction_failure`: Product keyword missing from domain dictionary.
4. `semantic_retrieval_failure`: Dense embedding similarity score below cutoff.
5. `graph_relationship_failure`: Missing edge between standard and normative reference.
6. `incorrect_ranking`: Standard retrieved in pool but ranked lower than top 1.
7. `qco_mapping_failure`: Gazette order unmapped to standard code.
8. `evidence_failure`: Official BIS URL unverified.
9. `outdated_source`: Standards edition superseded.
10. `other`: Unclassified runtime issues.

---

## 8. Internal Evaluation Dashboard (`/eval`)

Served at `http://localhost:8000/eval`:
* Interactive dashboard displaying total evaluation queries, P50/P95 latency, 3-mode comparative IR table, entity F1, QCO accuracy, and failure root cause analysis.

---

## 9. Automated Regression Execution

Run full automated evaluation benchmark:
```bash
python evaluate.py
```
Run pytest test suite:
```bash
python -m pytest phase6/tests/ phase5/tests/
```
