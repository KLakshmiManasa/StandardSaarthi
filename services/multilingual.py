"""
Multilingual Processing Service for SIH 26108 / Product Engine.
Uses `config.languages.SUPPORTED_LANGUAGES` as centralized single source of truth for language maps.
Implements Indian language detection and query translation normalization with fallback dictionary for Indic procurement terms.
"""

import logging
from typing import Dict, Any

from config.languages import SUPPORTED_LANGUAGES

logger = logging.getLogger("MultilingualService")

# Indic Procurement Glossary for Rate-Limit & Fallback Translation
INDIC_GLOSSARY = {
    # Hindi
    "केबल": "cable",
    "केबल्स": "cables",
    "तार": "wire",
    "तारों": "wires",
    "वायर": "wire",
    "वायरिंग": "wiring",
    "पीवीसी": "PVC",
    "इंसुलेशन": "insulation",
    "इंसुलेटेड": "insulated",
    "कॉपर": "copper",
    "तांबा": "copper",
    "तांबे": "copper",
    "कंडक्टर": "conductor",
    "इलेक्ट्रिकल": "electrical",
    "बिजली": "electrical",
    "बिल्डिंग": "building",
    "अंदर": "indoor",
    "चाहिए": "need",
    "खरीद": "procurement",
    "सीमेंट": "cement",
    "कंक्रीट": "concrete",
    "ट्रांसफॉर्मर": "transformer",
    "कन्स्ट्रक्शन": "construction",
    "पानी": "water",
    "पाइप": "pipe",

    # Marathi
    "इमारतीच्या": "building",
    "इमारत": "building",
    "आतील": "indoor",
    "विद्युत": "electrical",
    "वायरिंगच्या": "wiring",
    "कामासाठी": "for work",
    "मला": "need",
    "तांब्याचा": "copper",
    "तांब्याची": "copper",
    "वाहक": "conductor",
    "इन्सुलेशन": "insulation",
    "असलेली": "having",
    "हवी": "need",
    "आहे": "",
    "साठी": "for",
    "आणि": "and",
    
    # Tamil
    "கேபிள்": "cable",
    "கேபிள்கள்": "cables",
    "கம்பி": "wire",
    "வயரிங்": "wiring",
    "பிவிசி": "PVC",
    "இன்சுலேஷன்": "insulation",
    "செம்பு": "copper",
    "தாமிரம்": "copper",
    "காப்பர்": "copper",
    "கண்டக்டர்": "conductor",
    "மின்சார": "electrical",
    "மின்": "electrical",
    "சிமெண்ட்": "cement",
    "கான்கிரீட்": "concrete",
    "மின்மாற்றி": "transformer",
    "கட்டிட": "building",
    "உள்ளே": "indoor",
    "வேண்டும்": "need",

    # Telugu
    "కేబుల్స్": "cables",
    "కేబుల్": "cable",
    "వైరింగ్": "wiring",
    "కాపర్": "copper",
    "కండక్టర్": "conductor",
    "పివిసి": "PVC",
    "ఇన్సులేషన్": "insulation",
    "ఎలక్ట్రికల్": "electrical",
    "భవనం": "building",
    "లోపల": "indoor",
    "కావాలి": "need"
}

# Key technical entity keywords to preserve across translation
ENTITY_KEYWORDS_MAP = {
    "कॉपर": "copper", "तांबा": "copper", "तांबे": "copper", "तांब्याचा": "copper", "तांब्याची": "copper",
    "காப்பர்": "copper", "தாமிரம்": "copper", "செம்பு": "copper", "కాపర్": "copper",
    "कंडक्टर": "conductor", "वाहक": "conductor", "கண்டக்டர்": "conductor", "కండక్టర్": "conductor",
    "पीवीसी": "PVC", "इन्सुलेशन": "insulation", "பிவிசி": "PVC", "పివిసి": "PVC", "pvc": "PVC",
    "इंसुलेशन": "insulation", "இன்சுலேஷன்": "insulation", "ఇన్సులేషన్": "insulation",
    "इलेक्ट्रिकल": "electrical", "विद्युत": "electrical", "மின்சார": "electrical", "ఎలక్ట్రికల్": "electrical",
    "केबल": "cable", "केबल्स": "cables", "கேபிள்": "cable", "கேபிள்கள்": "cables", "కేబుల్స్": "cables", "కేబుల్": "cable",
    "वायरिंग": "wiring", "वायरिंगच्या": "wiring", "வயரிங்": "wiring", "వైరిங்": "wiring",
    "बिल्डिंग": "building", "इमारतीच्या": "building", "कட்டிட": "building", "భవనం": "building"
}

MARATHI_MARKERS = [
    "साठी", "कामासाठी", "आतील", "इमारतीच्या", "मला", "हवी", "आहे", "तांब्याचा", "तांब्याची", "वाहक", "असलेली",
    "माझ्या", "पाहिजे", "करणे", "आहेत", "करायचे", "किंवा", "सर्व", "झाले", "नाही", "काय", "आणि", "इन्सुलेशन",
    "च्या", "तील", "मध्ये", "कडून", "मुळे", "णारे", "णार", "करावे"
]

HINDI_MARKERS = [
    "मुझे", "चाहिए", "अंदर", "का", "की", "को", "से", "में", "पर", "और", "हो", "है", "होना", "जिसमें",
    "जिन्हें", "करता", "करते", "करती", "होगा", "होगी", "करें", "इंसुलेशन", "कॉपर", "तांबा"
]


class MultilingualService:
    def __init__(self):
        try:
            import mtranslate
            self.mtranslate = mtranslate
            self.available = True
        except ImportError:
            self.mtranslate = None
            self.available = False

    def detect_language(self, text: str, target_lang: str = "auto") -> Dict[str, Any]:
        """
        Detects language of input text using script inspection and lexical classification.
        Respects explicit manual selection if target_lang != 'auto'.
        Uses SUPPORTED_LANGUAGES as single source of truth.
        """
        if target_lang and target_lang != "auto":
            return {
                "code": target_lang,
                "name": SUPPORTED_LANGUAGES.get(target_lang, target_lang),
                "method": "manual_selection",
                "confidence": 1.0
            }

        text_str = str(text or "").strip()
        if not text_str or text_str.isascii():
            return {
                "code": "en",
                "name": SUPPORTED_LANGUAGES.get("en", "English"),
                "method": "ascii_check",
                "confidence": 1.0
            }

        # Check non-Devanagari script ranges for Eighth Schedule languages
        if any('\u0b80' <= c <= '\u0bff' for c in text_str):
            return {"code": "ta", "name": SUPPORTED_LANGUAGES["ta"], "method": "script_detection", "confidence": 0.99}
        if any('\u0c00' <= c <= '\u0c7f' for c in text_str):
            return {"code": "te", "name": SUPPORTED_LANGUAGES["te"], "method": "script_detection", "confidence": 0.99}
        if any('\u0c80' <= c <= '\u0cff' for c in text_str):
            return {"code": "kn", "name": SUPPORTED_LANGUAGES["kn"], "method": "script_detection", "confidence": 0.99}
        if any('\u0d00' <= c <= '\u0d7f' for c in text_str):
            return {"code": "ml", "name": SUPPORTED_LANGUAGES["ml"], "method": "script_detection", "confidence": 0.99}
        if any('\u0980' <= c <= '\u09ff' for c in text_str):
            return {"code": "bn", "name": SUPPORTED_LANGUAGES["bn"], "method": "script_detection", "confidence": 0.99}
        if any('\u0a80' <= c <= '\u0aff' for c in text_str):
            return {"code": "gu", "name": SUPPORTED_LANGUAGES["gu"], "method": "script_detection", "confidence": 0.99}
        if any('\u0a00' <= c <= '\u0a7f' for c in text_str):
            return {"code": "pa", "name": SUPPORTED_LANGUAGES["pa"], "method": "script_detection", "confidence": 0.99}
        if any('\u0b00' <= c <= '\u0b7f' for c in text_str):
            return {"code": "or", "name": SUPPORTED_LANGUAGES["or"], "method": "script_detection", "confidence": 0.99}
        if any('\u0600' <= c <= '\u06ff' for c in text_str) or any('\u0750' <= c <= '\u077f' for c in text_str):
            return {"code": "ur", "name": SUPPORTED_LANGUAGES["ur"], "method": "script_detection", "confidence": 0.99}
        if any('\u1c50' <= c <= '\u1c7f' for c in text_str):
            return {"code": "sat", "name": SUPPORTED_LANGUAGES["sat"], "method": "script_detection", "confidence": 0.99}

        # Devanagari script range check (Hindi, Marathi, Sanskrit, Bodo, Dogri, Konkani, Maithili, Nepali)
        if any('\u0900' <= c <= '\u097f' for c in text_str):
            has_lla = '\u0933' in text_str
            t_lower = text_str.lower()
            mr_score = 5 if has_lla else 0
            hi_score = 0

            for kw in MARATHI_MARKERS:
                if kw in t_lower:
                    mr_score += 2

            for kw in HINDI_MARKERS:
                if kw in t_lower:
                    hi_score += 2

            if mr_score > hi_score:
                det_code = "mr"
            else:
                det_code = "hi"

            return {
                "code": det_code,
                "name": SUPPORTED_LANGUAGES.get(det_code, "Hindi"),
                "method": "devanagari_lexical_classification",
                "confidence": 0.95
            }

        return {
            "code": "en",
            "name": "English",
            "method": "default_fallback",
            "confidence": 0.5
        }

    def translate_to_english(self, text: str, source_lang: str = "auto") -> Dict[str, Any]:
        """
        Normalizes input text from Indian languages to English for recommendation processing.
        """
        text_str = str(text or "").strip()
        det = self.detect_language(text_str, target_lang=source_lang)
        lang_code = det["code"]

        if not text_str:
            return {
                "original_text": text_str,
                "normalized_english": text_str,
                "detected_language": lang_code,
                "language_name": det["name"],
                "is_translated": False,
                "method": "none",
                "detection_details": det
            }

        if source_lang == "auto" and (text_str.isascii() or lang_code == "en"):
            return {
                "original_text": text_str,
                "normalized_english": text_str,
                "detected_language": "en",
                "language_name": "English",
                "is_translated": False,
                "method": "ascii_check",
                "detection_details": det
            }

        translated_text = None
        method_used = "glossary_fallback"

        # Try mtranslate
        if self.available and self.mtranslate:
            try:
                translated_text = self.mtranslate.translate(text_str, 'en', 'auto')
                if translated_text and translated_text.strip() != text_str:
                    method_used = "mtranslate"
            except Exception as e:
                logger.warning(f"mtranslate error during input translation: {e}")

        # Fallback dictionary normalization
        if not translated_text or translated_text.strip() == text_str:
            words = text_str.split()
            norm_words = []
            for w in words:
                w_clean = w.strip(",.!?\"'")
                if w_clean in INDIC_GLOSSARY:
                    norm_words.append(INDIC_GLOSSARY[w_clean])
                elif w_clean in ENTITY_KEYWORDS_MAP:
                    norm_words.append(ENTITY_KEYWORDS_MAP[w_clean])
                else:
                    norm_words.append(w_clean)
            translated_text = " ".join([w for w in norm_words if w])
            method_used = "glossary_fallback"

        return {
            "original_text": text_str,
            "normalized_english": translated_text or text_str,
            "detected_language": lang_code,
            "language_name": det["name"],
            "is_translated": lang_code != "en",
            "method": method_used,
            "detection_details": det
        }

    def process_query(self, query: str, target_lang: str = "auto") -> Dict[str, Any]:
        return self.translate_to_english(query, source_lang=target_lang)


multilingual_service = MultilingualService()
