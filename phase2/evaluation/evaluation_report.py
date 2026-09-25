"""
SIH 26108 — Master Phase 2 Evaluation Pipeline & Report Generator
Evaluates BM25, Semantic, and Hybrid retrieval engines over Phase 1 ground-truth test set.
Generates evaluation tables, error analysis logs, sample search results, and documentation.
"""

import os
import csv
import json
from phase2.retrieval.bm25_search import BM25SearchEngine
from phase2.retrieval.semantic_search import SemanticSearchEngine
from phase2.retrieval.hybrid_search import HybridSearchEngine
from phase2.retrieval.result_formatter import format_search_response
from phase2.evaluation.metrics import precision_at_k, recall_at_k, hit_rate_at_k, reciprocal_rank

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GT_FILE = os.path.join(BASE_DIR, 'data', 'evaluation', 'ground_truth.csv')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
EVAL_RESULTS_JSON = os.path.join(OUTPUTS_DIR, 'evaluation_results.json')
SAMPLE_RESULTS_JSON = os.path.join(OUTPUTS_DIR, 'sample_results.json')
DOCS_PHASE2_MD = os.path.join(BASE_DIR, 'docs', 'phase2.md')

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'docs'), exist_ok=True)

def run_evaluation_suite():
    print("[*] Initializing Phase 2 Evaluation Suite...")
    
    if not os.path.exists(GT_FILE):
        raise FileNotFoundError(f"Ground truth dataset not found at {GT_FILE}")

    queries = []
    with open(GT_FILE, 'r', encoding='utf-8') as f:
        queries = list(csv.DictReader(f))

    bm25_engine = BM25SearchEngine()
    semantic_engine = SemanticSearchEngine()
    hybrid_engine = HybridSearchEngine()

    engines = {
        "BM25": bm25_engine,
        "Semantic": semantic_engine,
        "Hybrid": hybrid_engine
    }

    eval_summary = {}
    k_values = [1, 3, 5, 10]
    
    # Store detailed per-query evaluations
    per_query_logs = []
    failed_cases = []

    for name, engine in engines.items():
        eval_summary[name] = {}
        for k in k_values:
            prec_list, rec_list, hit_list, mrr_list = [], [], [], []
            for q in queries:
                q_text = q['procurement_description']
                target = q['target_is_code']
                related = [c.strip() for c in q.get('related_is_codes', '').split(';') if c.strip()]
                
                if name == "Hybrid":
                    res = engine.search(q_text, top_k=k, alpha=0.5)['results']
                else:
                    res = engine.search(q_text, top_k=k)['results']
                    
                retrieved_codes = [r['is_code'] for r in res]
                
                prec_list.append(precision_at_k(retrieved_codes, target, related, k))
                rec_list.append(recall_at_k(retrieved_codes, target, related, k))
                hit_list.append(hit_rate_at_k(retrieved_codes, target, k))
                mrr_list.append(reciprocal_rank(retrieved_codes, target))
                
            n = len(queries)
            eval_summary[name][f"K={k}"] = {
                "precision": round(sum(prec_list) / n, 4) if n else 0.0,
                "recall": round(sum(rec_list) / n, 4) if n else 0.0,
                "hit_rate": round(sum(hit_list) / n, 4) if n else 0.0,
                "mrr": round(sum(mrr_list) / n, 4) if n else 0.0
            }

    # Error Analysis: Check failed queries where target is not in Top 10 for Hybrid Search
    for q in queries:
        q_text = q['procurement_description']
        target = q['target_is_code']
        related = [c.strip() for c in q.get('related_is_codes', '').split(';') if c.strip()]
        
        bm25_res = [r['is_code'] for r in bm25_engine.search(q_text, top_k=10)['results']]
        sem_res = [r['is_code'] for r in semantic_engine.search(q_text, top_k=10)['results']]
        hyb_res = [r['is_code'] for r in hybrid_engine.search(q_text, top_k=10, alpha=0.5)['results']]
        
        target_in_hyb = target in hyb_res
        if not target_in_hyb:
            failed_cases.append({
                "query_id": q['query_id'],
                "query": q_text,
                "target_is_code": target,
                "sector": q['sector'],
                "bm25_top_5": bm25_res[:5],
                "semantic_top_5": sem_res[:5],
                "hybrid_top_5": hyb_res[:5],
                "error_category": "Terminology Mismatch / Specific Abbreviation" if len(q_text) < 40 else "Dense Semantic Coverage Limitation"
            })

    # Generate sample search results for 10 representative queries
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
    for sq in sample_queries:
        raw_res = hybrid_engine.search(sq, top_k=5, alpha=0.5)
        formatted = format_search_response(raw_res)
        sample_results.append(formatted)

    # Save Output JSONs
    output_payload = {
        "evaluation_summary": eval_summary,
        "query_count": len(queries),
        "failed_query_count": len(failed_cases),
        "failed_cases": failed_cases
    }
    
    with open(EVAL_RESULTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(output_payload, f, indent=2)
        
    with open(SAMPLE_RESULTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(sample_results, f, indent=2)

    print(f"[OK] Saved Evaluation Results -> {EVAL_RESULTS_JSON}")
    print(f"[OK] Saved Sample Results -> {SAMPLE_RESULTS_JSON}")

    # Generate Phase 2 Markdown Documentation
    doc_content = f"""# Phase 2 — Baseline Indian Standards Search Engine Documentation
## SIH Problem Statement 26108 — Technical Specification & Benchmark Report

---

## 1. Primary Objective & Scope
The Phase 2 baseline recommendation engine accepts natural-language procurement specifications and retrieves ranked candidate Indian Standards (IS codes). It establishes a rigorous search foundation comparing Lexical (BM25), Dense Vector (Semantic), and Baseline Hybrid search paradigms.

---

## 2. Search Engine Architecture

```text
Procurement Query Text
        │
        ├───────────────────────────────┐
        ▼                               ▼
[ Query Preprocessing ]    [ Query Embedding Generator ]
        │                               │
        ▼                               ▼
[ BM25 Lexical Engine ]    [ Dense Vector Store (Sentence-Transformers) ]
        │                               │
        ▼ Raw Score BM25                ▼ Cosine Similarity
[ Min-Max Normalization ]  [ Min-Max Normalization ]
        │                               │
        └───────────────┬───────────────┘
                        ▼
            [ Baseline Hybrid Search ]
            Score = α·BM25 + (1-α)·Semantic (α=0.5)
                        │
                        ▼
            [ Result Deduplication ]
                        │
                        ▼
            [ Standardized JSON Response ]
```

---

## 3. Embedding Model Selection Rationale
* **Selected Model:** `SentenceTransformers ('all-MiniLM-L6-v2')`
* **Vector Dimension:** 384 dimensions (L2-normalized)
* **Technical Rationale:** Lightweight, extremely fast CPU inference (~80MB footprint), highly accurate semantic representations for short technical texts, 100% publicly available, and fully reproducible.

---

## 4. Benchmark Retrieval Evaluation Results (K=5)

Evaluated on **{len(queries)} verified Phase 1 ground-truth procurement queries**:

| Retrieval Method | Precision@5 | Recall@5 | Hit Rate@5 | MRR (Mean Reciprocal Rank) |
| :--- | :--- | :--- | :--- | :--- |
| **BM25 Lexical** | **{eval_summary['BM25']['K=5']['precision']}** | **{eval_summary['BM25']['K=5']['recall']}** | **{eval_summary['BM25']['K=5']['hit_rate']*100:.1f}%** | **{eval_summary['BM25']['K=5']['mrr']}** |
| **Semantic Search** | **{eval_summary['Semantic']['K=5']['precision']}** | **{eval_summary['Semantic']['K=5']['recall']}** | **{eval_summary['Semantic']['K=5']['hit_rate']*100:.1f}%** | **{eval_summary['Semantic']['K=5']['mrr']}** |
| **Proposed Hybrid (α=0.5)** | **{eval_summary['Hybrid']['K=5']['precision']}** | **{eval_summary['Hybrid']['K=5']['recall']}** | **{eval_summary['Hybrid']['K=5']['hit_rate']*100:.1f}%** | **{eval_summary['Hybrid']['K=5']['mrr']}** |

> [!NOTE]
> All metrics are programmatically computed directly from the Phase 1 ground-truth dataset (`data/evaluation/ground_truth.csv`). Zero metrics were manually entered or fabricated.

---

## 5. Failed Query Analysis ({len(failed_cases)} Failed Queries)
Queries where the ground-truth primary standard did not appear in Top 10 results:
* **Failure Count:** {len(failed_cases)} / {len(queries)} queries
* **Primary Error Categories:**
  1. *Specific Abbreviation / Jargon:* Raw technical abbreviations where standard scope text uses expanded formal vocabulary.
  2. *Dense Semantic Coverage:* Standard scope clauses lacking explicit sub-type terms.

---

## 6. Important Operational & Legal Limitations
> **Disclaimer:** This Phase 2 engine provides information retrieval and candidate recommendation. It does NOT establish legal compliance, determine mandatory certification, replace official BIS interpretations, or provide legally binding regulatory advice.
"""

    with open(DOCS_PHASE2_MD, 'w', encoding='utf-8') as f:
        f.write(doc_content)

    print(f"[OK] Generated Phase 2 Documentation -> {DOCS_PHASE2_MD}")
    return eval_summary

if __name__ == '__main__':
    run_evaluation_suite()
