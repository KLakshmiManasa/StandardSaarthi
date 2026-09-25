# 5-Minute Technical Deep Dive — SIH 26108 (For Technical Judges)

## 1. System Architecture Overview

The system implements a multi-stage hybrid intelligence pipeline combining Natural Language Processing (NLP), dense vector search, dual-store Knowledge Graph RAG, deterministic QCO gazette matching, and multi-factor rank fusion.

```text
Natural Language Procurement Description
                   │
                   ▼
       [ 1. Security Sanitizer ]
                   │
                   ▼
        [ 2. Query Guardrails ]
                   │
                   ▼
       [ 3. NLP Entity Extractor ]
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
 [ Vector Search ]    [ Knowledge Graph ]
 (SentenceTransformers) (Neo4j / NetworkX)
       │                       │
       └───────────┬───────────┘
                   ▼
             [ Graph-RAG ]
                   │
                   ▼
            [ QCO Engine ]
                   │
                   ▼
           [ Hybrid Ranker ]
                   │
                   ▼
         [ Evidence Grounding ]
```

---

## 2. Deep Dive into Pipeline Stages

### A. Security Sanitization & Guardrails
- Input text passes through `SecuritySanitizer`, defending against SQL injection, Cypher injection, XSS script tags, and LLM prompt injection attempts.
- `QueryGuardrails` evaluates input completeness. If key attributes are missing, it triggers `NEEDS_CLARIFICATION`. Non-procurement inputs return `OUT_OF_DOMAIN`.

### B. NLP Entity Extraction
- Uses domain-specific regex and tokenization dictionary to extract `product`, `category`, `materials`, `application`, and `technical_characteristics`.

### C. Hybrid Candidate Retrieval
- **Dense Vector Search:** Generates 384-dimensional dense vector embeddings using `all-MiniLM-L6-v2` SentenceTransformers model for semantic similarity matching.
- **Lexical Search:** BM25 keyword search provides fallback matching for exact IS code numbers and technical identifiers.

### D. Knowledge Graph RAG (Neo4j / In-Memory Fallback)
- Dual-store graph database linking Indian Standards, product categories, material nodes, and inter-standard relationship edges (`NORMATIVE_REFERENCE`, `SUPERSEDES`, `COMPLEMENTS`).
- Traverses 1-hop and 2-hop neighborhoods to enrich retrieved candidate standards with linked testing standards and raw material specifications.

### E. QCO Gazette Compliance Engine
- Queries verified gazette records to determine if a candidate standard falls under a mandatory Quality Control Order issued by Ministry directives.

### F. Multi-Factor Hybrid Ranking
- Computes final relevance score using weighted rank fusion:
  $$S_{\text{final}} = w_{\text{vec}} \cdot S_{\text{vec}} + w_{\text{ent}} \cdot S_{\text{ent}} + w_{\text{graph}} \cdot S_{\text{graph}} + w_{\text{app}} \cdot S_{\text{app}} + w_{\text{qco}} \cdot I_{\text{qco}}$$
  where weights default to $w_{\text{vec}}=0.45, w_{\text{ent}}=0.30, w_{\text{graph}}=0.15, w_{\text{app}}=0.10$.

### G. Evidence & Provenance Grounding
- Assembles verifiable source citations, official BIS catalog URLs, and clause excerpts to ensure transparent auditing without AI hallucinations.
