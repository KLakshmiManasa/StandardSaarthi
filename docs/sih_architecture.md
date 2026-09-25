# Smart India Hackathon (SIH 26108) — System Architecture Document

## 1. Executive Summary

This document provides both high-level and detailed technical architecture diagrams for **SIH Problem Statement 26108: AI-Powered Indian Standards Recommendation Engine for Procurement Descriptions**.

The architecture combines Natural Language Processing (NLP), dense vector semantic search, Knowledge Graph RAG, Quality Control Order (QCO) gazette compliance verification, and multi-factor hybrid ranking into a security-first, evidence-grounded decision support tool.

---

## 2. High-Level Judge Architecture Diagram

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

## 3. Subsystem Breakdown

1. **Security & Input Sanitization:** Checks inputs for SQL injection, Cypher injection, XSS script tags, and LLM prompt injection attempts before pipeline execution.
2. **Query Guardrails:** Evaluates input completeness. If essential fields are missing, it triggers `NEEDS_CLARIFICATION` without guessing. Non-procurement queries return `OUT_OF_DOMAIN`.
3. **NLP Entity Extractor:** Extracts product types, material compositions, intended applications, and technical parameters using domain tokenization.
4. **Dense Vector Semantic Search:** Computes 384-dimensional dense vector embeddings using `SentenceTransformers all-MiniLM-L6-v2` for semantic similarity search.
5. **Knowledge Graph RAG (Neo4j / NetworkX):** Traverses multi-hop relationships (`NORMATIVE_REFERENCE`, `SUPERSEDES`, `COMPLEMENTS`) between Indian Standards, product categories, and materials.
6. **QCO Compliance Engine:** Verifies whether a candidate standard falls under a mandatory Quality Control Order gazetted by Ministry directives.
7. **Configurable Hybrid Ranker:** Fuses dense vector similarity, entity match score, graph relevance score, application match score, and QCO mandatory weight.
8. **Evidence & Provenance Builder:** Assembles verifiable BIS catalog URLs, gazette order references, and clause citations for transparent auditing.
