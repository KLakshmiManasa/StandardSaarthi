"""
SIH 26108 — Clean Standards Script
Normalizes IS codes, cleans text formatting, validates edition years and status values.
"""

import os
import json
import csv
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'standards', 'raw_standards.json')
PROCESSED_CSV = os.path.join(BASE_DIR, 'data', 'processed', 'standards_clean.csv')
PROCESSED_JSON = os.path.join(BASE_DIR, 'data', 'processed', 'standards_clean.json')

def normalize_is_code(code_str):
    if not code_str:
        return ""
    code = code_str.strip()
    code = re.sub(r'^(is|IS)[-\s]*', 'IS ', code, flags=re.IGNORECASE)
    code = re.sub(r'\s+', ' ', code)
    return code

def clean_standards():
    if not os.path.exists(RAW_FILE):
        print(f"[ERROR] Raw file {RAW_FILE} not found. Run build_pilot_dataset.py first.")
        return

    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    cleaned = []
    seen = set()
    allowed_statuses = {'ACTIVE', 'SUPERSEDED', 'WITHDRAWN', 'UNKNOWN'}
    allowed_sectors = {'Electrical', 'Civil', 'Mechanical', 'Electronics', 'General'}

    for record in raw_data:
        code = normalize_is_code(record.get('is_code', ''))
        if not code or code in seen:
            continue
        seen.add(code)

        rec = dict(record)
        rec['is_code'] = code
        rec['title'] = rec.get('title', '').strip()
        rec['scope_text'] = rec.get('scope_text', '').strip()
        
        # Validate edition year
        year = rec.get('edition_year')
        if year is not None:
            try:
                year = int(year)
                if year < 1900 or year > 2026:
                    year = None
            except ValueError:
                year = None
        rec['edition_year'] = year

        # Validate status
        status = rec.get('status', 'UNKNOWN').upper()
        if status not in allowed_statuses:
            status = 'UNKNOWN'
        rec['status'] = status

        # Validate sector
        sector = rec.get('sector', 'General').strip()
        if sector not in allowed_sectors:
            sector = 'General'
        rec['sector'] = sector

        cleaned.append(rec)

    # Write cleaned output
    with open(PROCESSED_JSON, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, indent=2)

    if cleaned:
        fieldnames = list(cleaned[0].keys())
        with open(PROCESSED_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned)

    print(f"[OK] Cleaning complete. Processed {len(cleaned)} standards -> {PROCESSED_CSV}")

if __name__ == '__main__':
    clean_standards()
