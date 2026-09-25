"""
SIH 26108 — Phase 8 Dataset Deduplication Script
Deduplicates standard entries based on IS code and titles.
"""

import os
import json
from typing import List, Dict, Any
from scripts.normalize_standards import normalize_standard_entry

def deduplicate_standards(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicates records retaining the most complete entry per IS code."""
    seen = {}
    for rec in records:
        norm = normalize_standard_entry(rec)
        code = norm['is_code']
        if not code:
            continue
        if code not in seen:
            seen[code] = norm
        else:
            # Keep entry with longer description / scope text
            existing_len = len(seen[code].get('description', '') or seen[code].get('scope_text', ''))
            new_len = len(norm.get('description', '') or norm.get('scope_text', ''))
            if new_len > existing_len:
                seen[code] = norm
                
    return list(seen.values())

if __name__ == '__main__':
    sample = [
        {"is_code": "IS 694", "title": "PVC Cables", "description": "Short"},
        {"is_code": "is 694", "title": "Polyvinyl Chloride Insulated Cables", "description": "Longer complete description"}
    ]
    dedup = deduplicate_standards(sample)
    print(f"Deduplicated count: {len(dedup)} (expected 1)")
