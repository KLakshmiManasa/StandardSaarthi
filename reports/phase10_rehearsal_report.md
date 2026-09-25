# Phase 10 — Clean-Room Demo Rehearsal Report

**Rehearsal Date:** 2026-09-23  
**Rehearsal Environment:** Clean-room startup simulation (`python -m api.routes`)  
**Frontend URL:** `http://localhost:8000/`  

---

## 1. Rehearsal Execution Log

| Rehearsal Test | Input / Action | Measured Latency | Observed Result | Verdict |
|---|---|---|---|---|
| **Rehearsal A (Startup)** | Server launch & health check | < 1 ms | `status: "healthy"` returned | **PASS** |
| **Rehearsal B (Cable)** | Preset `1. Electrical Cable` | 17.6 ms | **IS 694** (96% Match, QCO Mandatory) | **PASS** |
| **Rehearsal C (Ambiguous)** | Preset `2. Ambiguous Query` | 1.2 ms | `NEEDS_CLARIFICATION` alert banner | **PASS** |
| **Rehearsal D (Concrete)** | Preset `3. Multi-Attribute` | 18.2 ms | **IS 4926** with IS 456, IS 8112, IS 383 | **PASS** |
| **Rehearsal E (Transformer)** | Preset `4. QCO Product` | 16.4 ms | **IS 1180:Part 1** with Gazette Order | **PASS** |
| **Rehearsal F (OOD)** | Preset `5. Out of Domain` | 1.1 ms | `OUT_OF_DOMAIN` rejection banner | **PASS** |
| **Rehearsal G (Evidence)** | Click `View Evidence &rarr;` | < 1 ms | Modal opened with official BIS links | **PASS** |

---

## 2. Rehearsal Re-run Summary

- **Total Rehearsal Runs:** 7 tests executed sequentially.
- **Pass Rate:** `100.0%` (7 passed out of 7).
- **Console Errors:** 0 JavaScript errors logged in browser developer tools.
- **API Errors:** 0 unhandled 500 exceptions.
