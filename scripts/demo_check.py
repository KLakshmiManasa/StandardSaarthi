"""
SIH 26108 — Automated Pre-Demo Health Check Script
Verifies system readiness across Backend API, Vector Store, Knowledge Graph, QCO Engine,
Demo Scenarios, Facts File, and Dataset Files.
"""

import os
import sys
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def run_demo_check():
    print("==========================================================================")
    print("           SIH 26108 AUTOMATED PRE-DEMO SYSTEM HEALTH CHECK               ")
    print("==========================================================================")

    checks = []

    # 1. Check Facts File
    facts_path = os.path.join(BASE_DIR, 'docs', 'project_facts.json')
    if os.path.exists(facts_path):
        with open(facts_path, 'r', encoding='utf-8') as f:
            facts = json.load(f)
        checks.append(("Single Source of Truth Facts", True, f"{facts.get('standards_count')} standards, {facts.get('evaluation_queries')} queries"))
    else:
        checks.append(("Single Source of Truth Facts", False, "Missing docs/project_facts.json"))

    # 2. Check Demo Scenarios JSON
    demo_scen_path = os.path.join(BASE_DIR, 'data', 'demo', 'demo_scenarios.json')
    if os.path.exists(demo_scen_path):
        with open(demo_scen_path, 'r', encoding='utf-8') as f:
            scens = json.load(f)
        checks.append(("Demo Scenarios Config", True, f"{len(scens)} demo scenarios loaded"))
    else:
        checks.append(("Demo Scenarios Config", False, "Missing data/demo/demo_scenarios.json"))

    # 3. Check Core Pipeline Initialization
    try:
        from integration.pipeline import pipeline
        checks.append(("Integration Pipeline Core", True, "Pipeline orchestrator loaded"))
        checks.append(("Vector Store Service", pipeline.vector_available, "SentenceTransformers Vector Store"))
        checks.append(("Knowledge Graph Service", pipeline.graph_available, "Neo4j / In-Memory Graph Store"))
    except Exception as e:
        checks.append(("Integration Pipeline Core", False, f"Error: {e}"))

    # 4. Check Health Check Function
    try:
        from api.health import check_health
        h_res = check_health()
        checks.append(("API Health Endpoint", True, f"Status: {h_res.get('status')}"))
    except Exception as e:
        checks.append(("API Health Endpoint", False, f"Error: {e}"))

    # 5. Check Test Live Recommendation (Electrical Cable Scenario 1)
    try:
        sample_q = "Procurement of 1.5 sq mm single core PVC insulated flame retardant copper electrical cables suitable for internal building wiring."
        rec_res = pipeline.recommend(sample_q, top_k=5)
        status_ok = rec_res.get("status") == "success" and len(rec_res.get("recommendations", [])) > 0
        top_code = rec_res.get("recommendations", [{}])[0].get("is_code", "None")
        checks.append(("Live Recommendation Engine", status_ok, f"Top Code: {top_code} (Status: {rec_res.get('status')})"))
    except Exception as e:
        checks.append(("Live Recommendation Engine", False, f"Error: {e}"))

    # 6. Check Ambiguous Query Guardrail (Scenario 2)
    try:
        ambig_q = "Requirement for electrical cable for office project."
        ambig_res = pipeline.recommend(ambig_q)
        ambig_ok = ambig_res.get("status") == "needs_clarification"
        checks.append(("Ambiguity Guardrail Check", ambig_ok, f"Status: {ambig_res.get('status')}"))
    except Exception as e:
        checks.append(("Ambiguity Guardrail Check", False, f"Error: {e}"))

    # 7. Check Out of Domain Guardrail (Scenario 5)
    try:
        ood_q = "What is the best smartphone for gaming and how to write a Python function?"
        ood_res = pipeline.recommend(ood_q)
        ood_ok = ood_res.get("status") == "out_of_domain"
        checks.append(("Out-of-Domain Guardrail Check", ood_ok, f"Status: {ood_res.get('status')}"))
    except Exception as e:
        checks.append(("Out-of-Domain Guardrail Check", False, f"Error: {e}"))

    # Print Readiness Report
    all_passed = True
    print("\nCheck Results:")
    print("-" * 74)
    for name, passed, detail in checks:
        status_str = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_passed = False
        print(f"  {status_str:<7} | {name:<32} | {detail}")

    print("-" * 74)
    if all_passed:
        print("OVERALL DEMO READINESS: READY FOR LIVE SIH DEMONSTRATION [READY]\n")
    else:
        print("OVERALL DEMO READINESS: READY WITH LIMITATIONS / WARNINGS [LIMITATIONS]\n")
    print("==========================================================================")

if __name__ == '__main__':
    run_demo_check()
