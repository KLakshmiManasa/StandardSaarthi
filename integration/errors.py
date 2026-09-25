"""
SIH 26108 — Phase 7 Exception Handling & Graceful Degradation
Handles pipeline failures, database disconnects, and unhandled exceptions safely without leaking internal stack traces.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SIH26108_Pipeline")

class PipelineExecutionException(Exception):
    def __init__(self, message: str, stage: str = "pipeline"):
        super().__init__(message)
        self.message = message
        self.stage = stage

async def global_exception_handler(request: Request, exc: Exception):
    """
    Global FastAPI exception handler returning safe user-facing JSON response.
    """
    logger.error(f"Unhandled pipeline error on path {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Unable to process the request due to an internal processing error. Please try again.",
            "warnings": ["Service encountered a temporary execution issue."],
            "processing": {
                "retrieval_method": "Unknown",
                "candidate_count": 0,
                "latency_ms": 0.0,
                "engine_version": "0.7.0-integrated"
            }
        }
    )
