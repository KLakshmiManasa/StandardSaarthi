# Phase 4 — Indian Standards Knowledge Graph Documentation

## Executive Summary
Phase 4 constructs a structured, domain-grounded Knowledge Graph representing Indian Standards (IS codes), products, raw materials, engineering applications, test methods, amendments, Quality Control Orders (QCOs), and issuing regulatory authorities.

The Knowledge Graph enhances Phase 3 statistical search and ranking candidates by performing controlled graph traversals to expand candidates with mandatory normative references, material specifications, test procedure dependencies, active amendments, and regulatory QCO compliance obligations.

---

## 1. Graph Architecture & Dual-Store Design

The system implements a **Dual-Mode GraphStore**:
1. **Neo4j Enterprise Graph Engine (Production):** High-performance Cypher query execution via official `neo4j` Python driver.
2. **In-Memory Graph Engine (Development/CI/Fallback):** High-efficiency Python indexing dictionary with 0 external network/server overhead.

### Graph Statistics
* **Total Nodes:** 504
  * `STANDARD`: 120 (60 Electrical, 60 Civil)
  * `PRODUCT`: 73
  * `MATERIAL`: 65
  * `APPLICATION`: 136
  * `TEST_METHOD`: 30
  * `AMENDMENT`: 35
  * `QCO`: 42
  * `AUTHORITY`: 3 (BIS, DPIIT, MoP)
* **Total Relationships/Edges:** 1,340
  * `SPECIFIES_PRODUCT`: 120
  * `USES_MATERIAL`: 537
  * `APPLIES_TO`: 169
  * `TESTED_BY`: 265
  * `AMENDED_BY`: 35
  * `MATERIAL_SPECIFICATION`: 22
  * `TEST_METHOD`: 8
  * `ASSOCIATED_WITH_QCO`: 42
  * `NORMATIVE_REFERENCE`: 89
  * `INSTALLATION_CODE`: 11
  * `ISSUED_BY`: 42

---

## 2. Query Capabilities & Cypher Patterns

The graph supports 9 core standard and relationship query patterns:

1. **Query 1 (Lookup Standard by Code):**
   `MATCH (s:STANDARD {is_code: $is_code}) RETURN s`
2. **Query 2 (Outgoing Relationships):**
   `MATCH (s:STANDARD {is_code: $is_code})-[r]->(target) RETURN type(r), target, properties(r)`
3. **Query 3 (Product Standards):**
   `MATCH (s:STANDARD)-[:SPECIFIES_PRODUCT]->(p:PRODUCT {normalized_name: $product}) RETURN s`
4. **Query 4 (Material Standards):**
   `MATCH (s:STANDARD)-[:USES_MATERIAL]->(m:MATERIAL {normalized_name: $material}) RETURN s`
5. **Query 5 (Application Standards):**
   `MATCH (s:STANDARD)-[:APPLIES_TO]->(a:APPLICATION {normalized_name: $app}) RETURN s`
6. **Query 6 (Referenced Standards):**
   `MATCH (s:STANDARD {is_code: $is_code})-[r:NORMATIVE_REFERENCE|TEST_METHOD_REFERENCE|MATERIAL_SPECIFICATION|INSTALLATION_REFERENCE]->(target:STANDARD) RETURN target, type(r), properties(r)`
7. **Query 7 (Referencing Standards):**
   `MATCH (source:STANDARD)-[r]->(s:STANDARD {is_code: $is_code}) RETURN source, type(r)`
8. **Query 8 (Active Amendments):**
   `MATCH (s:STANDARD {is_code: $is_code})-[:AMENDED_BY]->(a:AMENDMENT) RETURN a`
9. **Query 9 (Associated QCOs & Authority):**
   `MATCH (s:STANDARD {is_code: $is_code})-[:ASSOCIATED_WITH_QCO]->(q:QCO)-[:ISSUED_BY]->(auth:AUTHORITY) RETURN q, auth`

---

## 3. Controlled Graph Traversals & Candidate Expansion

### 1-Hop and 2-Hop Traversals
* **1-Hop Traversal:** Examines all immediate outgoing/incoming entity and standard edges.
* **2-Hop Traversal (`traverse_two_hop`):** Performs controlled multi-step traversal with configurable branching limits (`max_branch=10`) to prevent graph combinatorial explosion while discovering indirect dependencies (e.g. `IS 694` -> `IS 8130` -> `annealed_copper`).

### Candidate Graph Expansion Engine (`CandidateGraphExpander`)
Passes Phase 3 candidate list through graph expansion:
* Identifies normative standards linked via `NORMATIVE_REFERENCE`, `TEST_METHOD`, `MATERIAL_SPECIFICATION`, or `INSTALLATION_CODE`.
* Extracts amendment counts and QCO compliance status per primary candidate.
* Demarcates graph-derived standards with evidence source and verification status.

---

## 4. REST API Endpoints

* **`GET /api/standards/{is_code}/graph`**
  Returns node attributes, outgoing relationships, active amendments, QCO status, and frontend visualization JSON (`nodes`, `edges`).
* **`POST /api/graph/expand`**
  Accepts candidate IS codes list (e.g., `{"is_codes": ["IS 694", "IS 456"], "depth": 1}`) and returns full graph-derived evidence bundle.

---

## 5. Quality Audit & Automated Integrity Verification

Automated audit script (`knowledge_graph.validation.validate_graph`):
* **Status:** `PASS`
* **Referential Integrity:** `100.0%`
* **Orphan Standards:** `0`
* **Broken References:** `0`
* **Duplicate Nodes:** `0` (within label namespaces)
* **Report Output:** `outputs/graph_validation_report.json`

---

## 6. Unit Testing Suite

Executed via `python -m pytest knowledge_graph/tests/`:
* `test_nodes.py`: Node loading & attribute verification (2 tests)
* `test_relationships.py`: Standard references & QCO associations (2 tests)
* `test_traversal.py`: 1-Hop, 2-Hop, and expansion tests (3 tests)
* **Result:** `7 passed in 0.10s` (100% PASS rate).
