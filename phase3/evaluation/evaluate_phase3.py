"""
SIH 26108 — Master Phase 3 Evaluation & Documentation Pipeline
Runs complete ablation benchmarks, rank movement analysis, difficulty breakdown, error analysis,
saves outputs/phase3_evaluation_results.json, and generates docs/phase3.md.
"""

import os
import json
import time
from typing import Dict, Any
from phase3.ranking.final_ranker import Phase3FinalRanker
from phase2.retrieval.result_formatter import format_search_response
from phase3.evaluation.ablation import run_ablation_experiments
from phase3.evaluation.rank_analysis import run_rank_analysis
from phase3.evaluation.error_analysis import analyze_errors_and_degradations

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
EVAL_JSON = os.path.join(OUTPUTS_DIR, 'phase3_evaluation_results.json')
SAMPLE_JSON = os.path.join(OUTPUTS_DIR, 'phase3_sample_results.json')
DOCS_MD = os.path.join(DOCS_DIR, 'phase3.md')

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

def run_master_phase3_evaluation():
    print("[*] Starting Master Phase 3 Evaluation Pipeline...")

    # 1. Run Ablation Experiments
    print("  [1/4] Running 6-Way Ablation Experiments...")
    ablation_res = run_ablation_experiments(k=5)

    # 2. Run Rank Movement & Difficulty Analysis
    print("  [2/4] Running Ground-Truth Rank Shift & Difficulty Analysis...")
    rank_res = run_rank_analysis()

    # 3. Run Error Analysis
    print("  [3/4] Running Error & Degraded Query Analysis...")
    error_res = analyze_errors_and_degradations()

    # 4. Measure Response Latency Breakdown & Generate Sample Results
    print("  [4/4] Measuring Pipeline Performance Latency & Generating Sample Results...")
    ranker = Phase3FinalRanker()

    sample_queries = [
        "Supply of PVC insulated copper electrical cables for internal building wiring",
        "53 Grade Ordinary Portland Cement (OPC 53) bags for precast flyover girder casting",
        "High Strength Deformed Fe 500D TMT steel rebar for RCC column structural reinforcement",
        "PE-100 PN-10 High Density Polyethylene (HDPE) pressure pipes for rural drinking water distribution",
        "ISMB 300 beams and ISMC 200 channels in E250 structural steel grade",
        "11 kV 3-core 185 sq mm XLPE insulated armored aluminum conductor underground power cables",
        "Outdoor 500 kVA 11kV/0.415kV oil immersed distribution transformer with Energy Level 2",
        "Chemical earthing electrode system with copper plate for ICU electrical earth safety",
        "10 kVA single phase online uninterruptible power supply (UPS) system for data center",
        "4-pole 63A 30mA residual current circuit breaker (RCCB) for human shock protection"
    ]

    sample_results = []
    latencies_list = []

    for sq in sample_queries:
        res = ranker.search(sq, top_k=5)
        latencies_list.append(res['latencies_ms'])
        formatted = format_search_response(res)
        sample_results.append(formatted)

    avg_latencies = {
        "bm25_ms": round(sum(l['bm25'] for l in latencies_list) / len(latencies_list), 2),
        "semantic_ms": round(sum(l['semantic'] for l in latencies_list) / len(latencies_list), 2),
        "rrf_ms": round(sum(l['rrf'] for l in latencies_list) / len(latencies_list), 2),
        "reranker_ms": round(sum(l['reranker'] for l in latencies_list) / len(latencies_list), 2),
        "metadata_ms": round(sum(l['metadata'] for l in latencies_list) / len(latencies_list), 2),
        "total_ms": round(sum(l['total'] for l in latencies_list) / len(latencies_list), 2)
    }

    # Save Output JSONs
    master_eval_output = {
        "dataset_version": "v0.1-pilot",
        "ablation_experiments": ablation_res,
        "rank_movement_analysis": {
            "total_queries": rank_res['total_queries'],
            "improved_count": rank_res['improved_count'],
            "improved_pct": rank_res['improved_pct'],
            "unchanged_count": rank_res['unchanged_count'],
            "unchanged_pct": rank_res['unchanged_pct'],
            "degraded_count": rank_res['degraded_count'],
            "degraded_pct": rank_res['degraded_pct'],
            "avg_rank_before_phase2": rank_res['avg_rank_before_phase2'],
            "avg_rank_after_phase3": rank_res['avg_rank_after_phase3'],
            "median_rank_before_phase2": rank_res['median_rank_before_phase2'],
            "median_rank_after_phase3": rank_res['median_rank_after_phase3']
        },
        "difficulty_breakdown": rank_res['difficulty_summary'],
        "error_analysis": error_res,
        "average_latencies_ms": avg_latencies
    }

    with open(EVAL_JSON, 'w', encoding='utf-8') as f:
        json.dump(master_eval_output, f, indent=2)

    with open(SAMPLE_JSON, 'w', encoding='utf-8') as f:
        json.dump(sample_results, f, indent=2)

    print(f"[OK] Saved Evaluation Results -> {EVAL_JSON}")
    print(f"[OK] Saved Sample Results -> {SAMPLE_JSON}")

    # Generate Markdown Documentation
    doc_markdown = f"""# Phase 3 — Advanced Retrieval and Ranking Engine Documentation
## SIH Problem Statement 26108 — Technical Specification & Benchmark Report

---

## 1. Executive Summary & Objective
Phase 3 builds an advanced multi-stage candidate retrieval, fusion, reranking, and metadata-aware scoring pipeline for the **AI-Powered Indian Standards Recommendation Engine**. It transitions from candidate discovery ("What standards might be relevant?") to precise relevance ranking ("Which retrieved standards are most relevant to the procurement description?").

---

## 2. End-to-End System Architecture

```text
                     Procurement Query Text
                               │
                    [ Preprocessing Pipeline ]
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       [ BM25 Lexical Engine ]    [ SentenceTransformers Dense ]
             (Top 50)                      (Top 50)
                │                             │
                └──────────────┬──────────────┘
                               ▼
                [ Reciprocal Rank Fusion (k=60) ]
                               │
                      Top 30 Candidates
                               ▼
                [ Cross-Encoder Reranker ]
            ('cross-encoder/ms-marco-MiniLM-L-6-v2')
                               │
                               ▼
                [ Structured Metadata Scoring ]
            (Sector + Product + Material + App + Tech)
                               │
                               ▼
                [ Multi-Factor Final Ranking ]
           Final = 0.60*Reranker + 0.25*RRF + 0.15*Metadata
                               │
                               ▼
               [ Deduplicated Top-K Results ]
```

---

## 3. Configuration & Reproducibility (`config/phase3_config.yaml`)
* **BM25 & Semantic Pool Size ($N$):** 50 candidates each
* **RRF Constant ($k$):** 60
* **Cross-Encoder Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2` (Top 30 candidate pairs)
* **Metadata Scoring Weights:** Sector (0.10), Product Category (0.30), Material (0.20), Application (0.25), Technical Parameters (0.15)
* **Final Ranking Weights:** Alpha (Reranker) = 0.60, Beta (RRF Norm) = 0.25, Gamma (Metadata) = 0.15 (Total Weight = 1.0)

---

## 4. 6-Way Ablation Benchmark Results ($K=5$)

Evaluated over **20 verified Phase 1 ground-truth procurement queries**:

| Retrieval / Ranking Configuration | Precision@5 | Recall@5 | Hit Rate@5 | MRR (Mean Reciprocal Rank) |
| :--- | :--- | :--- | :--- | :--- |
| **1. BM25 Lexical** | {ablation_res['BM25']['precision_at_5']} | {ablation_res['BM25']['recall_at_5']} | **{ablation_res['BM25']['hit_rate_at_5']*100:.1f}%** | {ablation_res['BM25']['mrr']} |
| **2. Semantic Search** | {ablation_res['Semantic']['precision_at_5']} | {ablation_res['Semantic']['recall_at_5']} | **{ablation_res['Semantic']['hit_rate_at_5']*100:.1f}%** | {ablation_res['Semantic']['mrr']} |
| **3. Basic Hybrid (Phase 2)** | {ablation_res['Basic Hybrid']['precision_at_5']} | {ablation_res['Basic Hybrid']['recall_at_5']} | **{ablation_res['Basic Hybrid']['hit_rate_at_5']*100:.1f}%** | {ablation_res['Basic Hybrid']['mrr']} |
| **4. Reciprocal Rank Fusion (RRF)** | {ablation_res['RRF']['precision_at_5']} | {ablation_res['RRF']['recall_at_5']} | **{ablation_res['RRF']['hit_rate_at_5']*100:.1f}%** | {ablation_res['RRF']['mrr']} |
| **5. RRF + Cross-Encoder Reranker** | {ablation_res['RRF + Reranker']['precision_at_5']} | {ablation_res['RRF + Reranker']['recall_at_5']} | **{ablation_res['RRF + Reranker']['hit_rate_at_5']*100:.1f}%** | {ablation_res['RRF + Reranker']['mrr']} |
| **6. Full Phase 3 (RRF + Reranker + Metadata)** | **{ablation_res['Full Phase 3']['precision_at_5']}** | **{ablation_res['Full Phase 3']['recall_at_5']}** | **{ablation_res['Full Phase 3']['hit_rate_at_5']*100:.1f}%** | **{ablation_res['Full Phase 3']['mrr']}** |

---

## 5. Rank Movement & Difficulty Analysis

### Rank Shift Analysis (Phase 2 vs. Phase 3)
* **Average Target Rank:** {rank_res['avg_rank_before_phase2']} (Phase 2) -> **{rank_res['avg_rank_after_phase3']}** (Phase 3)
* **Median Target Rank:** Position {rank_res['median_rank_before_phase2']} (Phase 2) -> **Position {rank_res['median_rank_after_phase3']}** (Phase 3)
* **Queries Improved in Rank:** **{rank_res['improved_count']} / {rank_res['total_queries']} ({rank_res['improved_pct']}%)**
* **Queries Unchanged in Rank:** **{rank_res['unchanged_count']} / {rank_res['total_queries']} ({rank_res['unchanged_pct']}%)**
* **Queries Degraded in Rank:** **{rank_res['degraded_count']} / {rank_res['total_queries']} ({rank_res['degraded_pct']}%)**

### Query Difficulty Level Performance

| Difficulty Level | Query Count | Avg Rank Before | Avg Rank After | Hit Rate@5 | MRR |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""

    for diff, dmetrics in rank_res['difficulty_summary'].items():
        doc_markdown += f"| **{diff}** | {dmetrics['query_count']} | {dmetrics['avg_rank_before']} | **{dmetrics['avg_rank_after']}** | **{dmetrics['hit_rate_at_5']*100:.1f}%** | **{dmetrics['mrr']}** |\n"

    doc_markdown += f"""
---

## 6. Execution Latency Breakdown
* **BM25 Retrieval:** {avg_latencies['bm25_ms']} ms
* **Semantic Vector Search:** {avg_latencies['semantic_ms']} ms
* **RRF Candidate Fusion:** {avg_latencies['rrf_ms']} ms
* **Cross-Encoder Reranking:** {avg_latencies['reranker_ms']} ms
* **Metadata Scoring:** {avg_latencies['metadata_ms']} ms
* **Total End-to-End Pipeline Latency:** **{avg_latencies['total_ms']} ms**

---

## 7. Compliance & Operational Boundary
> **Statutory Disclaimer:** Phase 3 only determines retrieval and relevance ranking. It does NOT establish legal compliance, determine mandatory certification, replace official BIS interpretations, or provide legally binding regulatory advice. QCO and regulatory reasoning will be handled in later phases.
"""

    with open(DOCS_MD, 'w', encoding='utf-8') as f:
        f.write(doc_markdown)

    print(f"[OK] Generated Phase 3 Documentation -> {DOCS_MD}")
    return master_eval_output


if __name__ == '__main__':
    run_master_phase3_evaluation()
