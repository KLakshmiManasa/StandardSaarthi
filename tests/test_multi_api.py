# -*- coding: utf-8 -*-
import sys
import io
import requests

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

test_cases = [
    ("hi", "भवन निर्माण के लिए टीएमटी स्टील बार"),
    ("te", "భవన అంతర్గత వైరింగ్ కోసం రాగి విద్యుత్ కేబుల్స్"),
    ("bn", "ভবন নির্মাণের জন্য পোর্টল্যান্ড সিমেন্ট"),
    ("gu", "પાણી માટે પ્લાસ્ટિક પાઇપ")
]

print("=== MULTI-LANGUAGE LIVE API VERIFICATION ===")
for lang, query in test_cases:
    resp = requests.post("http://127.0.0.1:8000/api/analyze", json={
        "description": query,
        "language": "auto"
    })
    data = resp.json()
    det = data.get("multilingual_info", {}).get("detected_language")
    recs = data.get("recommendations", [])
    top = recs[0] if recs else {}
    print(f"\n[{lang.upper()}] Query: {query}")
    print(f"  Detected: {det} | Status: {data.get('status')}")
    print(f"  Entities Localized: {data.get('entities_localized')}")
    print(f"  Top Standard: {top.get('is_code')}")
    print(f"  Localized Title: {top.get('title_localized')}")
