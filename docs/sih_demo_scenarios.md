# Smart India Hackathon (SIH 26108) — Live Demonstration Scenarios

This document provides 5 scripted presentation scenarios for SIH judges to demonstrate the core capabilities, security guardrails, knowledge graph RAG, and Quality Control Order (QCO) compliance verification of the **AI-Powered Indian Standards Recommendation Engine**.

---

## Scenario 1: Standard Electrical Cable Recommendation (High Precision Matching)

### **Goal:** Demonstrate core NLP entity extraction, dense vector retrieval, and ground-truth mapping for standard electrical cables.

- **Sample Procurement Input:**  
  `"Procurement of 1.5 sq mm single core PVC insulated flame retardant copper electrical cables for internal wiring of a government building."`
- **Expected System Output:**
  - **Status:** `SUCCESS`
  - **Extracted Entities:** Product: `Cables and Wires` | Category: `Electrical` | Materials: `["Copper", "PVC"]` | Application: `Internal building wiring`
  - **Top 1 Recommendation:** **IS 694** — *Polyvinyl Chloride Insulated Cables for Working Voltages up to and including 1100 V*
  - **Relevance Score:** `96.4%`
  - **QCO Compliance Status:** `MANDATORY CERTIFICATION (QCO APPLICABLE)`
  - **Evidence Provenance:** BIS Standards Catalog 2024 & Gazette Order Ref: `S.O. 1234(E)`
- **Judge Talking Point:** "Notice how our engine extracts technical parameters (1.5 sq mm, PVC, Copper), matches the exact IS 694 standard, and automatically flags the mandatory Quality Control Order from the official Gazette."

---

## Scenario 2: Ambiguous Procurement Description Guardrail (`needs_clarification`)

### **Goal:** Demonstrate safety guardrails detecting missing technical specifications and prompting human-in-the-loop clarification without guessing.

- **Sample Procurement Input:**  
  `"Requirement for electrical cable for office project."`
- **Expected System Output:**
  - **Status:** `NEEDS_CLARIFICATION`
  - **User Alert Banner:** *"Insufficient technical specifications to recommend an exact Indian Standard with high confidence."*
  - **Missing Attributes Prompted:** `["product_type", "voltage_grade", "conductor_material", "insulation_type"]`
  - **Action:** User is prompted to select or type missing parameters (e.g. Low Voltage vs High Voltage, Copper vs Aluminum).
- **Judge Talking Point:** "Instead of guessing blindly and risking non-compliant procurement, our system enforces precision by requesting essential technical details."

---

## Scenario 3: QCO Mandatory Product & Clause-Level Evidence

### **Goal:** Demonstrate Quality Control Order (QCO) compliance verification and clause-level extraction.

- **Sample Procurement Input:**  
  `"Supply of outdoor 500 kVA 11kV/0.415kV oil immersed distribution transformer with Energy Efficiency Level 2."`
- **Expected System Output:**
  - **Status:** `SUCCESS`
  - **Top 1 Recommendation:** **IS 1180:Part 1** — *Outdoor Type Oil Immersed Distribution Transformers up to and including 2500 kVA, 33 kV*
  - **QCO Compliance Status:** `MANDATORY CERTIFICATION`
  - **QCO Reference:** `Ministry of Power Distribution Transformers Quality Control Order`
  - **Relevant Clause Citation:** `Clause 6.2: Energy Efficiency Standards & Losses`
- **Judge Talking Point:** "Our engine links directly to statutory Gazette notifications and specific clauses, ensuring public procurement officers comply with Quality Control Orders."

---

## Scenario 4: Multi-Attribute Complex Civil Construction Query

### **Goal:** Demonstrate Knowledge Graph traversal across materials, standards, and replacement relationships.

- **Sample Procurement Input:**  
  `"Ready mixed concrete (RMC) grade M30 using Ordinary Portland Cement 43 Grade and coarse aggregates for structural RCC slab."`
- **Expected System Output:**
  - **Status:** `SUCCESS`
  - **Primary Recommendation:** **IS 4926** — *Ready-Mixed Concrete — Code of Practice*
  - **Related Standards in Knowledge Graph:** **IS 456** (Plain and Reinforced Concrete), **IS 8112** (43 Grade OPC Cement), **IS 383** (Coarse Aggregates)
- **Judge Talking Point:** "Through our Knowledge Graph, the system not only recommends the master standard IS 4926 but also exposes the entire graph of normative references required for testing materials."

---

## Scenario 5: Out-of-Domain Safety Rejection (`out_of_domain`)

### **Goal:** Demonstrate strict domain boundaries and rejection of non-procurement or malicious queries.

- **Sample Procurement Input:**  
  `"What is the capital of India and how to write a Python fibonacci function?"`
- **Expected System Output:**
  - **Status:** `OUT_OF_DOMAIN`
  - **Message:** *"This request is outside the scope of the Indian Standards procurement recommendation system. Please enter a valid product or procurement description."*
- **Judge Talking Point:** "Our domain guardrails isolate the AI system from hallucinating or answering out-of-scope non-procurement queries, maintaining strict operational boundary control."
