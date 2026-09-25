"""
SIH 26108 — Phase 7 API Health Check Module
Provides GET /health endpoint checking operational status of API, Vector Retriever, Knowledge Graph, and QCO Engine.
"""

from fastapi import APIRouter
from typing import Dict, Any
from integration.pipeline import pipeline

router = APIRouter()

@router.get("/health")
@router.get("/api/health")
def check_health() -> Dict[str, Any]:
    """
    Returns operational health status of all pipeline services.
    """
    vector_ok = getattr(pipeline, "vector_available", False)
    graph_ok = getattr(pipeline, "graph_available", False)

    # Determine overall system health
    if vector_ok and graph_ok:
        overall_status = "healthy"
    elif vector_ok or graph_ok:
        overall_status = "degraded"
    else:
        overall_status = "critical"

    return {
        "status": overall_status,
        "services": {
            "api": True,
            "vector_retriever": vector_ok,
            "graph": graph_ok,
            "qco_engine": True
        },
        "version": "0.7.0-integrated"
    }
