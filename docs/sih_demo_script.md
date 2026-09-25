# Smart India Hackathon (SIH 26108) — 3-Minute Live Presentation Script

## 0:00–0:30 — Problem & Context
**Speaker:** "Respected judges, public procurement officers write procurement descriptions in natural language trade terms, but must specify accurate Indian Standards (IS codes) and Quality Control Orders in tender documents. Finding the right standard manually across dense catalogs and gazettes is slow, error-prone, and risks audit non-compliance. Our solution is the **AI-Powered Indian Standards Recommendation Engine**."

---

## 0:30–1:00 — Live Demonstration (Scenario 1: Electrical Cable)
**Speaker:** "Let's select our first demo scenario: *'Procurement of 1.5 sq mm single core PVC insulated flame retardant copper electrical cables for internal building wiring.'* Notice how we click 'Analyze Requirement'. In 17 milliseconds, the system extracts the product, category, materials, and application."

---

## 1:00–1:30 — Core Recommendation & QCO Verification
**Speaker:** "The system recommends **IS 694** with a 96% relevance match. Crucially, the QCO Engine automatically flags that this standard is governed by a **Mandatory Quality Control Order** from the official Gazette. Clicking 'View Evidence' opens verifiable BIS source citations and relevant scope clauses."

---

## 1:30–2:00 — Multi-Attribute Knowledge Graph Traversal (Scenario 3)
**Speaker:** "Next, let's look at Scenario 3: *'Ready mixed concrete grade M30 using OPC 43 Grade cement and coarse aggregates.'* The engine recommends **IS 4926**, but also uses our Knowledge Graph to expose linked normative references: IS 456 for structural concrete, IS 8112 for cement, and IS 383 for coarse aggregates."

---

## 2:00–2:30 — Robustness & Safety Guardrails (Scenarios 2 & 5)
**Speaker:** "What happens if a query is vague, like *'Requirement for electrical cable for office project'*? The system does NOT guess blindly—it triggers **Needs Clarification** and prompts the user for missing voltage and conductor parameters. And if someone asks an out-of-domain query like *'What is the best smartphone for gaming?'*, our guardrails return **Out of Domain** without returning random standards."

---

## 2:30–3:00 — Empirical Benchmarks & Impact
**Speaker:** "We benchmarked our engine across 195 multi-sector queries with a P50 latency of 17.6 ms and 100% guardrail accuracy. In summary, our system reduces search effort, ensures statutory QCO compliance, and provides transparent, evidence-grounded recommendations. Thank you!"
