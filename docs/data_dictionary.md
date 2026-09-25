# Data Dictionary — Indian Standards Procurement Recommendation Engine
## SIH Problem Statement 26108 — Phase 1 Dataset Foundation

This document provides a comprehensive data dictionary for all data fields used in the processed standards dataset, relationship mapping, QCO compliance table, procurement query dataset, and ground-truth evaluation tables.

---

## 1. Standards Master Table (`standards_clean.csv` / `standards_clean.json` / `standards_master`)

| Field Name | Data Type | Nullable | Description & Constraints | Example Values |
| :--- | :--- | :--- | :--- | :--- |
| `is_code` | `VARCHAR(50)` | No (PK) | Canonical unique Indian Standard code identifier. Standardized format `IS <Number>[:Part <P>][:Sec <S>]`. | `IS 694`, `IS 456`, `IS 10810:Part 62` |
| `title` | `TEXT` | No | Official title of the standard as published by the Bureau of Indian Standards (BIS). | `Polyvinyl Chloride Insulated Cables for Working Voltages Up to and Including 1100 V` |
| `edition_year` | `INTEGER` | Yes | Year of standard edition/publication. Must be a 4-digit valid year (1900–2026). If unknown, `NULL`. | `2010`, `2021`, `2000` |
| `status` | `VARCHAR(20)`| No | Operational status of standard. Allowed values: `ACTIVE`, `SUPERSEDED`, `WITHDRAWN`, `UNKNOWN`. | `ACTIVE`, `SUPERSEDED` |
| `sector` | `VARCHAR(100)`| No | Primary domain sector. Allowed values in Pilot: `Electrical`, `Civil`. | `Electrical`, `Civil` |
| `product_category` | `VARCHAR(150)`| No | Sub-classification category of product/service. | `Cables and Wires`, `Cement and Concrete` |
| `scope_text` | `TEXT` | No | Verified scope clause describing application limits, ratings, and coverage. | `Covers requirements for single core and multicore PVC insulated cables...` |
| `keywords` | `TEXT[]` | Yes | Semicolon/array separated domain keywords for BM25 sparse indexing. | `PVC; copper; cable; 1100V; insulation` |
| `materials` | `TEXT` | Yes | Primary raw materials governed or specified by the standard. | `Copper, PVC, Aluminum` |
| `applications` | `TEXT` | Yes | Primary operational or structural applications. | `Internal building wiring, industrial power distribution` |
| `technical_parameters` | `TEXT` | Yes | Key rating limits, voltage ratings, compressive strength, tolerances. | `Voltage up to 1100V, temperature rating 70°C` |
| `test_methods` | `TEXT` | Yes | Directly referenced test method standard codes or clauses. | `IS 10810, IS 8130` |
| `normative_references` | `TEXT` | Yes | Mandatory referenced standard codes required for compliance. | `IS 8130, IS 10810:Part 62` |
| `installation_references` | `TEXT` | Yes | Applicable code of practice, field laying, or safety installation codes. | `IS 732` |
| `amendments` | `JSONB / TEXT` | Yes | Structured JSON array or string of active amendments. | `[{"num": 1, "year": 2013}, {"num": 2, "year": 2017}]` |
| `certification_information` | `TEXT` | Yes | Applicable BIS product certification scheme details. | `Scheme-I (ISI Mark Certification)` |
| `qco_applicability` | `VARCHAR(20)`| No | General Quality Control Order status. Allowed values: `MANDATORY`, `NOT_MANDATORY`, `UNKNOWN`. | `MANDATORY`, `UNKNOWN` |
| `source_url` | `TEXT` | Yes | URL to official BIS portal, gazette, or authoritative metadata page. | `https://www.services.bis.gov.in/...` |
| `source_document` | `TEXT` | Yes | Title/reference of public metadata source document. | `BIS Standards Catalog 2024` |
| `source_type` | `VARCHAR(30)`| No | Provenance classification. Allowed values: `PRIMARY_OFFICIAL`, `SECONDARY_GOVT`, `CURATED_PILOT`. | `PRIMARY_OFFICIAL`, `CURATED_PILOT` |
| `last_verified_date` | `DATE` | No | Date on which standard record metadata was verified (YYYY-MM-DD). | `2026-09-22` |
| `verification_status` | `VARCHAR(20)`| No | Record validation status. Allowed values: `VERIFIED`, `NEEDS_REVIEW`. | `VERIFIED`, `NEEDS_REVIEW` |

---

## 2. Standards Relationships Table (`relationships.csv` / `standard_relationships`)

| Field Name | Data Type | Nullable | Description & Constraints | Example Values |
| :--- | :--- | :--- | :--- | :--- |
| `relationship_id` | `VARCHAR(50)` | No (PK) | Unique identifier for relationship record (`REL_001`). | `REL_ELEC_001` |
| `source_is_code` | `VARCHAR(50)` | No (FK) | Originating IS code (`standards_master.is_code`). | `IS 694` |
| `target_is_code` | `VARCHAR(50)` | No (FK) | Target IS code referenced by source. | `IS 8130` |
| `relationship_type` | `VARCHAR(50)` | No | Type of dependency edge. Allowed values: `NORMATIVE_REFERENCE`, `TEST_METHOD`, `MATERIAL_SPECIFICATION`, `INSTALLATION_CODE`, `RELATED_STANDARD`, `SUPERSEDES`, `AMENDED_BY`. | `NORMATIVE_REFERENCE`, `TEST_METHOD` |
| `description` | `TEXT` | Yes | Technical context of relationship. | `Specifies conductor flexibility and resistance requirements` |
| `source` | `TEXT` | No | Citation of clause or document where reference is specified. | `IS 694:2010 Clause 5.1` |
| `verification_status` | `VARCHAR(20)`| No | `VERIFIED` or `NEEDS_REVIEW`. | `VERIFIED` |

---

## 3. QCO Compliance Table (`qco_compliance.csv` / `qco_compliance`)

| Field Name | Data Type | Nullable | Description & Constraints | Example Values |
| :--- | :--- | :--- | :--- | :--- |
| `qco_id` | `VARCHAR(50)` | No (PK) | Unique QCO record identifier (`QCO_001`). | `QCO_DPIIT_2019_01` |
| `is_code` | `VARCHAR(50)` | No (FK) | Indian Standard code subject to QCO (`standards_master.is_code`). | `IS 694` |
| `qco_title` | `TEXT` | No | Gazette title of the Quality Control Order. | `Electrical Wires, Cables, Appliances and Protection Devices (Quality Control) Order, 2019` |
| `issuing_ministry` | `TEXT` | No | Central Ministry issuing gazette notification. | `Department for Promotion of Industry and Internal Trade (DPIIT)` |
| `notification_number` | `TEXT` | No | Official Gazette S.O. / S.R.O. notification number. | `S.O. 4059(E)` |
| `notification_date` | `DATE` | Yes | Date of gazette notification (YYYY-MM-DD). | `2019-11-06` |
| `mandatory_status` | `VARCHAR(20)`| No | Statutory enforcement status. Allowed values: `MANDATORY`, `NOT_MANDATORY`, `UNKNOWN`. | `MANDATORY` |
| `effective_date` | `DATE` | Yes | Date when QCO enforcement came into effect. | `2020-05-06` |
| `source_url` | `TEXT` | Yes | Direct link to gazette notification PDF or DPIIT repository. | `https://dpiit.gov.in/qco/...` |
| `verification_status` | `VARCHAR(20)`| No | `VERIFIED` or `NEEDS_REVIEW`. | `VERIFIED` |
| `last_verified_date` | `DATE` | No | Verification timestamp (YYYY-MM-DD). | `2026-09-22` |

---

## 4. Procurement Query & Ground Truth Dataset (`procurement_queries.csv` & `ground_truth.csv`)

| Field Name | Data Type | Nullable | Description & Constraints | Example Values |
| :--- | :--- | :--- | :--- | :--- |
| `query_id` | `VARCHAR(50)` | No (PK) | Unique query identifier (`QRY_ELEC_001`). | `QRY_ELEC_001` |
| `procurement_description` | `TEXT` | No | Unstructured or semi-structured tender specification clause. | `Supply of 1.5 sq mm single core PVC insulated flame retardant copper electrical cables for internal wiring of a government hospital.` |
| `sector` | `VARCHAR(100)`| No | Sector domain (`Electrical`, `Civil`). | `Electrical` |
| `product` | `TEXT` | Yes | Extracted product name slot. | `Electrical Cable` |
| `material` | `TEXT` | Yes | Extracted material composition slot. | `Copper conductor, PVC insulation` |
| `application` | `TEXT` | Yes | Extracted functional/structural application slot. | `Internal building wiring, hospital` |
| `technical_requirements` | `TEXT` | Yes | Extracted ratings, sizes, pressure, or strength limits. | `1.5 sq mm, 1100V, Flame Retardant` |
| `environment` | `TEXT` | Yes | Operating environmental conditions. | `Indoor, fire-sensitive` |
| `target_is_code` | `VARCHAR(50)` | No | Ground-truth primary Indian Standard code. | `IS 694` |
| `related_is_codes` | `TEXT` | Yes | Semicolon-separated expected normative/test/installation IS codes. | `IS 8130; IS 10810:Part 62; IS 732` |
| `difficulty` | `VARCHAR(20)`| No | Difficulty level classification. Allowed values: `EASY`, `MEDIUM`, `HARD`. | `MEDIUM` |
| `source_type` | `VARCHAR(30)`| No | Origin of query. Allowed values: `MANUAL_VERIFIED`, `SYNTHETIC`. | `MANUAL_VERIFIED` |
| `verification_status` | `VARCHAR(20)`| No | `VERIFIED` or `NEEDS_REVIEW`. | `VERIFIED` |
