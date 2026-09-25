# SIH 26108 — AI-Powered Indian Standards Recommendation Engine for Procurement Descriptions

[![Smart India Hackathon](https://img.shields.io/badge/SIH-26108-blue.svg)](https://sih.gov.in)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An evidence-grounded decision support platform that maps natural-language procurement descriptions to applicable **Indian Standards (IS codes)**, relevant clauses, and statutory **Quality Control Orders (QCOs)** issued by Ministry gazettes.

---

## 📌 Problem Statement Overview

Government departments, Public Sector Undertakings (PSUs), procurement agencies, and private organizations prepare detailed procurement descriptions for products and services. Procurement officials must identify the appropriate **Indian Standards (IS codes)** and Quality Control Orders applicable to those requirements.

Currently, finding the appropriate standard requires manual searching through standards catalogs, trade keywords, amendment sheets, related testing standards, and fragmented gazette notifications.

---

## 🌟 Key System Capabilities

- **NLP Entity Extraction:** Extracts product types, material compositions, intended applications, and technical specifications from natural language text.
- **Dense Vector Semantic Search:** Computes 384-dimensional dense vector embeddings via `SentenceTransformers all-MiniLM-L6-v2` for semantic similarity matching.
- **Knowledge Graph RAG (Neo4j / NetworkX):** Traverses 1-hop and 2-hop inter-standard relationships (`NORMATIVE_REFERENCE`, `SUPERSEDES`, `COMPLEMENTS`).
- **Statutory QCO Compliance Engine:** Automatically flags Quality Control Orders issued under official Ministry gazettes.
- **Explainable Hybrid Ranking:** Combines dense vector similarity, entity match score, graph relevance score, application match score, and QCO mandatory weights into a transparent relevance score.
- **Evidence & Provenance Grounding:** Provides verifiable primary source citations, official BIS catalog URLs, and relevant clause excerpts.
- **Safety Guardrails & Security:** Detects ambiguous requirements missing mandatory attributes (`NEEDS_CLARIFICATION`) and rejects non-procurement queries (`OUT_OF_DOMAIN`). Defends against SQLi, Cypher injection, XSS script tags, and prompt injection attempts.

---

## 🏗️ System Architecture

```text
                  USER (Procurement Officer)
                            │
                            ▼
               [ Procurement Description ]
                            │
                            ▼
                [ Security Sanitizer ]
             (XSS / SQLi / Prompt Filter)
                            │
                            ▼
               [ Query Guardrails Check ]
             (Ambiguity & Scope Verification)
                            │
                            ▼
               [ NLP Entity Extraction ]
           (Product, Category, Material, Spec)
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
    [ Vector Retrieval ]           [ Knowledge Graph ]
    (SentenceTransformers)       (Neo4j / In-Memory Graph)
            │                               │
            └───────────────┬───────────────┘
                            ▼
                       [ Graph-RAG ]
               (Context & References)
                            │
                            ▼
                    [ QCO Engine ]
              (Gazette Compliance Flag)
                            │
                            ▼
                  [ Hybrid Ranker ]
           (Multi-Factor Score Fusion)
                            │
                            ▼
                [ Evidence Grounding ]
              (Verifiable BIS Links)
                            │
                            ▼
            [ Explainable Recommendation UI ]
```

---

## 📊 Dataset & Baseline Performance (Phase 8 Facts)

| Metric | Measured Value | Provenance / Source |
|---|---|---|
| **Indexed Standards Count** | 120 Verified Standards | Official BIS Standards Catalog (Electrical & Civil) |
| **Evaluation Benchmark** | 195 Multi-Sector Queries | 13 Product Sectors (`data/evaluation/phase8_queries.csv`) |
| **MRR (System B / System C)** | 0.2655 / 0.1694 | `reports/phase8_evaluation_report.json` |
| **Precision@1 (System B / System C)** | 0.2462 / 0.1538 | `reports/phase8_evaluation_report.json` |
| **P50 Latency** | `17.64 ms` | `reports/phase8_performance_report.md` |
| **P95 Latency** | `24.45 ms` | `reports/phase8_performance_report.md` |
| **QCO Detection Accuracy** | `77.14%` | Gazette Notification Verification |
| **Ambiguity Guardrail Accuracy** | `100.0%` | Underspecified Query Tests |
| **Out-of-Domain Rejection Accuracy**| `100.0%` | Non-procurement Query Tests |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11 or Python 3.14
- Git

### 2. Environment Setup & Dependency Installation
```bash
# Clone the repository
git clone https://github.com/SIH26108/SIH26108.git
cd SIH26108

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Pre-Demo Health Check
```bash
python scripts/demo_check.py
```

### 4. Start REST API Server & Web UI
```bash
python -m api.routes
```
Open your browser at `http://localhost:8000/` to launch the search dashboard.

---

## ⚡ SIH Live Demonstration Scenarios

The web interface includes 5 preset demo scenario buttons:

1. **Scenario 1 — Electrical Cable Mapping:**  
   `"Procurement of 1.5 sq mm single core PVC insulated flame retardant copper electrical cables suitable for internal building wiring."`  
   *Expected:* Returns **IS 694** (96% match) with mandatory QCO certification flag.
2. **Scenario 2 — Ambiguous Procurement Guardrail:**  
   `"Requirement for electrical cable for office project."`  
   *Expected:* Returns `NEEDS_CLARIFICATION` prompting missing voltage/conductor parameters.
3. **Scenario 3 — Multi-Attribute Civil Construction:**  
   `"Ready mixed concrete (RMC) grade M30 using Ordinary Portland Cement 43 Grade and coarse aggregates for structural RCC slab."`  
   *Expected:* Returns **IS 4926** with linked normative references **IS 456**, **IS 8112**, **IS 383**.
4. **Scenario 4 — QCO Mandatory Certified Product:**  
   `"Supply of outdoor 500 kVA 11kV/0.415kV oil immersed distribution transformer with Energy Efficiency Level 2."`  
   *Expected:* Returns **IS 1180:Part 1** with Ministry of Power Gazette QCO notice.
5. **Scenario 5 — Out-of-Domain Safety Rejection:**  
   `"What is the best smartphone for gaming and how to write a Python fibonacci function?"`  
   *Expected:* Returns `OUT_OF_DOMAIN` without guessing arbitrary standards.

---

## 🧪 Testing & Evaluation Commands

### Run Full Test Suite
```bash
python -m pytest
```

### Run 195-Query Comparative Evaluation
```bash
python scripts/evaluate_phase8.py
```

### Run Concurrency & Latency Benchmark
```bash
python scripts/benchmark_performance.py
```

---

## 🐳 Docker Deployment

```bash
# Build and run container with docker-compose
docker-compose up --build
```
Access application at `http://localhost:8000/`.

---

## ⚠️ Known Operational Limitations

1. **Pilot Dataset Scope:** Currently indexes 120 verified standards across Electrical and Civil sectors. Full production deployment requires scaling to the complete 20,000+ active BIS standards corpus.
2. **CPU Embedding Latency:** Dense vector embedding generation on CPU adds ~12-18ms latency under high concurrency queues.
3. **QCO Verification Scope:** QCO directives apply strictly to gazetted records in the verified database.

---

## 📄 License

This project is developed for **Smart India Hackathon (SIH) Problem Statement 26108** under the MIT License.
