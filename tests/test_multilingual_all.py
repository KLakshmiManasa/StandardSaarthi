# -*- coding: utf-8 -*-
import sys
import io

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.multilingual import multilingual_service

queries = {
    "ta": "அடைக்கப்பட்ட குடிநீர் 20 லிட்டர் கேன்கள்",
    "te": "భవన అంతర్గత వైరింగ్ కోసం రాగి విద్యుత్ కేబుల్స్",
    "bn": "ভবন নির্মাণের জন্য পোর্টল্যান্ড সিমেন্ট",
    "gu": "પાણી માટે પ્લાસ્ટિક પાઇપ",
    "hi": "भवन निर्माण के लिए टीएमटी स्टील बार",
    "mr": "इमारतीच्या अंतर्गत वायरिंगसाठी तांब्याची केबल"
}

print("=== MULTILINGUAL DETECTION & TRANSLATION TEST ===")
for lang, q in queries.items():
    res = multilingual_service.process_query(q)
    det = res.get("detected_language")
    norm = res.get("normalized_english")
    print(f"[{lang}] Detected: {det} | Normalized English: {norm}")

print("\n=== LOCALIZATION TEST (ENGLISH -> INDIC) ===")
sample_res = {
    "status": "success",
    "message": "Verified Indian Standard successfully identified.",
    "entities": {
        "product": "Packaged Drinking Water",
        "category": "Food & Water",
        "application": "Direct human consumption"
    },
    "recommendations": [
        {
            "is_code": "IS 14543:2024",
            "title": "Packaged Drinking Water (other than Packaged Natural Mineral Water) — Specification",
            "scope": "Covers the requirements, hygiene conditions, physical and chemical parameters, testing procedures, and packaging standards for packaged drinking water.",
            "ranking_reasons": ["Exact match for packaged drinking water specification."]
        }
    ]
}

for lang in ["ta", "te", "bn", "gu", "hi", "mr"]:
    import copy
    copied = copy.deepcopy(sample_res)
    loc = multilingual_service.localize_results(copied, target_lang=lang)
    r = loc["recommendations"][0]
    print(f"[{lang}] Localized Title: {r.get('title_localized')}")
    print(f"[{lang}] Localized Scope: {r.get('scope_localized')}")
