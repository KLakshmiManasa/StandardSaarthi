"""
SIH 26108 — Load QCO Nodes, Authority Nodes, and Compliance Edges
"""

import os
import csv
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QCO_CSV = os.path.join(BASE_DIR, 'data', 'processed', 'qco_compliance.csv')

def normalize_text(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', str(text)).strip().lower()
    return re.sub(r'\s+', '_', clean)

def load_qco_and_authorities():
    if not os.path.exists(QCO_CSV):
        raise FileNotFoundError(f"QCO CSV not found at {QCO_CSV}")

    qco_nodes = []
    authorities = {}
    edges = []

    with open(QCO_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('verification_status') != 'VERIFIED':
                continue

            qco_id = row['qco_id'].strip()
            is_code = row['is_code'].strip()
            ministry = row.get('issuing_ministry', '').strip()

            qco_nodes.append({
                "qco_id": qco_id,
                "qco_title": row.get('qco_title', ''),
                "notification_number": row.get('notification_number', ''),
                "issuing_ministry": ministry,
                "notification_date": row.get('notification_date', ''),
                "mandatory_status": row.get('mandatory_status', 'MANDATORY'),
                "effective_date": row.get('effective_date', ''),
                "source_url": row.get('source_url', ''),
                "verification_status": "VERIFIED"
            })

            # Edge: STANDARD -> QCO
            edges.append({
                "source": is_code,
                "target": qco_id,
                "type": "ASSOCIATED_WITH_QCO",
                "target_type": "QCO",
                "verification_status": "VERIFIED"
            })

            # Authority Node & Edge: QCO -> AUTHORITY
            if ministry:
                auth_norm = normalize_text(ministry)
                if auth_norm not in authorities:
                    authorities[auth_norm] = {"name": ministry, "normalized_name": auth_norm}
                edges.append({
                    "source": qco_id,
                    "target": auth_norm,
                    "type": "ISSUED_BY",
                    "target_type": "AUTHORITY",
                    "verification_status": "VERIFIED"
                })

    return {
        "qcos": qco_nodes,
        "authorities": list(authorities.values()),
        "qco_edges": edges
    }

if __name__ == '__main__':
    res = load_qco_and_authorities()
    print(f"[OK] Loaded {len(res['qcos'])} QCO nodes, {len(res['authorities'])} Authority nodes, {len(res['qco_edges'])} QCO edges.")
