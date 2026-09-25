# SIH 26108 — Claim-to-Evidence Audit Matrix

Every technical claim present in presentation slides, README, reports, demo script, and judge Q&A is audited against authoritative files in the repository.

---

## Audit Matrix Table

| Claim | Value / Statement | Source File | Verification Method | Status |
|---|---|---|---|---|
| **Indexed Standards Count** | 120 Verified Standards | `data/processed/standards_phase5.json` | JSON record count inspection | **VERIFIED** |
| **Evaluation Queries Count** | 195 Queries (175 verified, 10 partially verified, 10 synthetic) | `data/evaluation/phase8_queries.csv` | CSV row audit via Pandas | **VERIFIED** |
| **Product Categories Covered** | 13 Product Sectors | `data/processed/dataset_version.json` | Sector field list audit | **VERIFIED** |
| **Primary Cable Standard Match** | IS 694 for PVC Electrical Cables | `integration/pipeline.py` | Live pipeline execution test | **VERIFIED** |
| **Match Score Calculation** | 96% Match (Weighted Rank Fusion Score = 0.964) | `phase5/ranking/hybrid_ranker.py` | Score breakdown math audit | **VERIFIED** |
| **P50 Latency** | 17.64 ms | `reports/phase8_evaluation_report.json` | Benchmark execution log | **VERIFIED FROM REPORT** |
| **P95 Latency** | 24.45 ms | `reports/phase8_evaluation_report.json` | Benchmark execution log | **VERIFIED FROM REPORT** |
| **MRR (Vector / Graph-RAG)** | 0.2655 (Vector) / 0.1694 (Graph-RAG) | `reports/phase8_evaluation_report.json` | Comparative metrics log | **VERIFIED FROM REPORT** |
| **Precision@1 (Vector / Graph-RAG)** | 0.2462 (Vector) / 0.1538 (Graph-RAG) | `reports/phase8_evaluation_report.json` | Comparative metrics log | **VERIFIED FROM REPORT** |
| **QCO Detection Accuracy** | 77.14% | `reports/phase8_evaluation_report.json` | Gazette verification audit | **VERIFIED FROM REPORT** |
| **Ambiguity Detection Accuracy** | 100.0% | `phase6/tests/test_guardrails.py` | Automated Pytest suite | **VERIFIED** |
| **Out-of-Domain Rejection Accuracy**| 100.0% | `phase6/tests/test_guardrails.py` | Automated Pytest suite | **VERIFIED** |
| **Security Threat Protection** | 100.0% (SQLi, XSS, Prompt Injection, Cypher) | `tests/security/test_security_phase8.py` | Automated Security Pytest suite | **VERIFIED** |
| **Test Suite Pass Count** | 53 Tests Passing | `pytest` test runner | Pytest execution run | **VERIFIED** |
| **Pre-Demo Health Check** | 9/9 Checks Passing (READY) | `scripts/demo_check.py` | Automated health check script | **VERIFIED** |

---

## Scientific Language Disambiguation

1. **"96% Match"**: Refers to the weighted normalized hybrid relevance score ($0.964$), NOT prediction accuracy.
2. **"Zero Hallucination"**: Refers to evidence grounding where IS codes and QCO notices are strictly fetched from verified database records.
3. **"100% Guardrail Accuracy"**: Refers to 100% pass rate on the 195-query evaluation benchmark suite for ambiguity and out-of-domain query classification.
