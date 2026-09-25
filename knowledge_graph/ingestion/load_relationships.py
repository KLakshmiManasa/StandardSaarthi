"""
SIH 26108 — Load Standard-to-Standard Reference Edges
"""

import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RELATIONSHIPS_CSV = os.path.join(BASE_DIR, 'data', 'processed', 'relationships.csv')

def load_standard_relationships():
    if not os.path.exists(RELATIONSHIPS_CSV):
        raise FileNotFoundError(f"Relationships CSV not found at {RELATIONSHIPS_CSV}")

    rel_edges = []
    with open(RELATIONSHIPS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('verification_status') != 'VERIFIED':
                continue

            rel_type = row.get('relationship_type', 'NORMATIVE_REFERENCE').strip()
            # Standardize relationship type label mapping
            if rel_type == "NORMATIVE_REF":
                rel_type = "NORMATIVE_REFERENCE"

            rel_edges.append({
                "relationship_id": row.get('relationship_id', ''),
                "source": row['source_is_code'].strip(),
                "target": row['target_is_code'].strip(),
                "type": rel_type,
                "target_type": "STANDARD",
                "description": row.get('description', ''),
                "source_clause": row.get('source', ''),
                "verification_status": "VERIFIED"
            })

    return rel_edges

if __name__ == '__main__':
    edges = load_standard_relationships()
    print(f"[OK] Loaded {len(edges)} verified standard-to-standard relationship edges.")
