"""
Multilingual Output & Localization Service for StandardSaarthi (SIH 26108).
Provides centralized language validation, protected technical entity masking/unmasking,
multi-provider translation, caching, debug tracking, and localized recommendation/standard detail response generation.
"""

import re
import hashlib
import json
import logging
from typing import Dict, Any, List, Tuple, Optional

from config.languages import SUPPORTED_LANGUAGES, UI_LOCALIZATION_MAP
from services.translation_service import translation_service

logger = logging.getLogger("LocalizationService")

# Glossary fallbacks for user explanations when translation API is unavailable
LOCALIZATION_GLOSSARY = {
    "hi": {
        "Scope verified from official BIS documentation.": "आधिकारिक बीआईएस दस्तावेजों से स्कोप का सत्यापन किया गया।",
        "Mandatory ISI Certification is required under Central Ministry Quality Control Order (QCO).": "केंद्रीय मंत्रालय के गुणवत्ता नियंत्रण आदेश (QCO) के तहत अनिवार्य आईएसआई प्रमाणन आवश्यक है।",
        "Product description and technical parameters match standard scope.": "उत्पाद विवरण और तकनीकी पैरामीटर मानक स्कोप से मेल खाते हैं।",
        "General procurement item.": "सामान्य खरीद वस्तु।",
        "No verified Indian Standard matching query found in database.": "डेटाबेस में प्रश्न से मेल खाने वाला कोई सत्यापित भारतीय मानक नहीं मिला।"
    },
    "ta": {
        "Scope verified from official BIS documentation.": "அதிகாரப்பூர்வ பிஐஎஸ் ஆவணங்களிலிருந்து வரம்பு சரிபார்க்கப்பட்டது.",
        "Mandatory ISI Certification is required under Central Ministry Quality Control Order (QCO).": "மத்திய அமைச்சகத்தின் தரக் கட்டுப்பாட்டு ஆணையின் (QCO) கீழ் கட்டாய ISI சான்றிதழ் தேவைப்படுகிறது.",
        "Product description and technical parameters match standard scope.": "தயாரிப்பு விளக்கம் மற்றும் தொழில்நுட்ப அளவுருக்கள் தரநிலை வரம்புடன் பொருந்துகின்றன."
    },
    "te": {
        "Scope verified from official BIS documentation.": "అధికారిక BIS డాక్యుమెంటేషన్ నుండి పరిధి ధృవీకరించబడింది.",
        "Mandatory ISI Certification is required under Central Ministry Quality Control Order (QCO).": "కేంద్ర మంత్రిత్వ శాఖ క్వాలిటీ కంట్రోల్ ఆర్డర్ (QCO) ప్రకారం నిర్బంధ ISI సర్టిఫికేషన్ అవసరం."
    }
}


class ProtectedEntityEngine:
    """
    Masks official technical identifiers, standard codes, clause numbers, technical values,
    units, QCO Gazette references, abbreviations (PVC, ISI, QCO, etc.), and URLs with temporary
    placeholders before translation, and restores them 100% untouched afterwards.
    """

    PATTERNS = [
        # URLs
        r'(https?://[^\s>]+)',
        # Gazette references
        r'(S\.O\.\s*\d+\([A-Z]\))',
        # Standard Codes (e.g., IS 14543:2024, IS 694:2010, IS 694, IS 1554:Part 1, IS/IEC 60502-1, ISO 9001, IEC 60502)
        r'\b((?:IS|ISO|IEC|IS/IEC)\s*[\d\:\-\.\/]+(?:\:Part\s*\d+)?(?::\d{4})?)\b',
        # Clauses & Annexes
        r'\b((?:Clause|Annex)\s+[\d\.\w]+)\b',
        # Technical values & units (e.g., 1.5 sq mm, 230 V, 50 Hz, 1100 V, 70°C, 20 L, 95%, M30, 100 kVA, 11kV)
        r'\b(\d+(?:\.\d+)?\s*(?:sq\s*mm|mm|cm|m|kg|kV|kVA|V|Hz|L|%|M30|°C))\b',
        # Standard Technical Abbreviations
        r'\b(PVC|ISI|QCO|IEC|ISO|BIS|XLPE|FRLS|HT|LT|AC|DC)\b',
    ]

    def __init__(self):
        self.combined_regex = re.compile('|'.join(self.PATTERNS), re.IGNORECASE)

    def mask(self, text: str) -> Tuple[str, Dict[str, str]]:
        if not text or not isinstance(text, str):
            return text, {}

        entities = {}
        counter = 0

        def replace_match(match):
            nonlocal counter
            val = match.group(0).strip()
            placeholder = f"__PROTECTED_ENTITY_{counter}__"
            entities[placeholder] = val
            counter += 1
            return placeholder

        masked_text = self.combined_regex.sub(replace_match, text)
        return masked_text, entities

    def unmask(self, masked_text: str, entities: Dict[str, str]) -> str:
        if not masked_text or not entities:
            return masked_text

        result = masked_text
        for placeholder, original in entities.items():
            num = placeholder.replace("__PROTECTED_ENTITY_", "").replace("__", "")
            pattern = re.compile(r'__\s*(?:PROTECTED_ENTITY_|ENTITY_?|PROTECTED_?)?\s*' + num + r'\s*__', re.IGNORECASE)
            if pattern.search(result):
                result = pattern.sub(original, result)
            elif placeholder in result:
                result = result.replace(placeholder, original)
            elif original not in result:
                result = f"{result} ({original})"
        return result


class LocalizationService:
    """
    Multilingual Translation & Localization Service for StandardSaarthi.
    Supports 9 Official Languages with multi-tiered fallbacks.
    """

    def __init__(self):
        self.entity_engine = ProtectedEntityEngine()
        self.cache: Dict[str, str] = {}
        self.last_provider_used = "none"
        self.last_fallback_used = False

    def validate_language(self, lang_code: Optional[str]) -> str:
        """Validates language code against 9 official supported languages. Returns valid code or 'en'."""
        if not lang_code or not isinstance(lang_code, str):
            return "en"
        code = lang_code.strip().lower()
        if code in SUPPORTED_LANGUAGES:
            return code
        logger.warning(f"Unsupported output_language '{lang_code}' requested. Falling back to 'en'.")
        return "en"

    def translate_text(self, text: str, target_lang: str) -> str:
        """
        Translates user-facing text to target_lang while protecting technical entities.
        Uses in-memory cache and multi-tiered provider pipeline.
        """
        target_lang = self.validate_language(target_lang)
        if target_lang == "en" or not text or not text.strip():
            self.last_provider_used = "none"
            self.last_fallback_used = False
            return text

        cache_key = hashlib.sha256(f"{text}||{target_lang}".encode('utf-8')).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        glossary = LOCALIZATION_GLOSSARY.get(target_lang, {})
        masked_text, entities = self.entity_engine.mask(text)

        translated_masked, provider, fallback = translation_service.translate(masked_text, target_lang, glossary)
        self.last_provider_used = provider
        if fallback:
            self.last_fallback_used = True

        final_text = self.entity_engine.unmask(translated_masked, entities)
        self.cache[cache_key] = final_text
        return final_text

    def localize_recommendation_response(self, response: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """
        Localizes recommendation response payload for target_language.
        Recommendation logic, scores, and IS codes remain 100% independent and untouched.
        """
        lang = self.validate_language(target_language)
        localized = dict(response)
        localized["input_language"] = response.get("input_language") or response.get("language") or "en"
        localized["output_language"] = lang
        localized["output_language_name"] = SUPPORTED_LANGUAGES.get(lang, "English")

        if lang == "en":
            localized["ui_labels"] = UI_LOCALIZATION_MAP.get("en")
            return localized

        translated_fields_list = []
        providers_used_set = set()
        fallback_occurred = False

        recs = localized.get("recommendations", [])
        localized_recs = []

        for rec in recs:
            rec_copy = dict(rec)
            
            if "title" in rec_copy:
                rec_copy["official_title"] = rec_copy["title"]
                translated_title = self.translate_text(rec_copy["title"], lang)
                rec_copy["localized_title"] = translated_title
                rec_copy["title"] = translated_title
                translated_fields_list.append("title")

            if "scope" in rec_copy and rec_copy["scope"]:
                rec_copy["localized_scope"] = self.translate_text(rec_copy["scope"], lang)
                rec_copy["scope"] = rec_copy["localized_scope"]
                translated_fields_list.append("scope")

            if "relevance_explanation" in rec_copy and rec_copy["relevance_explanation"]:
                rec_copy["localized_reason"] = self.translate_text(rec_copy["relevance_explanation"], lang)
                rec_copy["relevance_explanation"] = rec_copy["localized_reason"]
                translated_fields_list.append("relevance_explanation")

            if "ranking_reasons" in rec_copy and isinstance(rec_copy["ranking_reasons"], list):
                rec_copy["ranking_reasons"] = [self.translate_text(r, lang) for r in rec_copy["ranking_reasons"]]
                translated_fields_list.append("ranking_reasons")

            if "reasons" in rec_copy and isinstance(rec_copy["reasons"], list):
                rec_copy["reasons"] = [self.translate_text(r, lang) for r in rec_copy["reasons"]]
                translated_fields_list.append("reasons")

            if "qco_compliance" in rec_copy and isinstance(rec_copy["qco_compliance"], dict):
                qco_copy = dict(rec_copy["qco_compliance"])
                if "notice" in qco_copy and qco_copy["notice"]:
                    qco_copy["localized_notice"] = self.translate_text(qco_copy["notice"], lang)
                    qco_copy["notice"] = qco_copy["localized_notice"]
                if "scheme" in qco_copy and qco_copy["scheme"]:
                    qco_copy["scheme"] = self.translate_text(qco_copy["scheme"], lang)
                rec_copy["qco_compliance"] = qco_copy
                rec_copy["localized_compliance"] = qco_copy
                translated_fields_list.append("qco_compliance")

            localized_recs.append(rec_copy)

        localized["recommendations"] = localized_recs

        if "message" in localized and localized["message"]:
            localized["message"] = self.translate_text(localized["message"], lang)
            translated_fields_list.append("message")

        main_provider = list(providers_used_set)[0] if providers_used_set else self.last_provider_used
        localized["translation_debug"] = {
            "requested_language": lang,
            "translation_provider": main_provider,
            "translated_fields": list(set(translated_fields_list)),
            "fallback_used": fallback_occurred
        }

        localized["ui_labels"] = UI_LOCALIZATION_MAP.get(lang, UI_LOCALIZATION_MAP.get("en"))
        return localized

    def localize_standard_details(self, details: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """
        Localizes the Standard Details page record for target_language without overwriting official database values.
        """
        lang = self.validate_language(target_language)
        localized = dict(details)
        localized["output_language"] = lang
        localized["output_language_name"] = SUPPORTED_LANGUAGES.get(lang, "English")

        if lang == "en":
            localized["ui_labels"] = UI_LOCALIZATION_MAP.get("en")
            return localized

        if "title" in localized and localized["title"]:
            localized["official_title"] = localized["title"]
            localized["localized_title"] = self.translate_text(localized["title"], lang)
            localized["title"] = localized["localized_title"]

        if "scope" in localized and localized["scope"]:
            localized["official_scope"] = localized["scope"]
            localized["localized_scope"] = self.translate_text(localized["scope"], lang)
            localized["scope"] = localized["localized_scope"]

        if "description" in localized and localized["description"]:
            localized["localized_description"] = self.translate_text(localized["description"], lang)
            localized["description"] = localized["localized_description"]

        if "applications" in localized and isinstance(localized["applications"], list):
            localized["localized_applications"] = [self.translate_text(app, lang) for app in localized["applications"]]

        if "materials" in localized and isinstance(localized["materials"], list):
            localized["localized_materials"] = [self.translate_text(mat, lang) for mat in localized["materials"]]

        if "technical_parameters" in localized and isinstance(localized["technical_parameters"], dict):
            tech_loc = {}
            for k, v in localized["technical_parameters"].items():
                if isinstance(v, str):
                    tech_loc[k] = self.translate_text(v, lang)
                else:
                    tech_loc[k] = v
            localized["localized_technical_parameters"] = tech_loc

        localized["ui_labels"] = UI_LOCALIZATION_MAP.get(lang, UI_LOCALIZATION_MAP.get("en"))
        return localized


localization_service = LocalizationService()
