# Phase 8 — Repository & System Architecture Audit

## 1. Executive Summary

This document provides a comprehensive audit of the **AI-Powered Indian Standards (IS Code) Recommendation Engine for Procurement Descriptions** as of Phase 8.

The system is designed to assist government departments, public sector undertakings (PSUs), procurement officers, and private organizations in automatically mapping natural-language procurement descriptions to applicable Indian Standards (IS codes), relevant clauses, and Quality Control Orders (QCOs).

---

## 2. System Architecture & Component Inventory

The application follows a layered, security-first intelligence architecture:

```
[ User Input / Procurement Description ]
                    │
                    ▼
       [ Frontend UI / Web Search ]
                    │
                    ▼
      [ REST API: POST /api/recommend ]
                    │
                    ▼
     [ Pipeline Orchestrator (pipeline.py) ]
      ├── 1. Security Sanitizer (XSS, SQLi, Prompt Injection)
      ├── 2. Query Guardrails (Ambiguity & Out-of-Domain Detection)
      ├── 3. NLP Entity Extractor (Products, Materials, Specs, QCOs)
      ├── 4. Vector Semantic Retriever (all-MiniLM-L6-v2)
      ├── 5. Graph-RAG Context Traverser (Neo4j / In-Memory Graph)
      ├── 6. QCO Compliance Engine (Mandatory Certification Flags)
      ├── 7. Configurable Hybrid Ranker (Vector + Graph + Entity + Application)
      └── 8. Evidence & Provenance Builder (Verifiable Citations)
                    │
                    ▼
      [ Structured Recommendation Response ]
```

### Key Components

| Layer | Component | File Path | Responsibilities |
|---|---|---|---|
| API | FastAPI App | `api/routes.py` | Exposes REST endpoints (`/api/recommend`, `/health`, `/eval`, `/api/evaluation/report`) |
| API | Health Check | `api/health.py` | Readiness monitor for API, VectorStore, GraphStore, QCO Engine |
| Orchestration | Master Pipeline | `integration/pipeline.py` | Sequential execution of security, NLP, retrieval, RAG, QCO, and ranking |
| Schemas | Pydantic Models | `integration/schemas.py` | Strict validation schemas for request/response payloads |
| Security | Sanitizer | `phase6/security/security_sanitizer.py` | Defense against injection attacks, oversized payloads, script tags |
| Guardrails | Query Classifier | `phase6/guardrails/query_guardrails.py` | Ambiguity detection and out-of-domain scope enforcement |
| NLP | Entity Extractor | `nlp/entity_extractor.py` | Extraction of products, materials, specs, QCOs |
| Retrieval | Vector Store | `phase5/retrieval/vector_retriever.py` | Dense vector embedding search using SentenceTransformers |
| Retrieval | Graph-RAG | `phase5/retrieval/graph_rag.py` | Multi-hop relationship traversal over standard hierarchies and relationships |
| Compliance | QCO Engine | `phase5/qco/qco_engine.py` | Verification of Quality Control Orders and mandatory certification |
| Ranking | Hybrid Ranker | `phase5/ranking/hybrid_ranker.py` | Multi-factor candidate scoring and weighted rank fusion |
| Evidence | Citation Engine | `phase5/evidence/evidence_system.py` | Assembles verifiable source provenance for recommendations |

---

## 3. Dataset & Knowledge Base Metrics

### Current Pilot Dataset Summary

| Metric | Count / Value | Description |
|---|---|---|
| Total Verified Standards | 120 | Curated Indian Standards covering Electrical (60) and Civil/Construction (60) |
| Total Relationships (Edges) | 130 | Standard-to-Standard relationships (replaces, complements, refers_to, subset_of) |
| Total Verified QCOs | 42 | Gazette notifications and mandatory certification directives |
| Knowledge Graph Nodes | 504 | Standard nodes, Product Category nodes, Material nodes, Organization nodes |
| Knowledge Graph Edges | 1,340 | Multi-relational connections in Neo4j/In-Memory graph |
| Vector Embeddings | 120 | 384-dimensional dense vectors generated via `all-MiniLM-L6-v2` |
| Evaluation Queries | 120 | Multi-sector query benchmark dataset with ground-truth IS code annotations |

---

## 4. API Endpoints Review

| Method | Endpoint | Description | Authentication | Status |
|---|---|---|---|---|
| `POST` | `/api/recommend` | Main recommendation endpoint | None (Public API) | Active |
| `GET` | `/health` | Subsystem health & readiness check | None | Active |
| `GET` | `/eval` | Evaluation dashboard HTML view | None | Active |
| `GET` | `/api/evaluation/report` | Returns latest benchmark evaluation JSON | None | Active |
| `GET` | `/` | Static frontend search interface | None | Active |

---

## 5. System Limitations & Known Operational Constraints

1. **Domain Coverage:** Current pilot dataset covers 120 standards across Electrical and Civil/Construction sectors. Other sectors (Medical, Automotive, Packaging, Safety) require dataset expansion.
2. **Neo4j Dependency Fallback:** In environments without a live Neo4j instance, the system seamlessly falls back to an in-memory NetworkX/graph structure.
3. **Local Embedding Execution:** CPU-based vector embedding generation adds ~8-15ms latency per request on standard hardware.
4. **QCO Verification Scope:** QCO directives are strictly checked against verified BIS/Ministry gazette records; unverified orders are explicitly flagged as `"Not Verified"`.
