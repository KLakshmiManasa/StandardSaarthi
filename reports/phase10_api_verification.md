# Phase 10 — API Endpoints Verification Report

**Verification Date:** 2026-09-23  
**Application File:** [api/routes.py](file:///c:/D_drive/Documents/SIH/SIH26108/api/routes.py)  
**Schema File:** [integration/schemas.py](file:///c:/D_drive/Documents/SIH/SIH26108/integration/schemas.py)  

---

## 1. REST Endpoints Audit Table

| HTTP Method | Endpoint Path | Description | Status Code | Test Verification |
|---|---|---|---|---|
| `POST` | `/api/recommend` | Main recommendation endpoint executing 8-stage pipeline | `200 OK` (or 400, 422, 403) | **VERIFIED** |
| `GET` | `/health` | Subsystem readiness monitor | `200 OK` | **VERIFIED** |
| `GET` | `/api/health` | Subsystem readiness monitor alias | `200 OK` | **VERIFIED** |
| `GET` | `/eval` | Serves internal evaluation dashboard HTML view | `200 OK` | **VERIFIED** |
| `GET` | `/api/evaluation/report` | Returns latest benchmark evaluation report JSON | `200 OK` | **VERIFIED** |
| `GET` | `/` | Static frontend search interface | `200 OK` | **VERIFIED** |

---

## 2. API Contract Verification Details

1. **Structured Request Schema (`RecommendRequest`):**
   - `description`: String (1 to 2000 chars)
   - `top_k`: Integer (default 10)
   - `mode`: String (`graph_rag`, `vector`, `keyword`)
2. **Structured Response Schema (`RecommendationResponse`):**
   - `status`: String (`success`, `needs_clarification`, `out_of_domain`, `security_blocked`, `no_results`)
   - `query`: String
   - `entities`: Object (`product`, `category`, `materials`, `application`)
   - `recommendations`: Array of recommendation objects
   - `processing`: Metadata (`latency_ms`, `candidate_count`, `engine_version`)
