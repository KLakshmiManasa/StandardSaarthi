"""
SIH 26108 — Phase 8 Dataset Normalization Script
Normalizes IS Code formatting, casing, whitespace, and structural fields.
"""

import os
import re
import json
from typing import Dict, Any

def normalize_is_code(code: str) -> str:
    """Normalizes IS code string to canonical format e.g. IS 694."""
    if not code:
        return ""
    code = code.strip().upper()
    code = re.sub(r'^IS[-_\s]*', 'IS ', code)
    code = re.sub(r'\s+', ' ', code)
    return code

def normalize_standard_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Applies canonical field normalization to standard entry."""
    entry['is_code'] = normalize_is_code(entry.get('is_code', ''))
    entry['title'] = (entry.get('title') or '').strip()
    entry['sector'] = (entry.get('sector') or 'General').strip().title()
    entry['product_category'] = (entry.get('product_category') or 'General').strip()
    
    # Ensure list types
    for key in ['materials', 'applications', 'industries', 'keywords', 'related_standards']:
        if isinstance(entry.get(key), str):
            entry[key] = [x.strip() for x in entry[key].split(',') if x.strip()]
        elif not isinstance(entry.get(key), list):
            entry[key] = []
            
    return entry

if __name__ == '__main__':
    test_code = normalize_is_code("is-694")
    print(f"Normalized sample: 'is-694' -> '{test_code}'")
