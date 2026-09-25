# SIH 26108 — Scoring & Relevance Match Definition

## 1. Executive Summary

This document provides the mathematical and technical definition of the **Relevance Score** (e.g. `96% Match`) displayed in the user interface and report outputs.

---

## 2. Mathematical Definition

The Relevance Score is a **multi-factor weighted rank fusion score**, NOT a statistical prediction accuracy or probability value.

The relevance score $S_{\text{final}} \in [0.0, 1.0]$ is computed as:

$$S_{\text{final}} = w_{\text{vec}} \cdot S_{\text{vec}} + w_{\text{ent}} \cdot S_{\text{ent}} + w_{\text{graph}} \cdot S_{\text{graph}} + w_{\text{app}} \cdot S_{\text{app}} + w_{\text{qco}} \cdot I_{\text{qco}}$$

Where the default component weights are:

- $w_{\text{vec}} = 0.45$: Dense Vector Cosine Similarity Score ($S_{\text{vec}} \in [0, 1]$)
- $w_{\text{ent}} = 0.30$: NLP Entity Match Score ($S_{\text{ent}} \in [0, 1]$ based on product and material matches)
- $w_{\text{graph}} = 0.15$: Knowledge Graph Traversal Relevance Score ($S_{\text{graph}} \in [0, 1]$ based on node degree and reference depth)
- $w_{\text{app}} = 0.10$: Application Domain Alignment Score ($S_{\text{app}} \in [0.3, 1.0]$)
- $w_{\text{qco}} = 0.05$: Mandatory QCO Flag Boost ($I_{\text{qco}} \in \{0, 1\}$)

---

## 3. Score Categorization & Display

- **High Relevance (80% – 100%):** Strong alignment across vector semantics, entity attributes, and graph references. Displayed with green badge.
- **Medium Relevance (50% – 79%):** Moderate semantic alignment with partial attribute match. Displayed with yellow badge.
- **Low Relevance (< 50%):** Baseline semantic match with low attribute overlap. Displayed with gray badge.

---

## 4. Scientific Labeling Policy

- **Allowed Label in UI:** `96% Match`, `Relevance Score: 0.96`, `Confidence: HIGH`
- **Prohibited Label:** `96% Prediction Accuracy` (Accuracy is measured separately across benchmark queries).
