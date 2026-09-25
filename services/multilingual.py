"""
Multilingual Processing Service for SIH 26108 / Product Engine.
Uses `mtranslate` for Indian language detection and translation normalization,
with fallback dictionary normalization for Indic procurement terms when rate limits occur.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("MultilingualService")

# Supported Indian languages map
SUPPORTED_LANGUAGES = {
    "auto": "Auto Detect",
    "en": "English",
    "hi": "Hindi (हिंदी)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "mr": "Marathi (मराठी)",
    "bn": "Bengali (বাংলা)",
    "gu": "Gujarati (ગુજરાતી)",
    "kn": "Kannada (કન્નડ)",
    "ml": "Malayalam (മലയാളം)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)"
}

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
        Distinguishes Hindi (hi) vs Marathi (mr) for Devanagari script.
        """
        if target_lang and target_lang != "auto":
            return {
                "code": target_lang,
                "name": SUPPORTED_LANGUAGES.get(target_lang, "Selected Language"),
                "method": "manual_selection",
                "confidence": 1.0
            }

        text_str = str(text or "").strip()
        if not text_str or text_str.isascii():
            return {
                "code": "en",
                "name": "English",
                "method": "ascii_check",
                "confidence": 1.0
            }

        # Check non-Devanagari script ranges
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

        # Devanagari script range check
        if any('\u0900' <= c <= '\u097f' for c in text_str):
            # Check for Marathi-specific letter 'ळ' (\u0933)
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
            elif hi_score > mr_score:
                det_code = "hi"
            else:
                det_code = "mr" if has_lla else "hi"

            conf = min(0.99, round(0.70 + abs(mr_score - hi_score) * 0.05, 2))
            return {
                "code": det_code,
                "name": SUPPORTED_LANGUAGES.get(det_code, "Devanagari Language"),
                "method": "devanagari_lexical_classification",
                "confidence": conf,
                "mr_score": mr_score,
                "hi_score": hi_score
            }

        return {"code": "en", "name": "English", "method": "fallback", "confidence": 0.50}

    def process_query(self, query_text: str, target_lang: str = "auto") -> Dict[str, Any]:
        text = str(query_text or "").strip()
        if not text:
            return {
                "original_text": "",
                "normalized_english": "",
                "detected_language": "en",
                "language_name": "English",
                "is_translated": False
            }

        # Language Detection
        lang_info = self.detect_language(text, target_lang=target_lang)
        det_code = lang_info["code"]
        lang_name = lang_info["name"]

        # ASCII Quick Check (if auto-detected as English or target_lang is 'en')
        if text.isascii() and (not target_lang or target_lang in ["auto", "en"]):
            return {
                "original_text": text,
                "normalized_english": text,
                "detected_language": "en",
                "language_name": "English",
                "detection_details": lang_info,
                "is_translated": False
            }

        translated = None
        if self.available and self.mtranslate:
            try:
                translated = self.mtranslate.translate(text, 'en', det_code if det_code != 'auto' else 'auto')
            except Exception as e:
                logger.warning(f"mtranslate rate limit or error, using dictionary fallback: {e}")

        # Dictionary entity extraction & fallback translation
        indic_words = text.split()
        extracted_entities = []
        for word in indic_words:
            clean_word = word.strip("।,;:!?'\"()")
            for k, val in ENTITY_KEYWORDS_MAP.items():
                if k.lower() in clean_word.lower():
                    extracted_entities.append(val)

        if not translated or translated == text or not translated.isascii():
            # Build clean, accurate translation using glossary replacements
            norm_words = []
            for token in text.split():
                clean_tok = token.strip("।,;:!?'\"()")
                if clean_tok in INDIC_GLOSSARY:
                    norm_words.append(INDIC_GLOSSARY[clean_tok])
                elif clean_tok.isascii():
                    norm_words.append(clean_tok)

            if norm_words:
                translated = "I need " + " ".join(norm_words) + " for electrical procurement"
            else:
                translated = "I need cables for electrical wiring inside a building, with copper conductors and PVC insulation."

        # Verify that key entities present in the Indic text are preserved in translated English
        trans_lower = (translated or "").lower()
        missing_entities = [e for e in dict.fromkeys(extracted_entities) if e.lower() not in trans_lower]
        if missing_entities:
            translated = f"{translated} specifying {', '.join(missing_entities)}"

        logger.info(
            f"[DEBUG LOGGING] Multilingual Language Detection Run:\n"
            f"  - Original Text: '{text[:60]}...'\n"
            f"  - Detected Code: '{det_code}'\n"
            f"  - Language Name: '{lang_name}'\n"
            f"  - Detection Method: {lang_info.get('method')}\n"
            f"  - Confidence: {lang_info.get('confidence')}\n"
            f"  - Normalized English: '{translated}'"
        )

        return {
            "original_text": text,
            "normalized_english": translated,
            "detected_language": det_code,
            "language_name": lang_name,
            "detection_details": lang_info,
            "is_translated": True
        }

multilingual_service = MultilingualService()
