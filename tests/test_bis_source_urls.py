"""
Automated Test Suite for BIS Source Authority Navigation & External URL Validation.
Tests `is_external_bis_url`, `validate_source` logic, IS 8130:2013 exact BIS portal URL, structured `source` data model,
relative path rejection, legacy URL rejection, non-BIS domain rejection, and missing URL fallback handling.
"""

import pytest
from fastapi.testclient import TestClient

from api.routes import app
from services.standards_service import standards_service, is_external_bis_url, validate_source

client = TestClient(app)

def test_a_valid_external_bis_url():
    """Test A: Valid absolute HTTPS BIS URLs return True, legacy services.bis.gov.in returns False."""
    assert is_external_bis_url("https://standards.bis.gov.in/") is True
    assert is_external_bis_url("https://www.bis.gov.in/") is True
    # Legacy URL rejection
    assert is_external_bis_url("https://services.bis.gov.in/php/BIS_2.0/bisconnect/ISL/is_details?IDS=MTUyMDM%3D") is False
    assert is_external_bis_url("https://www.services.bis.gov.in/php/BIS_2/bisweb/standard_details/IS+694") is False

def test_b_missing_url_fallback():
    """Test B: Missing / None URL returns False and triggers fallback."""
    assert is_external_bis_url(None) is False
    assert is_external_bis_url("") is False

def test_c_invalid_relative_url_rejection():
    """Test C: Relative paths and scheme-less URLs are rejected."""
    assert is_external_bis_url("services.bis.gov.in/php/BIS_2.0/bisconnect/ISL/is_details?IDS=MTUyMDM%3D") is False
    assert is_external_bis_url("/services.bis.gov.in/php/BIS_2.0/") is False
    assert is_external_bis_url("/bis-source/IS8130") is False
    assert is_external_bis_url("http://localhost:8000/BIS%20Standards%20Catalog%202024") is False

def test_d_validate_source_rules():
    """Test D: validate_source enforces authority, portalUrl, and specificUrl rules."""
    valid_source = {
        "authority": "Bureau of Indian Standards (BIS)",
        "authorityUrl": "https://www.bis.gov.in/",
        "portalUrl": "https://standards.bis.gov.in/",
        "specificUrl": None,
        "verified": True,
        "sourceType": "official_bis"
    }
    assert validate_source(valid_source) is True

    # Invalid authority
    bad_auth = dict(valid_source, authority="Fake Agency")
    assert validate_source(bad_auth) is False

    # Invalid portalUrl
    bad_portal = dict(valid_source, portalUrl="http://fakeportal.com")
    assert validate_source(bad_portal) is False

    # Obsolete legacy specificUrl
    legacy_url = dict(valid_source, specificUrl="https://services.bis.gov.in/php/BIS_2.0/is_details?IDS=MTUyMDM%3D")
    assert validate_source(legacy_url) is False

def test_e_is_8130_exact_official_bis_portal_and_lifecycle():
    """Test E: IS 8130 returns BIS Standards Portal, specificUrl=None, and verified lifecycle data."""
    resp = client.get("/api/standards/IS%208130")
    assert resp.status_code == 200
    details = resp.json()
    assert details["is_code"] == "IS 8130"
    assert details["standardNumber"] == "IS 8130:2013"
    assert "Conductors for insulated electric cables" in details["title"]
    assert details["publicationYear"] == 2013
    assert details["revisionNumber"] == 2
    assert details["revisionLabel"] == "Second Revision"
    assert details["reviewYear"] == 2025
    assert details["amendmentCount"] == 2
    assert len(details["amendments"]) == 2
    assert details["lifecycleStatus"] == "CURRENT / VERIFIED"

    # Structured source object
    source = details["source"]
    assert source["authority"] == "Bureau of Indian Standards (BIS)"
    assert source["portalUrl"] == "https://standards.bis.gov.in/"
    assert source["specificUrl"] is None
    assert source["verified"] is True
    assert validate_source(source) is True

def test_f_phase13_multi_standard_lifecycle_schema():
    """Test F: Phase 13 lifecycle schema dynamically loads for IS 694, IS 1554, IS 456, IS 383, IS 1180."""
    stds_to_test = ["IS 694", "IS 1554:Part 1", "IS 456", "IS 383", "IS 1180:Part 1"]
    for code in stds_to_test:
        resp = client.get(f"/api/standards/{code}")
        assert resp.status_code == 200
        details = resp.json()
        assert "publicationYear" in details
        assert "revisionLabel" in details
        assert "amendmentCount" in details
        assert "lifecycleStatus" in details
        assert details["lifecycleStatus"] in ["CURRENT / VERIFIED", "SUPERSEDED", "STATUS REQUIRES VERIFICATION"]
        assert validate_source(details["source"]) is True


