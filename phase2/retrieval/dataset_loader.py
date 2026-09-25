"""
SIH 26108 — Phase 2 Dataset Loader
Loads verified standards from Phase 1 CSV dataset and constructs normalized searchable search documents.
"""

import os
import csv
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STANDARDS_CSV = os.path.join(BASE_DIR, 'data', 'processed', 'standards_clean.csv')

def load_standards_dataset():
    """
    Loads verified standards from Phase 1 processed dataset.
    Returns a list of dictionaries containing standard metadata and constructed search document text.
    """
    if not os.path.exists(STANDARDS_CSV):
        raise FileNotFoundError(f"Phase 1 standards dataset not found at {STANDARDS_CSV}. Run Phase 1 first.")

    standards = []
    with open(STANDARDS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Filter only verified standards
            if row.get('verification_status') != 'VERIFIED':
                continue
            
            # Construct normalized searchable text document
            is_code = row.get('is_code', '').strip()
            title = row.get('title', '').strip()
            product_category = row.get('product_category', '').strip()
            scope_text = row.get('scope_text', '').strip()
            keywords = row.get('keywords', '').strip()
            materials = row.get('materials', '').strip()
            applications = row.get('applications', '').strip()
            technical_parameters = row.get('technical_parameters', '').strip()
            test_methods = row.get('test_methods', '').strip()
            normative_references = row.get('normative_references', '').strip()

            search_doc = f"""
IS CODE: {is_code}
TITLE: {title}
PRODUCT CATEGORY: {product_category}
SCOPE: {scope_text}
KEYWORDS: {keywords}
MATERIALS: {materials}
APPLICATIONS: {applications}
TECHNICAL PARAMETERS: {technical_parameters}
TEST METHODS: {test_methods}
NORMATIVE REFERENCES: {normative_references}
""".strip()

            standard_record = dict(row)
            standard_record['search_doc'] = search_doc
            standards.append(standard_record)

    return standards

if __name__ == '__main__':
    stds = load_standards_dataset()
    print(f"[OK] Loaded {len(stds)} verified standards into Phase 2 search document format.")
