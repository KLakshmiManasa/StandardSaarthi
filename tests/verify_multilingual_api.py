# -*- coding: utf-8 -*-
import sys
import os
import io
import json
import requests

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Test 1: Mode A with Tamil Query
print("--- TEST 1: POST /api/analyze with Tamil Query ---")
resp = requests.post("http://127.0.0.1:8000/api/analyze", json={
    "description": "அடைக்கப்பட்ட குடிநீர் 20 லிட்டர் கேன்கள்",
    "language": "auto"
})
print("HTTP Status:", resp.status_code)
data = resp.json()
print("Pipeline Status:", data.get("status"))
print("Detected Language:", data.get("multilingual_info", {}).get("detected_language"))
print("Entities Original:", data.get("entities"))
print("Entities Localized:", data.get("entities_localized"))

if data.get("recommendations"):
    top_r = data["recommendations"][0]
    print("Top Standard:", top_r.get("is_code"))
    print("Localized Title:", top_r.get("title_localized"))
    print("Localized Scope:", top_r.get("scope_localized"))

# Test 2: Mode C with Tamil Tender Document Upload
print("\n--- TEST 2: POST /api/analyze/document with Tamil Document ---")
doc_path = os.path.join(os.path.dirname(__file__), "sample_tender_tamil.txt")
with open(doc_path, "rb") as f:
    files = {"file": ("sample_tender_tamil.txt", f, "text/plain")}
    resp_doc = requests.post("http://127.0.0.1:8000/api/analyze/document", files=files)

print("HTTP Status:", resp_doc.status_code)
doc_data = resp_doc.json()
print("Doc Status:", doc_data.get("status"))
print("Doc Language:", doc_data.get("detected_language"))
print("Doc Language Name:", doc_data.get("language_name"))
print("Extracted Count:", doc_data.get("requirement_count"))
for item in doc_data.get("extracted_requirements", []):
    print(f"  [{item['req_id']}] ({item['category_hint']}) Text: {item['text'][:40]}... -> EN: {item['normalized_english'][:40]}...")
