# SIH 26108 — Pre-Demo Final Verification Checklist

## 1. Technical Readiness Checklist
- [x] Python 3.11/3.14 environment with required packages installed.
- [x] FastAPI REST application server entry point ([api/routes.py](file:///c:/D_drive/Documents/SIH/SIH26108/api/routes.py)) tested.
- [x] Subsystem health check endpoint (`/health` & `/api/health`) returning operational status.
- [x] FAISS / SentenceTransformer dense vector index loaded.
- [x] Knowledge Graph (Neo4j / In-Memory NetworkX fallback) populated.
- [x] Ground-truth database and QCO gazette tables initialized.
- [x] Master integration pipeline ([integration/pipeline.py](file:///c:/D_drive/Documents/SIH/SIH26108/integration/pipeline.py)) verified.

---

## 2. Live Presentation Demo Checklist
- [x] Scenario 1 (Electrical Cable - IS 694) verified.
- [x] Scenario 2 (Ambiguous Query - NEEDS_CLARIFICATION) verified.
- [x] Scenario 3 (Multi-Attribute Concrete - IS 4926 & linked IS 456) verified.
- [x] Scenario 4 (QCO Transformer - IS 1180:Part 1) verified.
- [x] Scenario 5 (Out-of-Domain Smartphone Query - OUT_OF_DOMAIN) verified.
- [x] Evidence modal displaying primary source organization and official BIS URLs.

---

## 3. Presentation & Documentation Checklist
- [x] Single source of truth ([docs/project_facts.json](file:///c:/D_drive/Documents/SIH/SIH26108/docs/project_facts.json)) verified.
- [x] 10-Slide presentation content ([docs/sih_presentation.md](file:///c:/D_drive/Documents/SIH/SIH26108/docs/sih_presentation.md)) created.
- [x] 15 Judge Q&A document ([docs/sih_judge_qa.md](file:///c:/D_drive/Documents/SIH/SIH26108/docs/sih_judge_qa.md)) ready.
- [x] 3-Minute live presentation script ([docs/sih_demo_script.md](file:///c:/D_drive/Documents/SIH/SIH26108/docs/sih_demo_script.md)) prepared.
- [x] Architecture diagrams ([docs/sih_architecture.md](file:///c:/D_drive/Documents/SIH/SIH26108/docs/sih_architecture.md)) ready.

---

## 4. Backup & Fallback Checklist
- [x] Client-side backup demo mode in [frontend/app.js](file:///c:/D_drive/Documents/SIH/SIH26108/frontend/app.js) with explicit `"DEMO FALLBACK — NOT LIVE"` banner.
- [x] Demo health check script ([scripts/demo_check.py](file:///c:/D_drive/Documents/SIH/SIH26108/scripts/demo_check.py)) verified.
- [x] Pre-demo backup data files present in `data/demo/demo_scenarios.json`.
