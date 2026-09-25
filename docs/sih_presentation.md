# Smart India Hackathon (SIH 26108) — 10-Slide Presentation Content

## Slide 1 — Title Slide
- **Title:** AI-Powered Indian Standards Recommendation Engine for Procurement Descriptions
- **Problem Statement:** SIH Problem Statement 26108
- **Subtitle:** Graph-RAG, QCO Compliance Engine & Evidence-Grounded Search

---

## Slide 2 — Problem & Need
- Procurement officials write descriptions in natural language.
- Identifying applicable Indian Standards (IS codes) currently requires manual catalog lookups.
- Missing Quality Control Orders (QCOs) leads to non-compliant public procurement tenders.

---

## Slide 3 — Existing Gap
- Traditional keyword search misses trade jargon synonyms ("PVC wire" vs "Polyvinyl chloride cable").
- Basic vector search lacks relationship awareness and regulatory gazette context.
- Existing tools do not provide verifiable evidence provenance or ambiguity detection.

---

## Slide 4 — Proposed Solution & Pipeline
- **NLP Entity Extraction:** Extracts product types, materials, applications, and technical specs.
- **Dense Vector Search:** Embeddings via `SentenceTransformers all-MiniLM-L6-v2`.
- **Knowledge Graph RAG:** Traverses inter-standard relationships in Neo4j / NetworkX.
- **QCO Engine:** Verifies mandatory statutory certification directives.
- **Hybrid Ranking:** Multi-factor score fusion with evidence grounding.

---

## Slide 5 — Architecture
- Visual pipeline: `Input -> Security -> Guardrails -> NLP -> Vector Search -> Knowledge Graph -> QCO Engine -> Hybrid Ranking -> Evidence -> Frontend UI`.
- Dual-store architecture: Neo4j Cypher queries with seamless in-memory fallback.

---

## Slide 6 — How It Works (Sample Flow)
- **Input:** `"Procurement of 1.5 sq mm single core PVC insulated flame retardant copper electrical cables for internal building wiring."`
- **NLP Extraction:** Product: Cables | Category: Electrical | Material: Copper, PVC | Application: Internal wiring.
- **Output:** **IS 694** (96.4% match) | **QCO Status:** Mandatory Certification | **Evidence:** BIS Catalog 2024.

---

## Slide 7 — Live Demo Scenarios
- **Scenario 1:** Electrical Cable Mapping (IS 694).
- **Scenario 2:** Ambiguous Query Guardrail (`NEEDS_CLARIFICATION`).
- **Scenario 3:** Multi-Attribute Civil Concrete (IS 4926 & linked IS 456, IS 383).
- **Scenario 4:** QCO Distribution Transformer (IS 1180:Part 1).
- **Scenario 5:** Out-of-Domain Safety Rejection (`OUT_OF_DOMAIN`).

---

## Slide 8 — Empirical Evaluation Benchmark (Phase 8 Results)
- Tested across **195 multi-sector queries** covering 13 product sectors:
  - **P50 Latency:** `17.64 ms`
  - **P95 Latency:** `24.45 ms`
  - **QCO Detection Accuracy:** `77.14%`
  - **Ambiguity Guardrail Accuracy:** `100.0%`
  - **Out-of-Domain Rejection Accuracy:** `100.0%`

---

## Slide 9 — Innovation & Differentiation
- **Grounding over Hallucination:** Explicit evidence citations and primary source links.
- **Safety First:** Guardrails for ambiguity and malicious injection defense.
- **Statutory QCO Awareness:** Integrates gazette order notices directly into search results.

---

## Slide 10 — Future Roadmap & Scalability
- **Corpus Expansion:** Scale knowledge graph from 120 pilot standards to 20,000+ active BIS standards.
- **GeM Portal Integration:** Direct API connector for Government e-Marketplace procurement auto-filling.
- **Multilingual Support:** Regional Indian language NLP extraction for tender descriptions.
