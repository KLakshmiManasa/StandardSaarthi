# SIH 26108 — Clean-Room Setup & Reproducibility Guide

Follow this step-by-step guide to clone, install, configure, verify, and run the **AI-Powered Indian Standards Recommendation Engine** on any clean environment.

---

## 1. System Requirements

- **Operating System:** Windows 10/11, Ubuntu 20.04+, or macOS 12+
- **Python Version:** Python 3.11.x or Python 3.14.x
- **RAM:** 8 GB minimum (16 GB recommended)
- **Disk Space:** 3 GB free storage

---

## 2. Step-by-Step Setup Instructions

### Step 1: Clone Repository
```bash
git clone https://github.com/SIH26108/SIH26108.git
cd SIH26108
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Validate Data & Environment
```bash
python scripts/validate_data.py
```

### Step 5: Run Pre-Demo System Health Check
```bash
python scripts/demo_check.py
```
*Expected Output:* `OVERALL DEMO READINESS: READY FOR LIVE SIH DEMONSTRATION [READY]`

### Step 6: Start FastAPI REST Server & Web Dashboard
```bash
python -m api.routes
```
Open your web browser at `http://localhost:8000/`.

---

## 3. Testing & Evaluation Execution

### Run Full Test Suite (53 Tests)
```bash
python -m pytest
```

### Run 195-Query Benchmark Evaluation
```bash
python scripts/evaluate_phase8.py
```

### Run Concurrency Benchmark
```bash
python scripts/benchmark_performance.py
```
