# Phase 5 — Graph-RAG & Explainable Recommendation Engine Documentation

## Executive Summary
Phase 5 implements the complete end-to-end intelligence pipeline for SIH Problem Statement 26108. It connects natural-language procurement description extraction with dense vector semantic search, Knowledge Graph RAG traversals, Quality Control Order (QCO) regulatory compliance evaluation, configurable hybrid scoring, evidence provenance tracking, a RESTful API (`POST /api/recommend`), an interactive web dashboard, and a 3-mode comparative evaluation benchmark.

---

## 1. Intelligence Pipeline Architecture

```
Procurement Description
         ↓
NLP Entity Extractor (nlp/entity_extractor.py)
         ↓
Vector Semantic Retriever (phase5/retrieval/vector_retriever.py)
         ↓
Knowledge Graph-RAG Traversal (phase5/retrieval/graph_rag.py)
         ↓
QCO Regulatory Engine (phase5/qco/qco_engine.py)
         ↓
Configurable Hybrid Ranker (phase5/ranking/hybrid_ranker.py & config/phase5_config.yaml)
         ↓
Evidence Provenance System (phase5/evidence/evidence_system.py)
         ↓
Explainable IS Recommendation & Interactive Dashboard
```

---

## 2. Component Specifications

### A. Data Layer & Provenance Enforcer (`data/phase5_data_loader.py`)
Enriches standards records (`data/processed/standards_phase5.json`) to enforce 18 complete provenance fields:
`is_code`, `title`, `product_category`, `product_type`, `description`, `materials`, `applications`, `industries`, `keywords`, `related_standards`, `clauses`, `qco_applicability`, `qco_reference`, `source_organization`, `source_document`, `source_url`, `retrieval_date`, `status`.

### B. NLP Requirement & Entity Extractor (`nlp/entity_extractor.py`)
Extracts structured domain entities from raw text:
* `product`: Primary equipment or item (e.g. `PVC Insulated Cable`, `OPC 53 Cement`, `TMT Rebar`)
* `category`: Sector classification (`Electrical`, `Civil`)
* `materials`: Raw material composition (`Copper`, `PVC`, `Aluminum`, `Steel`)
* `application`: Functional usage environment (`Control Panel Wiring`, `Foundation Raft`)
* `industry`: Target industry domain
* `technical_attributes`: Quantitative parameters (`1.1kV`, `6 sq mm`, `3 core`, `53 MPa`)
* `regulatory_terms`: Statutory terms (`QCO`, `BIS`, `Mandatory`)

### C. Vector Retrieval & Graph-RAG Traversal (`phase5/retrieval/`)
* **Vector Retriever:** Generates embeddings via `sentence-transformers/all-MiniLM-L6-v2` and retrieves top candidate standards.
* **Graph-RAG Retriever:** Maps query entities to graph nodes, traverses 1-hop/2-hop relationships (`NORMATIVE_REFERENCE`, `TEST_METHOD`, `MATERIAL_SPECIFICATION`, `ASSOCIATED_WITH_QCO`), and extracts relevant clause text and multi-hop evidence.

### D. Configurable Hybrid Ranker (`phase5/ranking/hybrid_ranker.py`)
Loaded via `config/phase5_config.yaml`:
$$\text{Relevance Score} = 0.30 \cdot S_{\text{vector}} + 0.25 \cdot S_{\text{entity}} + 0.20 \cdot S_{\text{graph}} + 0.15 \cdot S_{\text{app}} + 0.10 \cdot S_{\text{qco}}$$
Generates transparent human-readable explanations explaining why each standard was recommended.

### E. QCO Regulatory Engine (`phase5/qco/qco_engine.py`)
Evaluates Quality Control Orders, covered product scope, mandatory certification clauses, and issuing authority.
**Zero Hallucination Safeguard:** If no verified QCO mapping exists in the knowledge base, explicitly returns:
`"No verified QCO mapping found in the available knowledge base."`

### F. Evidence Provenance System (`phase5/evidence/evidence_system.py`)
Bundles source organization, source document name, official URL link, standard code, clause number, and QCO gazette notification into verifiable evidence packages.

---

## 3. REST API Endpoint & Frontend Interface

### REST API Endpoint (`POST /api/recommend`)
* **Request:** `{"description": "Procurement of 1.1kV 3 core 6 sq mm PVC insulated copper flexible cable for control panel wiring with QCO compliance.", "top_k": 5, "mode": "graph_rag"}`
* **Response:** Extracted entities, recommended standards, relevance scores, confidence levels, score breakdowns, explanations, QCO info, evidence provenance, processing latency.

### Web Search Dashboard (`frontend/`)
* Clean responsive interface served at `http://localhost:8000/`.
* Displays natural-language search bar, retrieval mode selector, extracted entity tags, recommendation cards with relevance badges, QCO status indicators, and direct evidence link inspection.

---

## 4. Baseline Comparative Evaluation Benchmark

Evaluated on 20 ground-truth procurement queries (`data/evaluation/ground_truth.csv`):

| Retrieval Mode | MRR | Precision@1 | Precision@5 | Recall@5 | NDCG@5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Mode A: BM25 Keyword Search** | 0.9500 | 0.9000 | 0.4700 | 0.7308 | 0.9440 |
| **Mode B: Vector Semantic RAG** | **0.9750** | **0.9500** | **0.5400** | **0.8042** | **0.9327** |
| **Mode C: Proposed Graph-RAG + QCO** | 0.5523 | 0.5000 | 0.2200 | 0.3542 | 0.5137 |

### Additional Pipeline Metrics
* **Entity Extraction Accuracy:** `95.0%`
* **QCO Detection Accuracy:** `100.0%`
* **Evidence Retrieval Coverage:** `100.0%`

### Key Empirical Finding
Vector Semantic RAG (Mode B) achieves the highest raw 1-shot top-1 retrieval precision (MRR 0.975). Proposed Graph-RAG + QCO (Mode C) provides rich multi-hop explainability, clause evidence, and regulatory compliance flags, but re-ranking based on graph connectivity & regulatory weights can lower pure top-1 ranking precision if QCO weights are overly aggressive.

---

## 5. Setup & Execution Instructions

1. **Enrich Dataset:**
   `python -m data.phase5_data_loader`
2. **Run Comparative Evaluation Benchmark:**
   `python -m phase5.evaluation.evaluator`
3. **Run Unit Tests:**
   `python -m pytest phase5/tests/`
4. **Launch API Server & Web UI:**
   `uvicorn phase2.api.routes:app --host 0.0.0.0 --port 8000 --reload`
5. Access interactive UI at `http://localhost:8000/` or Swagger docs at `http://localhost:8000/docs`.
