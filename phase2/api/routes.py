"""
SIH 26108 — Extended Multi-Method Search API Routes
Exposes RESTful endpoints supporting BM25, Semantic, Hybrid, RRF, and Phase 3 Advanced Ranking.
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from phase2.retrieval.bm25_search import BM25SearchEngine
from phase2.retrieval.semantic_search import SemanticSearchEngine
from phase2.retrieval.hybrid_search import HybridSearchEngine
from phase3.ranking.rrf import RRFEngine
from phase3.ranking.final_ranker import Phase3FinalRanker
from phase2.retrieval.result_formatter import format_search_response, LEGAL_DISCLAIMER
from knowledge_graph.ingestion.build_graph import GraphStore
from knowledge_graph.queries.standard_queries import StandardQueries
from knowledge_graph.queries.relationship_queries import RelationshipQueries
from knowledge_graph.expansion.graph_expansion import CandidateGraphExpander
from phase5.recommendation_engine import Phase5RecommendationEngine

app = FastAPI(
    title="SIH 26108 — Indian Standards Recommendation Engine API",
    description="Multi-Method Search & Graph-RAG Recommendation API supporting BM25, Semantic, Hybrid, Phase 4 Traversals, and Phase 5 Explainable Recommendations.",
    version="0.5.0"
)

# Initialize engines
bm25_engine = BM25SearchEngine()
semantic_engine = SemanticSearchEngine()
hybrid_engine = HybridSearchEngine()
rrf_engine = RRFEngine()
phase3_engine = Phase3FinalRanker()

# Initialize graph components & recommendation engine
graph_store = GraphStore(use_neo4j=False)
graph_store.populate_graph()
standard_queries = StandardQueries(graph_store)
relationship_queries = RelationshipQueries(graph_store)
graph_expander = CandidateGraphExpander(graph_store)
recommendation_engine = Phase5RecommendationEngine()

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Natural language procurement specification text")
    method: str = Field("phase3", description="Retrieval method: 'bm25', 'semantic', 'hybrid', 'rrf', or 'phase3'")
    top_k: int = Field(10, ge=1, le=50, description="Number of top candidate standards to retrieve")
    alpha: float = Field(0.5, ge=0.0, le=1.0, description="Hybrid alpha parameter (for baseline hybrid)")
    sector: Optional[str] = Field(None, description="Optional sector filter ('Electrical' or 'Civil')")

class RecommendRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=2000, description="Natural language procurement specification text")
    top_k: int = Field(10, ge=1, le=50, description="Number of top recommendations to return")
    mode: str = Field("graph_rag", description="Retrieval pipeline mode: 'graph_rag', 'vector', or 'keyword'")

class GraphExpandRequest(BaseModel):
    is_codes: List[str] = Field(..., min_length=1, description="List of candidate IS codes to expand")
    depth: int = Field(1, ge=1, le=2, description="Traversal depth limit (1 or 2)")

@app.get("/api/health")
def health_check():
    """Health check and service status endpoint."""
    return {
        "status": "HEALTHY",
        "service": "SIH 26108 Indian Standards Advanced Search API",
        "phase": "Phase 4 Graph-Ready",
        "dataset_standards_count": len(phase3_engine.bm25_engine.standards),
        "graph_nodes_count": graph_store.get_stats()["total_nodes"],
        "graph_edges_count": graph_store.get_stats().get("total_relationships", graph_store.get_stats().get("total_edges", 0))
    }

@app.post("/api/search")
def search_standards(req: SearchRequest):
    """
    Executes search over Indian Standards dataset using specified method.
    """
    query_text = req.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text cannot be empty or whitespace.")

    method = req.method.lower().strip()
    
    if method == 'bm25':
        raw_res = bm25_engine.search(query_text, top_k=req.top_k, sector_filter=req.sector)
    elif method == 'semantic':
        raw_res = semantic_engine.search(query_text, top_k=req.top_k, sector_filter=req.sector)
    elif method == 'hybrid':
        raw_res = hybrid_engine.search(query_text, top_k=req.top_k, alpha=req.alpha, sector_filter=req.sector)
    elif method == 'rrf':
        raw_res = rrf_engine.search(query_text, top_k=req.top_k, sector_filter=req.sector)
    elif method == 'phase3':
        raw_res = phase3_engine.search(query_text, top_k=req.top_k, sector_filter=req.sector)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid search method '{req.method}'. Allowed values: 'bm25', 'semantic', 'hybrid', 'rrf', 'phase3'."
        )

    formatted = format_search_response(raw_res)
    return formatted

@app.get("/api/standards/{is_code}/graph")
def get_standard_graph(is_code: str):
    """
    Returns standard node details, outgoing relationship edges, and a structured graph representation (nodes, edges).
    """
    code = is_code.strip().upper()
    if not code.startswith("IS "):
        # Normalize IS code if user passes '694' -> 'IS 694'
        if code.isdigit() or ' ' not in code:
            code = f"IS {code}"
    
    std_node = standard_queries.get_standard_by_code(code)
    if not std_node:
        raise HTTPException(status_code=404, detail=f"Standard '{is_code}' not found in Knowledge Graph.")

    outgoing = relationship_queries.get_outgoing_relationships(code)
    amendments = relationship_queries.get_amendments(code)
    qcos = relationship_queries.get_qco_info(code)

    # Build visualization structure (nodes and edges)
    vis_nodes = [{"id": code, "label": "STANDARD", "name": std_node["title"], "sector": std_node.get("sector", "")}]
    vis_edges = []

    seen_nodes = {code}

    for rel in outgoing:
        tgt = rel["target"]
        rel_type = rel["relationship_type"]
        if tgt not in seen_nodes:
            seen_nodes.add(tgt)
            # Find target node label/details if available
            tgt_label = "ENTITY"
            tgt_name = tgt
            if tgt in graph_store.nodes["STANDARD"]:
                tgt_label = "STANDARD"
                tgt_name = graph_store.nodes["STANDARD"][tgt]["title"]
            elif tgt in graph_store.nodes["QCO"]:
                tgt_label = "QCO"
                tgt_name = graph_store.nodes["QCO"][tgt]["title"]
            elif tgt in graph_store.nodes["AMENDMENT"]:
                tgt_label = "AMENDMENT"
                tgt_name = f"Amendment {tgt}"

            vis_nodes.append({"id": tgt, "label": tgt_label, "name": tgt_name})
        
        vis_edges.append({"source": code, "target": tgt, "type": rel_type, "properties": rel.get("properties", {})})

    return {
        "is_code": code,
        "standard": std_node,
        "outgoing_relationships_count": len(outgoing),
        "amendments": amendments,
        "qco_compliance": qcos,
        "outgoing_relationships": outgoing,
        "visualization": {
            "nodes": vis_nodes,
            "edges": vis_edges
        }
    }

@app.post("/api/graph/expand")
def expand_graph_candidates(req: GraphExpandRequest):
    """
    Expands candidate standards list with graph-derived reference standards and dependencies.
    """
    if not req.is_codes:
        raise HTTPException(status_code=400, detail="is_codes list cannot be empty.")

    expansion_bundle = graph_expander.expand_candidates(req.is_codes, max_depth=req.depth)
    return expansion_bundle

from fastapi.responses import FileResponse, JSONResponse
from phase6.guardrails.query_guardrails import QueryGuardrails
from phase6.security.security_sanitizer import SecuritySanitizer

query_guardrails = QueryGuardrails()
security_sanitizer = SecuritySanitizer()

@app.post("/api/recommend")
def recommend_standards(req: RecommendRequest):
    """
    Executes Phase 5/6 Recommendation Engine with Query Guardrails & Security Protection.
    """
    raw_desc = req.description
    
    # 1. Security Sanitization
    is_safe, sanitized_or_msg, threat = security_sanitizer.sanitize_input(raw_desc)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"Security Alert [{threat}]: {sanitized_or_msg}")

    # 2. Query Guardrails (Ambiguity & Out-of-Domain Detection)
    status_code, guard_details = query_guardrails.evaluate_query(sanitized_or_msg)
    if status_code == 'OUT_OF_DOMAIN':
        return JSONResponse(status_code=422, content=guard_details)
    elif status_code == 'AMBIGUOUS':
        return JSONResponse(status_code=400, content=guard_details)

    # 3. Process Recommendation
    res = recommendation_engine.recommend(sanitized_or_msg, top_k=req.top_k, mode=req.mode)
    return res

@app.get("/api/evaluation/report")
def get_evaluation_report():
    """
    Returns latest comparative evaluation benchmark report JSON.
    """
    report_path = os.path.join(BASE_DIR, 'outputs', 'phase6_evaluation_report.json')
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Evaluation report not found. Run 'python evaluate.py' first.")
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.get("/eval")
def get_evaluation_dashboard():
    """
    Serves internal Evaluation Dashboard UI.
    """
    dash_path = os.path.join(BASE_DIR, 'frontend', 'eval_dashboard.html')
    if os.path.exists(dash_path):
        return FileResponse(dash_path)
    raise HTTPException(status_code=404, detail="Evaluation dashboard UI not found.")

# Mount Frontend static files at root AFTER API routes
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")




