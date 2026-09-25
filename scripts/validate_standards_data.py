"""
Script to audit and validate standards data quality across processed dataset files.
Generates reports/standards_data_quality_report.json.
"""

import os
import json
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'standards_clean.json')
REPORT_OUTPUT_PATH = os.path.join(BASE_DIR, 'reports', 'standards_data_quality_report.json')

def validate_data_quality():
    if not os.path.exists(CLEAN_DATA_PATH):
        print(f"File not found: {CLEAN_DATA_PATH}")
        return

    with open(CLEAN_DATA_PATH, 'r', encoding='utf-8') as f:
        standards = json.load(f)

    total_standards = len(standards)
    valid_records = 0
    duplicate_codes = set()
    seen_codes = set()
    invalid_urls = []
    missing_fields = []
    conflicting_lifecycles = []

    for idx, std in enumerate(standards):
        code = std.get("is_code", "").strip()
        if not code:
            missing_fields.append({"index": idx, "field": "is_code"})
            continue

        if code in seen_codes:
            duplicate_codes.add(code)
        seen_codes.add(code)

        title = std.get("title")
        pub_yr = std.get("publicationYear") or std.get("edition_year")
        if not title:
            missing_fields.append({"code": code, "field": "title"})
        if not pub_yr:
            missing_fields.append({"code": code, "field": "publicationYear"})

        # Source URL Validation
        src = std.get("source", {})
        portal_url = src.get("portalUrl")
        specific_url = src.get("specificUrl")

        if portal_url != "https://standards.bis.gov.in/":
            invalid_urls.append({"code": code, "url": portal_url, "reason": "portalUrl must be https://standards.bis.gov.in/"})

        if specific_url:
            if not specific_url.startswith("https://") or "services.bis.gov.in" in specific_url:
                invalid_urls.append({"code": code, "url": specific_url, "reason": "specificUrl uses obsolete/invalid domain"})

        # Lifecycle Status Validation
        sup_by = std.get("supersededBy") or std.get("superseded_by")
        life_status = std.get("lifecycleStatus")
        if sup_by and sup_by != "None" and life_status == "CURRENT / VERIFIED":
            conflicting_lifecycles.append({"code": code, "conflict": "Marked CURRENT but has supersededBy record"})

        valid_records += 1

    report = {
        "dataset_path": "data/processed/standards_clean.json",
        "total_standards_audited": total_standards,
        "valid_standards_count": valid_records,
        "duplicate_codes_count": len(duplicate_codes),
        "duplicate_codes": list(duplicate_codes),
        "invalid_urls_count": len(invalid_urls),
        "invalid_urls": invalid_urls,
        "missing_fields_count": len(missing_fields),
        "missing_fields_sample": missing_fields[:10],
        "conflicting_lifecycles_count": len(conflicting_lifecycles),
        "conflicting_lifecycles": conflicting_lifecycles,
        "data_quality_score_percent": round(((total_standards - len(invalid_urls) - len(missing_fields)) / max(1, total_standards)) * 100, 2)
    }

    os.makedirs(os.path.dirname(REPORT_OUTPUT_PATH), exist_ok=True)
    with open(REPORT_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Data quality audit completed! Score: {report['data_quality_score_percent']}%. Saved report to {REPORT_OUTPUT_PATH}")

if __name__ == "__main__":
    validate_data_quality()
