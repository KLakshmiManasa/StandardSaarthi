"""
Indian Standards Recommendation Engine — API & Entry Point
Provides centralized RESTful endpoints for Recommendations, Document Upload, Technical Specs,
Standards Catalog, Regulatory/QCO, History, PDF Reports, and System Diagnostics.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Response
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel

from integration.pipeline import pipeline
from integration.schemas import RecommendRequest
from integration.errors import global_exception_handler
from api.health import router as health_router, check_health

from services.tender_parser import tender_parser
from services.multilingual import multilingual_service
from services.standards_service import standards_service
from services.history_store import history_store
from services.report_generator import report_generator

logger = logging.getLogger("ProductAPI")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = FastAPI(
    title="StandardSaarthi API",
    description="AI-powered standards intelligence for procurement and tender specifications.",
    version="1.0.0"
)

# Register Global Exception Handler
app.add_exception_handler(Exception, global_exception_handler)

# Register Health Router
app.include_router(health_router)

@app.get("/health")
def get_health():
    return check_health()

# ==========================================================
# LEGACY RECOMMENDATION ENDPOINT FOR COMPATIBILITY
# ==========================================================
@app.post("/api/recommend")
def recommend_standards(req: RecommendRequest):
    raw_query = req.description or ""
    if (req.language and req.language != "auto") or not raw_query.isascii():
        lang_res = multilingual_service.process_query(raw_query, target_lang=req.language or "auto")
        effective_query = lang_res.get("normalized_english", raw_query)
    else:
        effective_query = raw_query

    res = pipeline.recommend(
        procurement_description=effective_query,
        raw_user_query=raw_query,
        top_k=req.top_k,
        mode=req.mode
    )

    if (req.language and req.language != "auto") or not raw_query.isascii():
        detected_lang = lang_res.get("detected_language", "en")
        if detected_lang != "en":
            res = multilingual_service.localize_results(res, target_lang=detected_lang)

    status_code = 200
    if res["status"] == "needs_clarification":
        status_code = 400
    elif res["status"] == "out_of_domain":
        status_code = 422
    elif res["status"] == "security_blocked":
        status_code = 403

    return JSONResponse(status_code=status_code, content=res)

# ==========================================================
# 1. MODE A — PRODUCT DESCRIPTION & MULTILINGUAL ANALYSIS
# ==========================================================
class AnalyzeRequest(BaseModel):
    description: str
    language: Optional[str] = "auto"
    top_k: Optional[int] = 10
    mode: Optional[str] = "graph_rag"

@app.post("/api/analyze")
def analyze_product_description(req: AnalyzeRequest):
    """
    Mode A Entry Point: Natural-language product description analysis with multilingual support.
    """
    raw_query = req.description or ""
    
    # Multilingual translation / normalization if Indic language
    lang_res = multilingual_service.process_query(raw_query, target_lang=req.language or "auto")
    normalized_query = lang_res.get("normalized_english", raw_query)

    # Execute core AI recommendation pipeline
    res = pipeline.recommend(
        procurement_description=normalized_query,
        raw_user_query=raw_query,
        top_k=req.top_k,
        mode=req.mode
    )

    # Attach multilingual metadata
    res["multilingual_info"] = lang_res
    res["user_original_query"] = raw_query

    # Localize standard titles, scopes, and match reasons into user's language
    detected_lang = lang_res.get("detected_language", "en")
    if detected_lang != "en":
        res = multilingual_service.localize_results(res, target_lang=detected_lang)

    # Save to search history if processed
    if res.get("status") in ["success", "abstain", "needs_clarification", "no_results"]:
        history_store.add_entry(
            query=raw_query,
            mode="product_description",
            result_summary=res,
            language=detected_lang
        )

    status_code = 200
    if res["status"] == "needs_clarification":
        status_code = 400
    elif res["status"] == "out_of_domain":
        status_code = 422
    elif res["status"] == "security_blocked":
        status_code = 403

    return JSONResponse(status_code=status_code, content=res)

# ==========================================================
# 2. MODE B — TECHNICAL SPECIFICATION ANALYSIS
# ==========================================================
class TechnicalSpecRequest(BaseModel):
    product_category: Optional[str] = None
    product_name: Optional[str] = None
    material: Optional[str] = None
    dimensions: Optional[str] = None
    grade: Optional[str] = None
    voltage: Optional[str] = None
    capacity: Optional[str] = None
    application: Optional[str] = None
    environment: Optional[str] = None
    performance_requirements: Optional[str] = None
    safety_requirements: Optional[str] = None
    other_specifications: Optional[str] = None

@app.post("/api/analyze/specification")
def analyze_technical_specification(spec: TechnicalSpecRequest):
    """
    Mode B Entry Point: Structured technical specification form inputs.
    Converts structured input into normalized procurement query.
    """
    parts = []
    if spec.product_name: parts.append(f"Product: {spec.product_name}")
    if spec.product_category: parts.append(f"Category: {spec.product_category}")
    if spec.material: parts.append(f"Material: {spec.material}")
    if spec.voltage: parts.append(f"Voltage: {spec.voltage}")
    if spec.capacity: parts.append(f"Capacity: {spec.capacity}")
    if spec.dimensions: parts.append(f"Dimensions: {spec.dimensions}")
    if spec.grade: parts.append(f"Grade: {spec.grade}")
    if spec.application: parts.append(f"Application: {spec.application}")
    if spec.performance_requirements: parts.append(f"Performance: {spec.performance_requirements}")
    if spec.safety_requirements: parts.append(f"Safety: {spec.safety_requirements}")
    if spec.other_specifications: parts.append(f"Other Specs: {spec.other_specifications}")

    query_str = ". ".join(parts) if parts else "General procurement requirement"

    res = pipeline.recommend(procurement_description=query_str, top_k=10, mode="graph_rag")
    res["structured_input"] = spec.model_dump()

    history_store.add_entry(
        query=query_str,
        mode="technical_specification",
        result_summary=res,
        language="en"
    )

    return res

# ==========================================================
# 3. MODE C — TENDER DOCUMENT UPLOAD & PARSING
# ==========================================================
@app.post("/api/analyze/document")
@app.post("/api/tender/analyze")
async def analyze_tender_document(file: UploadFile = File(...), language: Optional[str] = Query("auto")):
    """
    Mode C Entry Point: PDF, DOCX, or TXT file upload and text requirement extraction with multilingual support.
    """
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        parsed_doc = tender_parser.parse_tender_document(contents, file.filename, target_lang=language or "auto")
        return parsed_doc
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

class TranslateRequest(BaseModel):
    text: str
    target_lang: Optional[str] = "auto"

@app.post("/api/translate")
def translate_query(req: TranslateRequest):
    """
    Multilingual Query Translation & Normalization Endpoint.
    """
    return multilingual_service.process_query(req.text, req.target_lang)

# ==========================================================
# 4. STANDARDS CATALOG & LIFECYCLE ENDPOINTS
# ==========================================================
@app.get("/api/standards")
def list_standards(sector: Optional[str] = Query(None), q: Optional[str] = Query(None)):
    """
    Returns search/browse standards list from catalog.
    """
    return standards_service.list_standards(sector=sector, query=q)

@app.get("/api/standards/{standard_code}")
def get_standard_detail(standard_code: str):
    """
    Returns full detailed record of a single standard with scope, lifecycle, and relationship categories.
    """
    detail = standards_service.get_standard_details(standard_code)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Standard '{standard_code}' not available in verified standards database.")
    return detail

@app.get("/api/standards/{standard_code}/relationships")
@app.get("/api/standards/{standard_code}/related")
def get_standard_relationships(standard_code: str):
    """
    Returns categorized relationships (Normative, Test Methods, Safety, Installation, Terminology, Related Product).
    """
    return standards_service.get_categorized_relationships(standard_code)

@app.get("/api/standards/{standard_code}/lifecycle")
def get_standard_lifecycle(standard_code: str):
    """
    Returns standard lifecycle status (ACTIVE / SUPERSEDED), amendments, and edition year.
    """
    detail = standards_service.get_standard_details(standard_code)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Standard '{standard_code}' not available in database.")
    return detail.get("lifecycle")

@app.get("/api/standards/{standard_code}/regulatory")
def get_standard_regulatory(standard_code: str):
    """
    Returns QCO and regulatory compliance information for a specific standard.
    """
    from integration.pipeline import pipeline
    return pipeline.qco_engine.evaluate_qco_compliance(standard_code)

# ==========================================================
# 5. REGULATORY / QCO FINDER ENDPOINT
# ==========================================================
@app.get("/api/regulatory")
def get_regulatory_records(q: Optional[str] = Query(None)):
    """
    Returns verified QCO and BIS Certification Scheme records.
    """
    all_stds = standards_service.list_standards(query=q)
    qco_records = []
    for s in all_stds:
        code = s.get("is_code")
        details = standards_service.get_standard_details(code)
        if details and details.get("qco_applicability") in ["MANDATORY", "RECOMMENDED"]:
            qco_records.append({
                "is_code": code,
                "title": details.get("title"),
                "sector": details.get("sector"),
                "product_category": details.get("product_category"),
                "qco_applicability": details.get("qco_applicability"),
                "certification_information": details.get("certification_information"),
                "source_provenance": details.get("source_provenance")
            })
    return qco_records

# ==========================================================
# 6. PDF REPORT GENERATION ENDPOINT
# ==========================================================
class ReportRequest(BaseModel):
    query: str
    entities: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]]

@app.post("/api/reports/generate")
def generate_procurement_report(req: ReportRequest):
    """
    Generates downloadable PDF Procurement Standards Report.
    """
    try:
        pdf_bytes = report_generator.generate_pdf_report(req.model_dump())
        filename = f"Procurement_Standards_Report_{int(os.times().elapsed)}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

# ==========================================================
# 7. HISTORY & SAVED ANALYSES ENDPOINTS
# ==========================================================
@app.get("/api/history")
def get_history(saved_only: bool = Query(False)):
    """
    Returns search history or saved project analyses.
    """
    return history_store.list_history(saved_only=saved_only)

class SaveProjectRequest(BaseModel):
    entry_id: str
    project_name: str

@app.post("/api/history/save")
def save_project(req: SaveProjectRequest):
    """
    Saves a history analysis with custom project name.
    """
    res = history_store.save_project(req.entry_id, req.project_name)
    if not res:
        raise HTTPException(status_code=404, detail="Analysis entry not found.")
    return res

# ==========================================================
# 7B. OFFICER REVIEW & AUDIT TRAIL ENDPOINTS
# ==========================================================
class AuditReviewRequest(BaseModel):
    analysis_id: Optional[str] = None
    query: str
    recommended_standard: str
    decision: str  # "ACCEPTED" or "OVERRIDDEN"
    final_standard: str
    officer_name: str
    officer_designation: str
    department: Optional[str] = "GeM / Central Procurement Division"
    justification: str

@app.post("/api/audit/review")
def record_officer_review(req: AuditReviewRequest):
    """
    Records official procurement officer determination (ACCEPT or OVERRIDE) with required justification into statutory audit trail.
    """
    record = history_store.add_audit_review(
        analysis_id=req.analysis_id,
        query=req.query,
        recommended_standard=req.recommended_standard,
        decision=req.decision,
        final_standard=req.final_standard,
        officer_name=req.officer_name,
        officer_designation=req.officer_designation,
        department=req.department or "Government Procurement Division",
        justification=req.justification
    )
    return record

@app.get("/api/audit/trail")
def get_audit_trail():
    """
    Returns complete chronological statutory audit trail of procurement officer determinations.
    """
    return history_store.list_audit_trail()

# ==========================================================
# 8. ADMIN / DIAGNOSTICS ENDPOINT (SIH METRICS ISOLATED)
# ==========================================================
@app.get("/api/admin/metrics")
def get_admin_metrics():
    """
    Returns technical benchmark metrics, latency stats, and system diagnostics for Admin dashboard.
    """
    facts_path = os.path.join(BASE_DIR, 'docs', 'project_facts.json')
    facts = {}
    if os.path.exists(facts_path):
        with open(facts_path, 'r', encoding='utf-8') as f:
            facts = json.load(f)

    return {
        "system_status": "Healthy",
        "dataset_statistics": {
            "total_verified_standards": len(standards_service.standards_map),
            "total_relationships": len(standards_service.relationships),
            "benchmark_queries": facts.get("ground_truth_statistics", {}).get("total_queries", 195)
        },
        "performance_benchmarks": facts.get("retrieval_evaluation_metrics", {}),
        "security_metrics": facts.get("guardrail_and_security_performance", {}),
        "pipeline_health": {
            "vector_store": pipeline.vector_available,
            "knowledge_graph": pipeline.graph_available,
            "qco_engine": True
        }
    }

@app.get("/api/evaluation/report")
def get_evaluation_report():
    report_path = os.path.join(BASE_DIR, 'outputs', 'phase6_evaluation_report.json')
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Evaluation report not found.")
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.get("/eval")
def get_evaluation_dashboard():
    dash_path = os.path.join(BASE_DIR, 'frontend', 'eval_dashboard.html')
    if os.path.exists(dash_path):
        return FileResponse(dash_path)
    raise HTTPException(status_code=404, detail="Evaluation dashboard UI not found.")

# ==========================================================
# FRONTEND UI SERVING (EXPLICIT FILE ROUTES)
# ==========================================================
@app.get("/")
def read_root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "StandardSaarthi API active"}

@app.get("/{filename}")
def read_frontend_static(filename: str):
    # Only serve static files if they exist in frontend dir and are not API paths
    if filename.startswith("api") or filename in ["health", "eval"]:
        raise HTTPException(status_code=404, detail="Not Found")
    file_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File Not Found")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("api.routes:app", host="0.0.0.0", port=8000, reload=False)
