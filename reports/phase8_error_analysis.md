# Phase 8 — Retrieval Error Analysis & Root Cause Audit

**Total Failures Analyzed:** 166 out of 195 queries  

## Failure Root Cause Classification (10 Categories)

1. **Uncovered Domain Standards:** Expanded sector standards (Medical, Automotive, Safety) not yet indexed in 120-standard pilot graph.
2. **Ambiguous Specifications:** Short description lacking insulation/voltage attributes correctly flagged for user clarification.
3. **Out of Domain Rejection:** Synthetic non-procurement query correctly blocked by query guardrail.
4. **Vocabulary Synonym Gap:** Procurement trade Jargon ("PVC wire") vs Official BIS title ("Polyvinyl chloride insulated cables").
5. **Multi-Attribute Weighting:** Technical rating vs product type candidate tie-breaking.
6. **Compound Query Separation:** Query requesting both transformer and switchgear simultaneously.
7. **Clause-Level Nuance:** Standard covers product line but specific sub-type clause missing.
8. **QCO Mandate Thresholding:** QCO gazette reference present in text but missing explicit BIS gazette link.
9. **Abbreviation Parsing:** Jargon acronyms ("XLPE", "HDPE") requiring domain dictionary expansion.
10. **Rank Fusion Calibration:** Candidate pool contains target standard at rank 2 or 3 rather than top 1.
