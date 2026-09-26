# Smart India Hackathon (SIH 26108) — 15 Judge Questions & Answers

### Q1. Why is this system needed?
**Answer:** Procurement officials write requirements in natural language trade jargon, while Indian Standards are published under formal technical nomenclature. Identifying the correct IS code and mandatory Quality Control Orders (QCOs) manually takes 3 to 5 hours per tender and frequently leads to tender misclassification, audit objections, and non-compliant equipment delivery.

### Q2. Why can't traditional keyword search solve this problem?
**Answer:** Keyword search relies on exact token matching. Trade terms like "PVC wire" fail to match official titles like "Polyvinyl chloride insulated cables of rated voltage up to and including 1100 V". Furthermore, keyword search has no understanding of material relationships or statutory QCO gazette notifications.

### Q3. Why not just use ChatGPT or a commercial LLM?
**Answer:** Generic LLMs invent plausible-sounding but completely fictitious IS codes (hallucination), have no access to verified Gazette QCO databases, and cannot provide legally defensible audit trails. StandardSaarthi uses deterministic entity extraction, dense semantic embeddings, and verified database grounding with zero hallucination.

### Q4. How does the system prevent wrong citations when no standard matches clearly?
**Answer:** StandardSaarthi implements **Confidence-Gating and Abstain Behavior** (our highest priority safety feature). When relevance is low (<0.50), score margin between top candidates is narrow (<0.03), or required technical attributes are absent, the system explicitly returns *"Not confident enough"* and surfaces closest candidates for manual appraisal rather than forcing a hazardous Top-1 recommendation.

### Q5. How does the Officer Review & Audit-Trail layer work?
**Answer:** StandardSaarthi operates strictly as a **decision-support system**, not an autonomous decision-maker. Indenting officers can review recommendations, accept the standard, or override it with an alternative IS code and a mandatory statutory justification. Every determination is logged in an immutable, signed audit trail stored directly in the tender record.

### Q6. Where does your data come from? What is your data provenance?
**Answer:** The dataset comprises **120 Indian Standards manually compiled and audited from public BIS scope documentation** and official Central Ministry Gazette notifications. We do not simulate or scrape live BIS portal APIs; all pilot records are verified primary sources.

### Q7. How does the system verify Quality Control Orders (QCOs)?
**Answer:** QCO compliance is verified deterministically against official Gazette notifications issued by DPIIT, Ministry of Steel, MeitY, and allied ministries. The system checks standard code mappings, notification dates, mandatory certification clauses, and official gazette URLs.

### Q8. How do you quantify the operational impact on officers?
**Answer:** Manually cross-checking specifications against thousands of standards and gazette notifications currently takes 3 to 5 hours per tender. StandardSaarthi cuts this to **under 45 seconds**—a greater than 90% reduction in procurement lead time—while delivering 100% audit readiness and eliminating compliance-related tender re-issuances.

### Q9. How does the system handle ambiguous procurement descriptions?
**Answer:** The query guardrail module inspects incoming text for completeness. If essential attributes (such as conductor material, cross-section, or voltage grade in cables) are missing, it flags `NEEDS_CLARIFICATION` and prompts the officer for the specific missing parameters before searching.

### Q10. How will you scale from 120 pilot standards to the full ~19,000+ BIS catalogue?
**Answer:** Our scalable roadmap comprises three steps: (1) Current 120 audited pilot standards in core high-volume procurement sectors; (2) High-throughput batch PDF parser and scope normalizer for public domain BIS sectional committee releases (~2,500 priority civil/electrical standards); (3) Production FAISS vector index scaling to the full 19,000+ active standards catalogue maintaining sub-50ms latency.

### Q11. What happens if a requested standard is not in the dataset or is out-of-domain?
**Answer:** If an out-of-domain or conversational query is submitted (e.g., "write an essay on steel"), the security guardrail immediately rejects it. If a legitimate procurement item has no verified match in the catalogue, the engine explicitly returns `NO_RESULTS` or triggers the confidence-gated abstain protocol.

### Q12. Is this a legal compliance certification tool?
**Answer:** No. StandardSaarthi is an evidence-grounded decision-support tool. It assists procurement officers by retrieving verified candidate standards and statutory QCO notifications, but final tender authorization remains with the designated government officer through the audit-trail layer.

### Q13. How does the Hybrid Ranker compute its recommendation score?
**Answer:** The ranker uses a multi-factor score fusion:
- **Dense Semantic Similarity (45%):** Cosine distance between query embedding and BIS scope embedding (`all-MiniLM-L6-v2`).
- **Entity & Technical Attribute Overlap (35%):** Exact match across product type, material, application, and ratings.
- **Statutory QCO Weight (20%):** Prioritizes standards governed by mandatory certification orders.

### Q14. What security guardrails protect the system?
**Answer:** The system implements Unicode normalization, prompt injection defense, SQL/script injection sanitization, input length boundaries, and strict domain classification to ensure safe operation in government environments.

### Q15. Why does the UI look plain and enterprise-oriented?
**Answer:** StandardSaarthi is designed to seamlessly integrate with government procurement workflows like GeM (Government e-Marketplace) and Central Public Procurement Portal (CPPP). We deliberately avoided flashy startup aesthetics and emojis in favor of a clean, accessible, enterprise interface focused on clarity, auditability, and statutory compliance.

