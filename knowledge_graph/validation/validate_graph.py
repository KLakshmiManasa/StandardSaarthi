"""
SIH 26108 — Master Knowledge Graph Validation & Integrity Audit Script
"""

import os
import json
from datetime import datetime
from knowledge_graph.ingestion.build_graph import GraphStore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
REPORT_JSON = os.path.join(OUTPUTS_DIR, 'graph_validation_report.json')

os.makedirs(OUTPUTS_DIR, exist_ok=True)

def validate_knowledge_graph():
    print("[*] Running automated Knowledge Graph integrity audit...")
    graph = GraphStore(use_neo4j=False)
    graph.populate_graph()

    stats = graph.get_stats()

    # Integrity Checks
    duplicate_nodes = 0
    orphan_standards = 0
    broken_references = 0
    valid_edges = 0

    all_nodes = set()
    all_node_ids = set()
    for label, node_dict in graph.nodes.items():
        for nid in node_dict.keys():
            node_key = (label, nid)
            if node_key in all_nodes:
                duplicate_nodes += 1
            all_nodes.add(node_key)
            all_node_ids.add(nid)

    for std_code in graph.nodes["STANDARD"].keys():
        out_cnt = len(graph.out_edges.get(std_code, []))
        in_cnt = len(graph.in_edges.get(std_code, []))
        if out_cnt == 0 and in_cnt == 0:
            orphan_standards += 1

    for src_id, edges in graph.out_edges.items():
        for e in edges:
            tgt_id = e['target']
            if tgt_id not in all_node_ids:
                broken_references += 1
            else:
                valid_edges += 1

    status = "PASS" if broken_references == 0 and duplicate_nodes == 0 else "NEEDS_REVIEW"

    audit_report = {
        "audit_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "dataset_version": "v0.1-pilot",
        "graph_version": "kg-v0.1",
        "overall_status": status,
        "node_statistics": stats['node_counts'],
        "total_nodes": stats['total_nodes'],
        "relationship_statistics": stats['relationship_counts'],
        "total_relationships": stats['total_relationships'],
        "integrity_metrics": {
            "duplicate_nodes": duplicate_nodes,
            "orphan_standards": orphan_standards,
            "broken_references": broken_references,
            "valid_edges": valid_edges,
            "referential_integrity_pct": round((valid_edges / max(1, stats['total_relationships'])) * 100, 2)
        }
    }

    with open(REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump(audit_report, f, indent=2)

    print(f"[OK] Graph Audit Completed ({status}). Report generated -> {REPORT_JSON}")
    return audit_report

if __name__ == '__main__':
    validate_knowledge_graph()
