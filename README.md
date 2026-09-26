# StandardSaarthi — AI-Powered Indian Standards Recommendation & Decision Support System

[![Smart India Hackathon](https://img.shields.io/badge/SIH-26108-blue.svg)](https://sih.gov.in)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An evidence-grounded decision-support platform that maps natural-language procurement specifications and tender descriptions to applicable **Indian Standards (IS codes)**, relevant technical clauses, and statutory **Quality Control Orders (QCOs)** issued under Central Ministry gazettes — complete with confidence-gated wrong-citation prevention and an official procurement officer review audit trail.

---

## 1. Problem Statement

Government departments, Public Sector Undertakings (PSUs), defense procurement wings, and municipal bodies prepare thousands of technical procurement descriptions for equipment, infrastructure, and works tenders. Under **General Financial Rules (GFR Rule 144)** and Ministry procurement directives, all public procurement tenders must mandate compliance with relevant **Indian Standards (IS codes)** and enforce statutory **Quality Control Orders (QCOs)**.

However, finding the exact applicable standard is extremely difficult:
- Procurement descriptions use natural language and commercial trade jargon (e.g., *"1.5 sq mm flame-retardant building wire"*, *"M30 ready mix concrete slab"*), whereas standards are cataloged under formal statutory nomenclature (*IS 694*, *IS 4926*).
- Crucial testing procedures, safety requirements, and material references are buried across interrelated normative standards.
- Ministry Quality Control Orders (QCOs) that mandate compulsory BIS ISI certification are fragmented across separate Central Ministry gazette notifications.

---

## 2. Impact on Officers Today

| Challenge | Impact on Procurement Officers Today |
|---|---|
| **Severe Time Drain** | Manually searching standards catalogs, trade indices, amendment sheets, and gazettes takes **3 to 5 hours per tender specification**. Across hundreds of annual tenders, this creates massive procurement bottlenecks. |
| **Wrong-Citation & Legal Risk** | Citing an incorrect, outdated, or superseded standard exposes the department to **statutory audit objections by the Comptroller and Auditor General (CAG)**, tender cancellation litigation, and contractor dispute arbitration. |
| **Regulatory Non-Compliance** | Omitting mandatory Quality Control Orders (QCOs) results in delivery of substandard or uncertified goods, violating Central Ministry statutory orders. |
| **Zero Audit Trail** | Search engines provide no decision trail. When an officer determines which standard applies or decides to override a recommendation based on project constraints, there is **no logged provenance or justification** for audit defense. |

> **Quantified Impact:** Manually cross-checking specifications against thousands of standards today takes **3 to 5 hours per tender**; **StandardSaarthi cuts this to under 45 seconds** with a verifiable primary-source citation trail and formal officer determination log (**>90% operational time reduction**).

---

## 3. Our Solution: An Evidence-Grounded Decision Support System

StandardSaarthi transforms standards discovery from an error-prone manual keyword search into an enterprise **decision-support platform**:

1. **NLP Technical Specification Understanding:** Automatically extracts product categories, materials, conductor types, voltage ratings, compressive grades, and intended applications from free text or structured schedules.
2. **Dense Vector Semantic Retrieval:** Uses 384-dimensional dense semantic vector embeddings (`SentenceTransformers all-MiniLM-L6-v2`) to capture technical intent beyond keyword matching.
3. **Normative Standards Linking:** Connects primary product standards with mandatory testing methods, safety standards, and normative references.
4. **Statutory QCO Compliance Engine:** Automatically evaluates candidate standards against gazetted Ministry Quality Control Orders to flag compulsory ISI certification directives.
5. **Confidence-Gating & Wrong-Citation Abstain Policy (Highest Priority):** When no standard clearly matches, the system refuses to force an arbitrary top-1 answer. It explicitly reports *"not confident enough"* and surfaces the closest potential candidates for officer discretion.
6. **Officer Review & Audit-Trail Layer:** Enables the reviewing procurement official to formally **ACCEPT** or **OVERRIDE** any recommendation, record mandatory statutory justification, and persist an immutable audit trail for vigilance and CAG inspection.
7. **Verifiable Evidence Provenance:** Every recommendation provides verifiable clause excerpts and direct links to official Bureau of Indian Standards (BIS) documentation.

---

## 4. System Architecture

```text
                  TENDER DOCUMENT / PROCUREMENT SPECIFICATION
                                       │
                                       ▼
                           [ Security Sanitization ]
                       (XSS, SQLi & Prompt Guardrails)
                                       │
                                       ▼
                           [ Query Guardrails Check ]
                       (Ambiguity & Scope Verification)
                                       │
                                       ▼
                         [ NLP Entity Extraction ]
                     (Product, Material, Rating, App)
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
           [ Dense Vector Retrieval ]          [ Normative Standards ]
          (SentenceTransformers MiniLM)            (Reference Graph)
                     │                                   │
                     └─────────────────┬─────────────────┘
                                       ▼
                          [ Statutory QCO Engine ]
                       (Ministry Gazette Compliance)
                                       │
                                       ▼
                           [ Hybrid Ranker Engine ]
                       (Multi-Factor Score Fusion)
                                       │
                                       ▼
                  [ Confidence Gate & Abstain Policy ]
                ┌──────────────────────┴──────────────────────┐
                │                                             │
      [ High Confidence ]                            [ Low Confidence ]
                │                                             │
                ▼                                             ▼
       Definitive Standard                           Abstain Alert:
       Recommendations + Scope                     Closest Candidates
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       ▼
                   [ Officer Review & Audit Trail Layer ]
                   - Officer Determination: ACCEPT or OVERRIDE
                   - Mandatory Statutory Justification Logging
                   - Immutable Chronological Audit Trail Register
                                       │
                                       ▼
                 [ Decision-Support Output & Official PDF Report ]
```

---

## 5. Why It Is Trustworthy for Government Use

Government procurement systems cannot rely on speculative AI. StandardSaarthi is engineered around statutory safety:

1. **Zero Hallucination Guarantee:** The system operates strictly over curated, verified database records. It never invents IS codes or fabricates standard titles.
2. **Confidence-Gated Abstain Behavior:** For ambiguous or border-line requirements, the engine explicitly reports *"Not confident enough"* and presents closest candidates instead of forcing a citation. This protects public tenders against wrong-citation liabilities.
3. **Human-in-the-Loop Officer Determination:** AI recommends, but the government officer decides. Every acceptance or override is logged with officer identity, timestamp, and required statutory reasoning.
4. **CAG-Compliant Audit Trail:** Generates a permanent, inspectable audit register (`AUDIT_<ID>`) recording who decided what, when, and on what technical basis.
5. **Primary Source Provenance:** Every cited standard links directly to official BIS portal records (`standards.bis.gov.in`) and verified gazette notifications.
6. **Enterprise Security Hardening:** Multi-layer input sanitizer rejects prompt injections, Cypher injections, SQL injections, and script tags before processing.

---

## 6. Precise Data Provenance & Scalability Roadmap

### Data Provenance
- **Current Pilot Corpus:** **120 standards manually compiled and audited from public BIS scope documentation** across the Electrical and Civil Engineering sectors, along with associated statutory Ministry Quality Control Orders.
- **Independence:** The current system operates autonomously from compiled public documentation and does **not** rely on or imply a live or private BIS API.

### Scalability Roadmap to Full 19,000+ Standards Catalogue
- **Milestone 1 (Current Pilot):** 120 verified standards across Electrical & Civil sectors with 195 multi-sector benchmark queries, confidence gating, and officer audit logging.
- **Milestone 2 (Automated Ingestion):** Automated scrapers and PDF parsers for public BIS Standards Monthlies, gazette notifications, and DPIIT Quality Control Orders to expand the verified corpus to 2,500 core procurement standards.
- **Milestone 3 (Full Catalogue Ingestion):** Scale vector indices and relational models to ingest the complete **~19,000+ active Indian Standards catalogue** across all 15 BIS Division Councils.
- **Milestone 4 (Procurement Portal Integration):** RESTful API connector directly embedding StandardSaarthi into the **Government e-Marketplace (GeM)** and **Central Public Procurement Portal (CPPP)** tender creation workflows.

---

## 7. Baseline Performance & Benchmark Facts

Empirically validated using a multi-sector benchmark covering 13 product categories:

| Metric | Measured Value | Benchmark Description |
|---|---|---|
| **Curated Pilot Standards** | 120 Verified Standards | Electrical & Civil Engineering sectors |
| **Evaluation Benchmark** | 195 Structured Queries | 13 Diverse Procurement Sectors |
| **Retrieval Speed (P50)** | `17.64 ms` | Dense vector embedding & ranking |
| **Retrieval Speed (P95)** | `24.45 ms` | Multi-factor hybrid ranking latency |
| **Ambiguity Detection Rate** | `100.0%` | Flags underspecified requirements |
| **Out-of-Domain Rejection** | `100.0%` | Blocks non-procurement queries |
| **QCO Verification Accuracy** | `77.14%` | Gazette compliance matching |
| **Time Savings per Item** | **>90%** (Hours -> <45s) | Defensible time-reduction metric |

---

## 8. Live Demonstration Scenarios

The web interface includes interactive scenarios illustrating end-to-end decision support:

1. **Scenario 1 — High-Confidence Electrical Mapping:**  
   `"Procurement of 1.5 sq mm single core PVC insulated flame retardant copper electrical cables suitable for internal building wiring."`  
   *Result:* Returns **IS 694** (High Confidence) with mandatory Ministry Quality Control Order directive.
2. **Scenario 2 — Ambiguous Procurement Guardrail:**  
   `"Requirement for electrical cable for office project."`  
   *Result:* Intercepted by query guardrail (`NEEDS_CLARIFICATION`) prompting for missing voltage, conductor material, or application specifications.
3. **Scenario 3 — Multi-Attribute Civil Construction:**  
   `"Ready mixed concrete (RMC) grade M30 using Ordinary Portland Cement 43 Grade and coarse aggregates for structural RCC slab."`  
   *Result:* Returns **IS 4926** alongside linked normative reference standards (**IS 456**, **IS 8112**, **IS 383**).
4. **Scenario 4 — Confidence-Gated Abstain Behavior (Wrong-Citation Prevention):**  
   `"Procurement of high-precision cryogenic laser isotope spectrometer for laboratory astrophysics research."`  
   *Result:* System **abstains** (`STATUS: abstain`), reports *"Not confident enough to recommend a single definitive standard"*, and displays closest candidates for officer discretion.
5. **Scenario 5 — Officer Determination & Statutory Audit Logging:**  
   The reviewing official reviews recommendations, selects **ACCEPT** or **OVERRIDE** (e.g., specifying IS 7098 (Part 1)), enters their statutory audit justification, and records the determination into the permanent audit register.
6. **Scenario 6 — Out-of-Domain Safety Rejection:**  
   `"What is the best smartphone for gaming and how to write a Python fibonacci function?"`  
   *Result:* Intercepted and rejected (`OUT_OF_DOMAIN`) without guessing arbitrary standards.

---

## 9. Quick Start Guide

### Prerequisites
- Python 3.11+
- Git

### Installation & Execution
```bash
# Clone the repository
git clone https://github.com/SIH26108/SIH26108.git
cd SIH26108

# Install dependencies
pip install -r requirements.txt

# Run Pre-Demo System Verification
python scripts/demo_check.py

# Launch Web Application & API Server
python -m api.routes
```
Open your browser at `http://localhost:8000/` to launch the enterprise dashboard.

---

## 10. License

Developed for **Smart India Hackathon (SIH 26108)** under the MIT License.
