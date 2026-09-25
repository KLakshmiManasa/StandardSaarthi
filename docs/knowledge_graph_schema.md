# Indian Standards Knowledge Graph Schema Documentation
## SIH Problem Statement 26108 — Phase 4 Specification

This document details the formal graph data model, node types, properties, relationship labels, Cypher DDL constraints, and provenance specifications for the Indian Standards Knowledge Graph.

---

## 1. Graph Entity (Node) Schemas

### 1. `STANDARD` Node
Represents an officially published Bureau of Indian Standards (BIS) standard.
* **Primary Key Constraint:** `is_code` (Unique)
* **Properties:**
  * `is_code` (`STRING`): Standard identifier (e.g. `"IS 694"`).
  * `title` (`STRING`): Official title of the standard.
  * `edition_year` (`INTEGER`): Publication edition year.
  * `status` (`STRING`): Operational status (`ACTIVE`, `SUPERSEDED`, `WITHDRAWN`, `UNKNOWN`).
  * `sector` (`STRING`): Sector domain (`Electrical`, `Civil`).
  * `product_category` (`STRING`): Sub-classification category.
  * `scope_text` (`STRING`): Verified scope clause text.
  * `source_url` (`STRING`): Link to official BIS portal catalog.
  * `source_document` (`STRING`): Reference metadata document.
  * `verification_status` (`STRING`): Validation status (`VERIFIED`).
  * `last_verified_date` (`STRING`): YYYY-MM-DD timestamp.

### 2. `PRODUCT` Node
Represents a product, equipment, or service specified by a standard.
* **Primary Key Constraint:** `normalized_name` (Unique)
* **Properties:** `name` (`STRING`), `category` (`STRING`), `normalized_name` (`STRING`).

### 3. `MATERIAL` Node
Represents a base raw material governed or used in standard specifications.
* **Primary Key Constraint:** `normalized_name` (Unique)
* **Properties:** `name` (`STRING`), `normalized_name` (`STRING`).

### 4. `APPLICATION` Node
Represents a functional, structural, or environmental application domain.
* **Primary Key Constraint:** `normalized_name` (Unique)
* **Properties:** `name` (`STRING`), `normalized_name` (`STRING`).

### 5. `TEST_METHOD` Node
Represents a specific test parameter or laboratory procedure.
* **Primary Key Constraint:** `normalized_name` (Unique)
* **Properties:** `name` (`STRING`), `normalized_name` (`STRING`), `reference` (`STRING`).

### 6. `AMENDMENT` Node
Represents an official gazette amendment issued for a standard.
* **Primary Key Constraint:** `amendment_id` (Unique)
* **Properties:** `amendment_id` (`STRING`), `number` (`INTEGER`), `year` (`INTEGER`), `source_url` (`STRING`), `verification_status` (`STRING`).

### 7. `QCO` Node
Represents a statutory Quality Control Order issued by a Central Ministry.
* **Primary Key Constraint:** `qco_id` (Unique)
* **Properties:** `qco_id` (`STRING`), `qco_title` (`STRING`), `notification_number` (`STRING`), `issuing_ministry` (`STRING`), `notification_date` (`STRING`), `mandatory_status` (`STRING`), `effective_date` (`STRING`), `source_url` (`STRING`), `verification_status` (`STRING`).

### 8. `AUTHORITY` Node
Represents a sovereign Ministry or issuing authority.
* **Primary Key Constraint:** `normalized_name` (Unique)
* **Properties:** `name` (`STRING`), `normalized_name` (`STRING`).

---

## 2. Graph Relationship (Edge) Schemas

| Relationship Type | Source Node | Target Node | Provenance Properties | Description |
| :--- | :--- | :--- | :--- | :--- |
| `:SPECIFIES_PRODUCT` | `STANDARD` | `PRODUCT` | `verification_status`, `source` | Specifies product design/manufacturing requirements. |
| `:USES_MATERIAL` | `STANDARD` | `MATERIAL` | `verification_status`, `source` | Specifies raw material requirements. |
| `:APPLIES_TO` | `STANDARD` | `APPLICATION` | `verification_status`, `source` | Identifies applicable structural/functional domain. |
| `:TESTED_BY` | `STANDARD` | `TEST_METHOD` | `verification_status`, `source` | Specifies required test method procedure. |
| `:NORMATIVE_REFERENCE` | `STANDARD` | `STANDARD` | `source_clause`, `verification_status` | Mandatory cross-referenced standard required for compliance. |
| `:TEST_METHOD_REFERENCE` | `STANDARD` | `STANDARD` | `source_clause`, `verification_status` | Referenced standard specifically providing test procedures. |
| `:MATERIAL_SPECIFICATION` | `STANDARD` | `STANDARD` | `source_clause`, `verification_status` | Referenced standard specifying raw material parameters. |
| `:INSTALLATION_REFERENCE` | `STANDARD` | `STANDARD` | `source_clause`, `verification_status` | Code of practice for field installation and safety. |
| `:RELATED_STANDARD` | `STANDARD` | `STANDARD` | `source_clause`, `verification_status` | Supporting or domain-adjacent standard. |
| `:SUPERSEDES` | `STANDARD` | `STANDARD` | `source_clause`, `verification_status` | Standard replacing an obsolete standard edition. |
| `:AMENDED_BY` | `STANDARD` | `AMENDMENT` | `verification_status`, `source` | Active amendment issued for the standard. |
| `:ASSOCIATED_WITH_QCO` | `STANDARD` | `QCO` | `verification_status`, `source` | Statutory Quality Control Order associated with standard. |
| `:ISSUED_BY` | `QCO` | `AUTHORITY` | `verification_status`, `source` | Ministry issuing gazette QCO. |

---

## 3. Cypher DDL Constraints (Neo4j)

```cypher
CREATE CONSTRAINT std_is_code_unique IF NOT EXISTS FOR (s:STANDARD) REQUIRE s.is_code IS UNIQUE;
CREATE CONSTRAINT prod_name_unique IF NOT EXISTS FOR (p:PRODUCT) REQUIRE p.normalized_name IS UNIQUE;
CREATE CONSTRAINT mat_name_unique IF NOT EXISTS FOR (m:MATERIAL) REQUIRE m.normalized_name IS UNIQUE;
CREATE CONSTRAINT app_name_unique IF NOT EXISTS FOR (a:APPLICATION) REQUIRE a.normalized_name IS UNIQUE;
CREATE CONSTRAINT test_name_unique IF NOT EXISTS FOR (t:TEST_METHOD) REQUIRE t.normalized_name IS UNIQUE;
CREATE CONSTRAINT amd_id_unique IF NOT EXISTS FOR (am:AMENDMENT) REQUIRE am.amendment_id IS UNIQUE;
CREATE CONSTRAINT qco_id_unique IF NOT EXISTS FOR (q:QCO) REQUIRE q.qco_id IS UNIQUE;
CREATE CONSTRAINT auth_name_unique IF NOT EXISTS FOR (au:AUTHORITY) REQUIRE au.normalized_name IS UNIQUE;
```
