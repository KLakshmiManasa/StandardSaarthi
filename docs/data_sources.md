# Data Sources & Provenance Architecture — SIH 26108
## Phase 1 Dataset Foundation

This document outlines all authoritative, supporting, and synthetic data sources utilized in Phase 1 of the AI-Powered Indian Standards Recommendation Engine.

---

## 1. Provenance & Authority Mapping

| Data Category | Primary Source | Authority Level | Access & Retrieval Method | Verification & Integrity Method |
| :--- | :--- | :--- | :--- | :--- |
| **Indian Standards Metadata & Scope** | Bureau of Indian Standards (BIS) Portal (`services.bis.gov.in`), Sectional Committee Catalogs | Primary Official | Public catalog inspection & gazetted standard listings | Cross-verification against official BIS title records and Sectional Committee catalogs. |
| **Quality Control Orders (QCOs)** | Gazette of India & DPIIT / Ministry Portal (`dpiit.gov.in/qco`) | Primary Official Statutory | Extraordinary Gazette Notifications (S.O. / S.R.O. releases) | Notification S.O. number verification & Gazette effective date cross-checking. |
| **Normative & Test Relationships** | Published BIS Standard Clause Scope Text (e.g., Clause 2 "Normative References") | Primary Official | Clause-level inspection of public standards metadata | Direct citation of clause numbers (e.g., IS 694:2010 Clause 5.1). |
| **Procurement Specification Phrasing** | Public Procurement Summaries (GeM / CPPP Public Tenders) | Secondary Govt Support | Public tender notice inspection & open RFP summaries | Contextual review by domain engineering team. |
| **Synthetic Query Variations** | Algorithmic Query Expansion Script (`scripts/generate_queries.py`) | Synthetic (Evaluation Only) | Automated template & synonym variation generator | Every synthetic query is bound strictly to a manually verified target IS code. |

---

## 2. Distinction Between Data Tiers

### 1. Primary Official Source
Official government records, gazettes, and standards catalogs published directly by sovereign bodies (BIS, DPIIT, Ministry of Steel, Ministry of Heavy Industries). These fields form the bedrock of the standards master schema.

### 2. Secondary Govt Support Source
Public tender descriptions extracted from historical procurement notices on Government e-Marketplace (GeM) or Central Public Procurement Portal (CPPP) used to align NLP slot-fillers with real-world officer vocabulary.

### 3. Synthetic Evaluation Tier
Artificially perturbed variations of real procurement queries created strictly for stress testing algorithm robustness.
* **Strict Policy:** Synthetic records exist ONLY in `data/evaluation/synthetic_queries.csv`. They are strictly prohibited from entering the standards master table or modifying official QCO compliance tables.

---

## 3. Pilot Sectors Selection Rationale

### Sector 1: Electrical / Electrotechnical (ETD)
* **Rationale:** Electrical products (cables, switchgear, motors, transformers, lighting) represent over 35% of public procurement inquiries and are subject to widespread mandatory QCO enforcement by DPIIT. Inter-standard dependencies (Product → Material → Test Code → Installation Code) are densely connected and highly structured.

### Sector 2: Civil / Construction (CED)
* **Rationale:** Civil materials (cement, structural steel, aggregates, concrete mixes, pipes) form the core of CPWD and PWD infrastructure tenders. Standards such as IS 456 (Concrete) and IS 1786 (Rebar) possess extensive normative references and rigid testing methods.
