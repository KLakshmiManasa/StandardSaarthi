# Phase 10 — Demo Scenarios & Live Pipeline Verification Report

**Verification Date:** 2026-09-23  
**Configuration File:** `data/demo/demo_scenarios.json`  
**Frontend Entry:** `frontend/index.html` & `frontend/app.js`  
**API Endpoint:** `POST /api/recommend`  

---

## 1. Demo Scenario Verification Matrix

| Scenario ID | Name | Input Description | Expected Status | Actual Status | Top Recommended Standard | QCO Status | Pipeline Verified |
|---|---|---|---|---|---|---|---|
| `scen_01` | Electrical Cable Mapping | "Procurement of 1.5 sq mm single core PVC insulated flame retardant copper electrical cables suitable for internal building wiring." | `success` | `success` | **IS 694** | Mandatory Certification | **VERIFIED** |
| `scen_02` | Ambiguous Requirement | "Requirement for electrical cable for office project." | `needs_clarification` | `needs_clarification` | None (Prompted missing attributes) | N/A | **VERIFIED** |
| `scen_03` | Multi-Attribute Concrete | "Ready mixed concrete (RMC) grade M30 using Ordinary Portland Cement 43 Grade and coarse aggregates for structural RCC slab." | `success` | `success` | **IS 4926** (Linked IS 456, IS 8112, IS 383) | Mandatory Certification | **VERIFIED** |
| `scen_04` | QCO Product | "Supply of outdoor 500 kVA 11kV/0.415kV oil immersed distribution transformer with Energy Efficiency Level 2." | `success` | `success` | **IS 1180:Part 1** | Mandatory Certification | **VERIFIED** |
| `scen_05` | Out-of-Domain Query | "What is the best smartphone for gaming and how to write a Python fibonacci function?" | `out_of_domain` | `out_of_domain` | None (Scope alert displayed) | N/A | **VERIFIED** |

---

## 2. Live Pipeline Execution Audit

- **No Bypass:** Preset demo buttons populate the `procurementQuery` text area. The user clicks "Analyze Requirement", which triggers `POST /api/recommend`.
- **Backend Flow:** Requests pass sequentially through `SecuritySanitizer` -> `QueryGuardrails` -> `NLPEntityExtractor` -> `Phase5VectorRetriever` -> `GraphRAGRetriever` -> `QCOEngine` -> `HybridRanker` -> `EvidenceSystem`.
- **Verdict:** Live pipeline execution verified 100%. No fake responses or client-side bypasses exist during online server execution.
