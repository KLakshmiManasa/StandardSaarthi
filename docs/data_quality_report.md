# Data Quality & Validation Report — SIH 26108
## Phase 1 Dataset Foundation Audit

**Audit Timestamp:** 2026-09-22 18:55:50  
**Dataset Version:** v0.1-pilot  
**Status:** PASS  

---

## 1. Executive Summary & Audit Statistics

| Dataset Category | Record Count | Pilot Sectors | Data Quality Metric | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Standards Master (`standards_clean.csv`)** | 120 | Electrical (60), Civil (60) | **100% Validated** | PASS |
| **Standard Relationships (`relationships.csv`)** | 130 | Inter-standard dependencies | **100.0% Referential Integrity** | PASS |
| **QCO Compliance (`qco_compliance.csv`)** | 42 | Statutory Orders | **100% Verifiable** | PASS |
| **Procurement Queries (`procurement_queries.csv`)** | 20 | Electrical & Civil Ground Truth | **100.0% Grounded** | PASS |
| **Synthetic Queries (`synthetic_queries.csv`)** | 60 | Algorithmic Perturbations | **100% Bound to Ground Truth** | PASS |

---

## 2. Six-Vector Quality Analysis

### 1. Completeness (100.0%)
* **Check:** All mandatory fields (`is_code`, `title`, `sector`, `product_category`, `scope_text`, `last_verified_date`) must be populated.
* **Result:** 120 / 120 records contain 100% mandatory field values. Optional fields missing in source are set explicitly to `NULL` / `UNKNOWN`.

### 2. Consistency (100.0%)
* **Check:** IS Code format normalization (`IS <Number>[:Part <P>][:Sec <S>]`).
* **Result:** 100% of IS codes follow standardized prefix formatting without formatting conflicts.

### 3. Uniqueness (100.0%)
* **Check:** Duplicate standard identifier detection.
* **Result:** 120 unique IS codes out of 120 total records. Zero duplicate primary key collisions.

### 4. Validity (100.0%)
* **Check:** Allowed domain values for `status` (`ACTIVE`, `SUPERSEDED`, `WITHDRAWN`, `UNKNOWN`) and `sector` (`Electrical`, `Civil`).
* **Result:** 120 / 120 records strictly adhere to categorical constraints.

### 5. Traceability (100.0%)
* **Check:** Presence of official source URLs (`source_url`) or gazette document citations (`source_document`).
* **Result:** 120 / 120 records contain explicit primary source citations.

### 6. Ground-Truth Grounding (100.0%)
* **Check:** Ground-truth `target_is_code` in procurement queries exists in `standards_master`.
* **Result:** 20 / 20 ground-truth target standards exist in the pilot database.

---

## 3. Detailed Data Integrity Matrix

```text
+------------------------------------+---------------+----------------+---------+
| Quality Check Dimension             | Target Metric | Metric Score   | Status  |
+------------------------------------+---------------+----------------+---------+
| Mandatory Field Completeness       | >= 95.0%      | 100.0%         | PASS    |
| Primary Key Uniqueness             | 100.0%        | 100.0%        | PASS    |
| Domain Categorical Validity        | 100.0%        | 100.0%        | PASS    |
| Source Traceability                | >= 90.0%      | 100.0%        | PASS    |
| Relationship Referential Integrity | 100.0%        | 100.0%        | PASS    |
| Ground-Truth Query Grounding       | 100.0%        | 100.0%        | PASS    |
+------------------------------------+---------------+----------------+---------+
```

---

## 4. Validation Issues & Resolutions Log

1. **Format Normalization Issue:** Variations such as `IS694`, `IS-694`, and `is 694` were normalized to canonical `IS 694`.
2. **Missing Source Handling:** Missing optional parameter fields (e.g. `amendments` or `materials`) were represented explicitly as `NULL` / `[]` rather than hallucinating metadata.
3. **Synthetic Data Isolation:** Synthetic queries were segregated into `data/evaluation/synthetic_queries.csv` with `source_type = SYNTHETIC` to prevent corruption of authoritative standards data.
