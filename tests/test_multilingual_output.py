"""
Comprehensive Test Suite for 9 Supported Official Languages (SIH 26108).
Verifies exact 9 language configuration, technical entity preservation, standard details localization,
FastAPI endpoints, PDF report generation, and language journey persistence.
"""

import pytest
from fastapi.testclient import TestClient

from api.routes import app
from config.languages import SUPPORTED_LANGUAGES, UI_LOCALIZATION_MAP
from services.localization_service import (
    localization_service,
    ProtectedEntityEngine
)
from services.report_generator import report_generator

client = TestClient(app)


class TestLanguageConfiguration:
    """Unit tests for 9 Official Supported Languages Configuration."""

    def test_exact_9_official_languages_present(self):
        expected_codes = ["en", "hi", "ta", "te", "bn", "gu", "pa", "ml", "kn"]
        assert len(SUPPORTED_LANGUAGES) == 9
        for code in expected_codes:
            assert code in SUPPORTED_LANGUAGES, f"Missing expected language code '{code}'"

    def test_language_validation(self):
        assert localization_service.validate_language("en") == "en"
        assert localization_service.validate_language("hi") == "hi"
        assert localization_service.validate_language("ta") == "ta"
        assert localization_service.validate_language("te") == "te"
        assert localization_service.validate_language("bn") == "bn"
        assert localization_service.validate_language("gu") == "gu"
        assert localization_service.validate_language("pa") == "pa"
        assert localization_service.validate_language("ml") == "ml"
        assert localization_service.validate_language("kn") == "kn"
        assert localization_service.validate_language("invalid_code") == "en"
        assert localization_service.validate_language(None) == "en"


class TestTechnicalEntityPreservation:
    """Tests for ProtectedEntityEngine regex masking and 100% entity preservation."""

    def test_protected_entity_engine_masking_and_unmasking(self):
        engine = ProtectedEntityEngine()
        sample_text = (
            "Mandatory ISI certification for IS 14543:2024 and IS 694 operating at 230 V 50 Hz "
            "under Clause 5.2 and S.O. 4210(E) with PVC insulation. Visit https://standards.bis.gov.in/."
        )

        masked_text, entities = engine.mask(sample_text)
        assert "__PROTECTED_ENTITY_" in masked_text
        restored = engine.unmask(masked_text, entities)
        assert restored == sample_text

    def test_technical_entity_preservation_during_translation(self):
        sample_text = "Product specification matches IS 694 for 1100 V cables with PVC insulation under Clause 4.1 requiring mandatory QCO."

        for lang in ["hi", "ta", "te", "bn", "gu", "pa", "ml", "kn"]:
            translated = localization_service.translate_text(sample_text, lang)
            assert "IS 694" in translated, f"IS 694 lost in target language {lang}"
            assert "1100 V" in translated or "1100V" in translated, f"1100 V lost in target language {lang}"
            assert "PVC" in translated, f"PVC lost in target language {lang}"
            assert "Clause 4.1" in translated, f"Clause 4.1 lost in target language {lang}"
            assert "QCO" in translated, f"QCO lost in target language {lang}"


class TestRecommendationLocalization:
    """Unit tests for response payload post-processing localization."""

    def test_localize_recommendation_response_translates_title(self):
        mock_response = {
            "query": "PVC Insulated Cable",
            "status": "success",
            "recommendations": [
                {
                    "is_code": "IS 694",
                    "title": "Polyvinyl Chloride Insulated Cables for Working Voltages Up to and Including 1100 V",
                    "relevance_score": 0.95,
                    "scope": "Scope verified from official BIS documentation.",
                    "ranking_reasons": ["Product description matches IS 694"],
                    "qco_compliance": {
                        "qco_mandatory": True,
                        "notice": "Mandatory ISI Certification under Central Ministry Quality Control Order."
                    }
                }
            ]
        }

        localized_hi = localization_service.localize_recommendation_response(mock_response, "hi")
        assert localized_hi["output_language"] == "hi"
        rec = localized_hi["recommendations"][0]
        assert rec["is_code"] == "IS 694"
        assert rec["official_title"] == "Polyvinyl Chloride Insulated Cables for Working Voltages Up to and Including 1100 V"
        assert rec["title"] != ""
        assert rec["title"] != rec["official_title"]
        assert "ui_labels" in localized_hi


class TestStandardDetailsLocalization:
    """Tests for Standard Details page localization API."""

    def test_standard_details_api_localization(self):
        resp = client.get("/api/standards/IS%20694?output_language=hi")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_code"] == "IS 694"
        assert data["output_language"] == "hi"
        assert "ui_labels" in data
        assert "विवरण और जीवन चक्र" in data["ui_labels"]["details_and_lifecycle"]


class TestAPIOutputLocalizationMatrix:
    """Integration tests for FastAPI endpoints across 9 supported languages."""

    def test_hindi_input_and_hindi_output(self):
        payload = {
            "description": "मुझे बिल्डिंग के अंदर इलेक्ट्रिकल वायरिंग के लिए केबल चाहिए, जिनमें कॉपर कंडक्टर और PVC इंसुलेशन हो।",
            "language": "auto",
            "output_language": "hi"
        }
        resp = client.post("/api/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert data["status"] == "success"
        assert data["output_language"] == "hi"
        top_rec = data["recommendations"][0]
        assert top_rec["is_code"] == "IS 694"
        assert top_rec["title"] != top_rec["official_title"]

    def test_hindi_input_and_tamil_output(self):
        payload = {
            "description": "मुझे बिल्डिंग के अंदर इलेक्ट्रिकल वायरिंग के लिए केबल चाहिए, जिनमें कॉपर कंडक्टर और PVC इंसुलेशन हो।",
            "language": "auto",
            "output_language": "ta"
        }
        resp = client.post("/api/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert data["status"] == "success"
        assert data["output_language"] == "ta"
        top_rec = data["recommendations"][0]
        assert top_rec["is_code"] == "IS 694"
        assert top_rec["title"] != top_rec["official_title"]

    def test_all_9_languages_output_matrix(self):
        query = "Procurement of 1.5 sq mm PVC insulated copper electrical cable 1100V"
        for lang_code in ["en", "hi", "ta", "te", "bn", "gu", "pa", "ml", "kn"]:
            resp = client.post("/api/analyze", json={"description": query, "output_language": lang_code})
            assert resp.status_code == 200
            data = resp.json()
            assert data["output_language"] == lang_code
            assert len(data["recommendations"]) > 0
            assert data["recommendations"][0]["is_code"] == "IS 694"


class TestMultilingualPDFReportGeneration:
    """Tests for localized PDF report generation across 9 supported languages."""

    def test_pdf_generation_for_all_9_languages(self):
        analysis_data = {
            "query": "PVC Insulated Cable",
            "entities": {"product": "Electric Cable", "materials": ["PVC", "Copper"]},
            "recommendations": [
                {
                    "is_code": "IS 694",
                    "title": "PVC Insulated Cables for Working Voltages Up to and Including 1100V",
                    "relevance_score": 0.98,
                    "scope": "Scope verified from official BIS documentation.",
                    "qco_compliance": {"qco_mandatory": True}
                }
            ]
        }

        for lang in ["en", "hi", "ta", "te", "bn", "gu", "pa", "ml", "kn"]:
            pdf_bytes = report_generator.generate_pdf_report(analysis_data, output_language=lang)
            assert isinstance(pdf_bytes, bytes)
            assert pdf_bytes.startswith(b"%PDF")
