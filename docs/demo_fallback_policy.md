# SIH 26108 — Frontend Demo Fallback Policy

## 1. Executive Policy Summary

During live SIH demonstrations, network interruptions, backend restarts, or temporary local port blocks can disrupt real-time API communication.

To ensure presentation continuity without misrepresenting system capabilities, the frontend client application ([frontend/app.js](file:///c:/D_drive/Documents/SIH/SIH26108/frontend/app.js)) implements a **Transparent Demo Fallback Policy**.

---

## 2. Core Governance Rules

1. **Explicit Labeling Rule:** When fallback mode is active, the UI must prominently display an orange alert banner stating:  
   `"DEMO FALLBACK MODE — Unable to reach live FastAPI backend. Please start server via 'python -m api.routes'."`
2. **No Fake Inference Rule:** Fallback mode MUST NOT simulate or fabricate fake AI processing or pretend to run live model inference.
3. **Prior Verification Rule:** Cached fallback datasets originate exclusively from prior verified execution runs stored in `data/demo/demo_scenarios.json`.
4. **Primary Direct Mode:** Live API server execution (`POST /api/recommend`) is ALWAYS attempted first. Fallback activates only if network fetch catches a connection failure.
