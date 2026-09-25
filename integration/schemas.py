"""
SIH 26108 — Phase 7 Integration Schemas
Defines stable, versioned Pydantic response and request models for the Indian Standards Recommendation API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class RecommendRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=2000, description="Natural language procurement specification text")
    top_k: int = Field(10, ge=1, le=50, description="Number of top recommendations to return")
    mode: str = Field("graph_rag", description="Retrieval pipeline mode: 'graph_rag', 'vector', or 'keyword'")
    language: Optional[str] = Field("auto", description="Query input language code (e.g. 'en', 'hi', 'ta')")

class EntitySummary(BaseModel):
    product: Optional[str] = Field(None, description="Primary product or equipment extracted")
    category: Optional[str] = Field(None, description="Product category or sector")
    materials: List[str] = Field(default_factory=list, description="Extracted raw materials")
    application: Optional[str] = Field(None, description="Intended usage or installation application")
    industry: Optional[str] = Field(None, description="Target industry domain")

class QCODetail(BaseModel):
    applicable: bool = Field(..., description="Whether a verified mandatory QCO exists")
    reference: Optional[str] = Field(None, description="QCO Gazette Order reference ID")
    requirements: List[str] = Field(default_factory=list, description="Mandatory compliance requirements")
    source: Optional[Dict[str, Any]] = Field(None, description="Source provenance of QCO notification")

class EvidenceItem(BaseModel):
    organization: str = Field(..., description="Source organization e.g. BIS")
    document: str = Field(..., description="Official source catalog or gazette document")
    url: str = Field(..., description="Verified direct URL link")

class ClauseItem(BaseModel):
    clause_no: str = Field(..., description="Clause number or title")
    content: str = Field(..., description="Clause content snippet")

class StandardRecommendation(BaseModel):
    rank: int = Field(..., description="Recommendation rank position")
    is_code: str = Field(..., description="Indian Standard IS Code e.g. IS 694")
    title: str = Field(..., description="Official title of the Indian Standard")
    relevance_score: float = Field(..., description="Calibrated relevance score (0.0 - 1.0)")
    confidence_level: str = Field(..., description="Confidence rating: HIGH, MEDIUM, LOW")
    reasons: List[str] = Field(default_factory=list, description="Grounded explanation points")
    qco: QCODetail = Field(..., description="QCO regulatory compliance information")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Supporting provenance evidence links")
    related_standards: List[str] = Field(default_factory=list, description="Normative & related reference IS codes")
    relevant_clauses: List[ClauseItem] = Field(default_factory=list, description="Key normative clause details")

class ProcessingMetadata(BaseModel):
    retrieval_method: str = Field(..., description="Pipeline retrieval method used")
    candidate_count: int = Field(..., description="Total candidates evaluated in pipeline")
    latency_ms: float = Field(..., description="End-to-end processing time in milliseconds")
    dataset_version: str = Field("v0.1-pilot", description="Dataset version string")
    engine_version: str = Field("0.7.0-integrated", description="Engine software version")

class RecommendationResponse(BaseModel):
    status: str = Field(..., description="Pipeline execution status: success, needs_clarification, out_of_domain, security_blocked, no_results, error")
    query: str = Field(..., description="Original or sanitized input query text")
    entities: Optional[EntitySummary] = Field(None, description="Extracted procurement entities")
    recommendations: List[StandardRecommendation] = Field(default_factory=list, description="Ranked list of recommended Indian Standards")
    warnings: List[str] = Field(default_factory=list, description="System warnings or degradation notices")
    message: Optional[str] = Field(None, description="User-facing status explanation or clarification prompt")
    missing_fields: List[str] = Field(default_factory=list, description="Missing technical fields if clarification needed")
    processing: ProcessingMetadata = Field(..., description="Pipeline processing metadata")
