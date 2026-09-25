# SIH 26108 — End-to-End System Architecture (Phase 8)

## 1. System Overview

The **AI-Powered Indian Standards Recommendation Engine for Procurement Descriptions** is a security-first, multi-stage hybrid search and Knowledge Graph-RAG system designed to map natural-language procurement requirements to applicable Indian Standards (IS codes), relevant clauses, and Quality Control Orders (QCOs).

---

## 2. Multi-Stage Pipeline Architecture

```
[ Procurement Description Input ]
              │
              ▼
   [ 1. Security Sanitizer ] ──► (Script / SQLi / Prompt Injection Filter)
              │
              ▼
   [ 2. Query Guardrails ]  ──► (Ambiguity & Out-of-Domain Detection)
              │
              ▼
   [ 3. NLP Entity Extractor ] ──► (Products, Materials, Specs, QCOs)
              │
              ▼
   [ 4. Hybrid Candidate Retrieval ]
     ├── Dense Vector Search (all-MiniLM-L6-v2)
     └── BM25 Keyword Search
              │
              ▼
   [ 5. Knowledge Graph RAG ] ──► (1-hop & 2-hop Graph Traversals)
              │
              ▼
   [ 6. QCO Compliance Engine ] ──► (Mandatory Certification & Gazette Flags)
              │
              ▼
   [ 7. Configurable Hybrid Ranker ] ──► (Vector + Graph + Entity + Application Weights)
              │
              ▼
   [ 8. Evidence & Provenance Builder ] ──► (Verifiable Source URLs & Citations)
              │
              ▼
   [ Structured Recommendation Response / Web UI ]
```

---

## 3. Core Subsystems

### A. NLP & Entity Extraction
- Uses domain-specific regex and keyword tokenization to extract product types, categories, material compositions, intended applications, and technical specifications.

### B. Hybrid Retrieval Layer
- **Vector Retrieval:** 384-dimensional embeddings produced by `all-MiniLM-L6-v2` SentenceTransformers model.
- **Lexical Search:** BM25 keyword matching for exact model numbers, technical numbers, and IS code identifiers.

### C. Knowledge Graph (Neo4j / In-Memory NetworkX Fallback)
- Dual-store architecture supporting live Neo4j Cypher queries with seamless in-memory graph fallback when Neo4j is offline.
- Stores standard hierarchy nodes, materials, applications, product categories, and standard-to-standard relationships (`NORMATIVE_REFERENCE`, `SUPERSEDES`, `COMPLEMENTS`).

### D. Security & Guardrails
- **SecuritySanitizer:** Sanitizes HTML script tags, SQL injection patterns, Cypher injection vectors, and LLM prompt injection attempts.
- **QueryGuardrails:** Detects ambiguous requirements missing mandatory attributes and isolates out-of-domain requests.
