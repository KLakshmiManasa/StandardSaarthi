# -*- coding: utf-8 -*-
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.tender_parser import tender_parser

file_path = os.path.join(os.path.dirname(__file__), "sample_tender_tamil.txt")
with open(file_path, "rb") as f:
    file_bytes = f.read()

res = tender_parser.parse_tender_document(file_bytes, "sample_tender_tamil.txt")
print("=== PARSED TENDER DOCUMENT ===")
print("Status:", res.get("status"))
print("Detected Language:", res.get("detected_language"))
print("Language Name:", res.get("language_name"))
print("Requirement Count:", res.get("requirement_count"))

for r in res.get("extracted_requirements", []):
    print(f"\n[{r['req_id']}] Language: {r.get('language')}")
    print("  Text:", r['text'])
    print("  Normalized English:", r.get('normalized_english'))
    print("  Category Hint:", r.get('category_hint'))
