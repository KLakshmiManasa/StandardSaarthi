"""
SIH 26108 — Synthetic Query Generator Script
Generates perturbation variations (abbreviations, tender prefixing, clause reordering) from verified ground-truth queries.
"""

import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUND_TRUTH_CSV = os.path.join(BASE_DIR, 'data', 'evaluation', 'ground_truth.csv')
SYNTHETIC_CSV = os.path.join(BASE_DIR, 'data', 'evaluation', 'synthetic_queries.csv')

def generate_synthetic():
    if not os.path.exists(GROUND_TRUTH_CSV):
        print(f"[ERROR] Ground truth file {GROUND_TRUTH_CSV} not found.")
        return

    queries = []
    with open(GROUND_TRUTH_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        queries = list(reader)

    synthetic = []
    syn_id = 1

    for q in queries:
        desc = q['procurement_description']
        target = q['target_is_code']
        sector = q['sector']

        # Variation 1: Abbreviated / Compressed wording
        var1 = desc.replace("Supply of", "Requirement for").replace("single core", "1-core").replace("High Strength Deformed", "TMT")
        synthetic.append({
            "query_id": f"SYN_{syn_id:04d}",
            "procurement_description": var1,
            "sector": sector,
            "target_is_code": target,
            "variation_type": "COMPRESSED_ABBREVIATED",
            "source_type": "SYNTHETIC",
            "verification_status": "VERIFIED"
        })
        syn_id += 1

        # Variation 2: Tender Jargon Prefixing
        var2 = f"Tender RFP Spec: {desc} Compliance with CPWD standards required."
        synthetic.append({
            "query_id": f"SYN_{syn_id:04d}",
            "procurement_description": var2,
            "sector": sector,
            "target_is_code": target,
            "variation_type": "TENDER_JARGON_PREFIX",
            "source_type": "SYNTHETIC",
            "verification_status": "VERIFIED"
        })
        syn_id += 1

        # Variation 3: Parametric Clause Reordering
        var3 = f"Specifications: {q.get('technical_requirements', '')} for {q.get('application', '')} ({q.get('material', '')})."
        synthetic.append({
            "query_id": f"SYN_{syn_id:04d}",
            "procurement_description": var3,
            "sector": sector,
            "target_is_code": target,
            "variation_type": "PARAMETRIC_CLAUSE_REORDER",
            "source_type": "SYNTHETIC",
            "verification_status": "VERIFIED"
        })
        syn_id += 1

    if synthetic:
        fieldnames = list(synthetic[0].keys())
        with open(SYNTHETIC_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(synthetic)

    print(f"[OK] Generated {len(synthetic)} synthetic query variations -> {SYNTHETIC_CSV}")

if __name__ == '__main__':
    generate_synthetic()
