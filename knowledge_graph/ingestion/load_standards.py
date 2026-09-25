"""
SIH 26108 — Load Standards, Products, Materials, Applications & Test Methods Node Ingestion
"""

import os
import csv
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STANDARDS_CSV = os.path.join(BASE_DIR, 'data', 'processed', 'standards_clean.csv')

def normalize_text(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', str(text)).strip().lower()
    return re.sub(r'\s+', '_', clean)

def parse_items(text_str: str) -> list[str]:
    if not text_str or text_str == "N/A" or text_str == "UNKNOWN":
        return []
    items = re.split(r'[,;]', str(text_str))
    return [i.strip() for i in items if i.strip() and i.strip() != "N/A"]

def extract_standards_and_entities():
    if not os.path.exists(STANDARDS_CSV):
        raise FileNotFoundError(f"Standards CSV not found at {STANDARDS_CSV}")

    standards = []
    products = {}
    materials = {}
    applications = {}
    test_methods = {}
    amendments = {}
    edges = []

    with open(STANDARDS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('verification_status') != 'VERIFIED':
                continue

            is_code = row['is_code'].strip()
            standards.append(dict(row))

            # 1. Product Category entity
            prod_cat = row.get('product_category', '').strip()
            if prod_cat:
                p_norm = normalize_text(prod_cat)
                if p_norm not in products:
                    products[p_norm] = {"name": prod_cat, "category": row.get('sector', ''), "normalized_name": p_norm}
                edges.append({
                    "source": is_code,
                    "target": p_norm,
                    "type": "SPECIFIES_PRODUCT",
                    "target_type": "PRODUCT",
                    "verification_status": "VERIFIED"
                })

            # 2. Materials entities
            mats = parse_items(row.get('materials', ''))
            for m in mats:
                m_norm = normalize_text(m)
                if m_norm:
                    if m_norm not in materials:
                        materials[m_norm] = {"name": m, "normalized_name": m_norm}
                    edges.append({
                        "source": is_code,
                        "target": m_norm,
                        "type": "USES_MATERIAL",
                        "target_type": "MATERIAL",
                        "verification_status": "VERIFIED"
                    })

            # 3. Application entities
            apps = parse_items(row.get('applications', ''))
            for a in apps:
                a_norm = normalize_text(a)
                if a_norm:
                    if a_norm not in applications:
                        applications[a_norm] = {"name": a, "normalized_name": a_norm}
                    edges.append({
                        "source": is_code,
                        "target": a_norm,
                        "type": "APPLIES_TO",
                        "target_type": "APPLICATION",
                        "verification_status": "VERIFIED"
                    })

            # 4. Test Method entities
            tests = parse_items(row.get('test_methods', ''))
            for t in tests:
                t_norm = normalize_text(t)
                if t_norm:
                    if t_norm not in test_methods:
                        test_methods[t_norm] = {"name": t, "reference": t, "normalized_name": t_norm}
                    edges.append({
                        "source": is_code,
                        "target": t_norm,
                        "type": "TESTED_BY",
                        "target_type": "TEST_METHOD",
                        "verification_status": "VERIFIED"
                    })

            # 5. Amendment entities
            amd_json = row.get('amendments', '[]')
            try:
                amd_list = json.loads(amd_json) if isinstance(amd_json, str) else amd_json
                for amd in amd_list:
                    amd_num = amd.get('num')
                    amd_yr = amd.get('year')
                    amd_id = f"AMD_{is_code.replace(' ', '_')}_A{amd_num}"
                    if amd_id not in amendments:
                        amendments[amd_id] = {
                            "amendment_id": amd_id,
                            "number": amd_num,
                            "year": amd_yr,
                            "title": f"Amendment {amd_num} ({amd_yr}) for {is_code}",
                            "source_url": row.get('source_url', ''),
                            "verification_status": "VERIFIED"
                        }
                    edges.append({
                        "source": is_code,
                        "target": amd_id,
                        "type": "AMENDED_BY",
                        "target_type": "AMENDMENT",
                        "verification_status": "VERIFIED"
                    })
            except Exception:
                pass

    return {
        "standards": standards,
        "products": list(products.values()),
        "materials": list(materials.values()),
        "applications": list(applications.values()),
        "test_methods": list(test_methods.values()),
        "amendments": list(amendments.values()),
        "entity_edges": edges
    }


if __name__ == '__main__':
    data = extract_standards_and_entities()
    print(f"[OK] Extracted {len(data['standards'])} Standards, {len(data['products'])} Products, {len(data['materials'])} Materials, {len(data['applications'])} Applications, {len(data['test_methods'])} Test Methods, {len(data['amendments'])} Amendments.")
