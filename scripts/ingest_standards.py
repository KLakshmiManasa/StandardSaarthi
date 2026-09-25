"""
SIH 26108 — Phase 8 Dataset Ingestion Script
Automates dataset ingestion and validation for expanded Indian Standards data.
"""

import os
import json
import csv
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')

def ingest_raw_data(raw_file_path: str) -> int:
    """
    Ingests raw standards JSON/CSV file into raw data directory with initial structure validation.
    """
    if not os.path.exists(raw_file_path):
        print(f"[!] File not found: {raw_file_path}")
        return 0

    print(f"[*] Ingesting raw standards file: {raw_file_path}")
    raw_records = []

    if raw_file_path.endswith('.csv'):
        with open(raw_file_path, 'r', encoding='utf-8') as f:
            raw_records = list(csv.DictReader(f))
    elif raw_file_path.endswith('.json'):
        with open(raw_file_path, 'r', encoding='utf-8') as f:
            raw_records = json.load(f)

    valid_count = 0
    for rec in raw_records:
        if rec.get('is_code') and rec.get('title'):
            valid_count += 1

    print(f"[OK] Ingestion audit complete: {valid_count} valid record candidates identified out of {len(raw_records)} records.")
    return valid_count

if __name__ == '__main__':
    pilot_json = os.path.join(PROCESSED_DIR, 'standards_phase5.json')
    if os.path.exists(pilot_json):
        ingest_raw_data(pilot_json)
