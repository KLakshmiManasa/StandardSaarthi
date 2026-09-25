# The SIH 26108 Narrative — Project Story & Value Impact

## 1. Problem Statement

Government departments, Public Sector Undertakings (PSUs), procurement agencies, and private organizations prepare detailed procurement descriptions for products and services. Procurement officials must identify the applicable **Indian Standards (IS codes)** and statutory **Quality Control Orders (QCOs)** for those requirements.

Currently, finding the appropriate standard requires manual searching through dense catalogs, keywords, amendment sheets, related testing standards, and fragmented gazette notifications.

---

## 2. Existing Challenge

- **Natural Language vs Technical Terms:** Procurement requests use informal trade jargon (e.g., *"1.5 sq mm PVC wire for hospital wiring"*), whereas official standards use formal nomenclature (*"IS 694: Polyvinyl Chloride Insulated Cables"*).
- **Fragmented Regulatory Information:** Identifying whether a standard is subject to a mandatory Quality Control Order (QCO) requires cross-referencing separate Ministry gazette notifications.
- **Risk of Misalignment:** Specifying incorrect or withdrawn standards in tender documents leads to audit objections, procurement delays, and non-compliant equipment delivery.

---

## 3. Proposed Solution

An **AI-Powered Indian Standards Recommendation Engine** that unifies:

```text
Natural Language Procurement Description
                ↓
     NLP Entity Extraction
                ↓
    Vector Semantic Retrieval
                ↓
     Knowledge Graph RAG
                ↓
    QCO Gazette Matching
                ↓
       Hybrid Ranking
                ↓
 Evidence-Grounded Recommendation
```

---

## 4. Key System Outputs

- **Recommended IS Standards:** Top-ranked candidate standards with relevance confidence levels.
- **Explainable Ranking Reasons:** Transparent justification highlighting product match, material match, and application alignment.
- **QCO & Regulatory Status:** Statutory gazette references and mandatory certification badges.
- **Normative References:** Inter-linked standards required for testing and raw materials.
- **Evidence Provenance:** Verified primary source citations and official BIS URLs.

---

## 5. Potential Impact

- **Reduces Manual Discovery Effort:** Streamlines standard identification from hours of manual searching to seconds.
- **Enhances Regulatory Compliance:** Automatically flags mandatory QCO certification directives.
- **Improves Tender Specification Quality:** Ensures precise IS code and clause citations in public procurement documents.
- **Transparent & Auditable:** Provides evidence-grounded recommendations without arbitrary AI hallucinations.
