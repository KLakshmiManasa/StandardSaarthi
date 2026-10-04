"""
SIH 26108 — Test Embedding Model Failure & Startup Halting
Verifies that:
1. If sentence-transformers fails to load, application startup halts immediately with a clear error.
2. The recommendation pipeline never returns recommendations when the embedding model is unavailable.
3. get_embedder() raises RuntimeError rather than falling back to silent TF-IDF.
"""

import pytest
from fastapi.testclient import TestClient
from api.routes import app
from integration.pipeline import pipeline
from phase2.embeddings.generate_embeddings import get_embedder

def test_app_startup_halts_on_embedding_failure(monkeypatch):
    """
    Simulates embedding model failure and proves application startup halts
    with a clear fatal error message.
    """
    monkeypatch.setattr(pipeline, "vector_available", False)
    monkeypatch.setattr(pipeline, "vector_error", "Mock load failure: sentence-transformers missing")

    with pytest.raises(RuntimeError) as exc_info:
        with TestClient(app):
            pass

    err_text = str(exc_info.value)
    assert "FATAL STARTUP ERROR" in err_text
    assert "sentence-transformers" in err_text
    assert "Mock load failure" in err_text


def test_recommendations_never_returned_on_embedding_failure(monkeypatch):
    """
    Proves that the pipeline never returns recommendations when the embedding model
    is unavailable.
    """
    monkeypatch.setattr(pipeline, "vector_available", False)
    monkeypatch.setattr(pipeline, "vector_error", "Simulated embedding failure")

    sample_query = "Supply of PVC insulated copper electrical cables for building wiring"
    res = pipeline.recommend(sample_query)

    assert res.get("status") == "error"
    assert len(res.get("recommendations", [])) == 0
    assert "Recommendations blocked" in res.get("message", "")


def test_get_embedder_raises_error_on_load_failure(monkeypatch):
    """
    Verifies that get_embedder() raises a RuntimeError if the model cannot be loaded,
    confirming that the silent TF-IDF fallback has been completely removed.
    """
    import sentence_transformers
    def mock_broken_st(*args, **kwargs):
        raise ImportError("No module named 'torch'")

    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", mock_broken_st)

    with pytest.raises(RuntimeError) as exc_info:
        get_embedder()

    err_text = str(exc_info.value)
    assert "Failed to load SentenceTransformer model" in err_text
    assert "TF-IDF fallback has been removed" in err_text
