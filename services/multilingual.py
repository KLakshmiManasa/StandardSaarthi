"""
Multilingual Processing Service for SIH 26108 / Product Engine.
Uses `config.languages.SUPPORTED_LANGUAGES` as centralized single source of truth for language maps.
Implements Indian language detection and query translation normalization with fallback dictionary for Indic procurement terms.
"""

import logging
import urllib.request
import urllib.parse
import json
from typing import Dict, Any, List, Optional, Tuple

from config.languages import SUPPORTED_LANGUAGES

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
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)",
    "or": "Odia (ଓଡ଼ିଆ)"
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
    "निर्माण": "construction",
    "स्टील": "steel",
    "इस्पात": "steel",
    "उत्पादों": "products",
    "उत्पाद": "product",
    "उपयोग": "use",
    "संरचना": "structure",
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
    "அடைக்கப்பட்ட": "packaged",
    "குடிநீர்": "drinking water",
    "தண்ணீர்": "water",
    "பாட்டில்": "bottle",

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
    "बिल्डिंग": "building", "इमारतीच्या": "building", "कட்டிட": "building", "భవనం": "building",
    "स्टील": "steel", "इस्पात": "steel", "steel": "steel", "निर्माण": "construction", "कन्स्ट्रक्शन": "construction",
    "அடைக்கப்பட்ட குடிநீர்": "packaged drinking water", "குடிநீர்": "drinking water", "தண்ணீர்": "water",
    "பேக்கேஜ்": "packaged", "पेयजल": "drinking water", "पैकेज्ड": "packaged"
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
        self._translation_cache: Dict[Tuple[str, str, str], str] = {}

    def translate_text(self, text: str, sl: str = "auto", tl: str = "en", timeout_sec: float = 3.5) -> str:
        """
        Translates text between languages with caching and multi-tier fallback.
        Works across all Indic languages (Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, etc.).
        """
        text_str = str(text or "").strip()
        if not text_str or sl == tl:
            return text_str

        cache_key = (text_str, sl, tl)
        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]

        # 1. Primary: Direct Google Translate endpoint with browser User-Agent and strict timeout
        try:
            q = urllib.parse.quote(text_str)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q={q}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and data[0]:
                    translated = "".join([segment[0] for segment in data[0] if segment and segment[0]])
                    if translated and translated.strip():
                        res_clean = translated.strip()
                        self._translation_cache[cache_key] = res_clean
                        return res_clean
        except Exception as e:
            logger.debug(f"Direct Google translate endpoint failed for '{text_str[:30]}': {e}")

        # 2. Fallback: Indic glossary for Indic -> English
        if tl == "en":
            norm_words = []
            for token in text_str.split():
                clean_tok = token.strip("।,;:!?'\"()")
                if clean_tok in INDIC_GLOSSARY:
                    norm_words.append(INDIC_GLOSSARY[clean_tok])
                elif clean_tok.isascii():
                    norm_words.append(clean_tok)
            if norm_words:
                res_clean = " ".join(norm_words)
                self._translation_cache[cache_key] = res_clean
                return res_clean

        return text_str

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

        return {"code": "en", "name": "English", "method": "default_fallback", "confidence": 0.50}

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

        # Extract entities to ensure they are preserved
        indic_words = text.split()
        extracted_entities = []
        for word in indic_words:
            clean_word = word.strip("।,;:!?'\"()")
            for k, val in ENTITY_KEYWORDS_MAP.items():
                if k.lower() in clean_word.lower():
                    extracted_entities.append(val)

        # Primary translation using translate_text
        translated = self.translate_text(text, sl=det_code if det_code != "auto" else "auto", tl="en")

        # Verify that key technical entities present in Indic text are preserved
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

    def translate_to_english(self, text: str, source_lang: str = "auto") -> Dict[str, Any]:
        return self.process_query(text, target_lang=source_lang)

    def localize_results(self, res: Dict[str, Any], target_lang: str = "en") -> Dict[str, Any]:
        """
        Translates recommendation titles, scopes, reasons, and status messages
        into the user's input/selected language when non-English.
        """
        if not target_lang or target_lang in ["en", "auto"]:
            return res

        try:
            # 1. Localize top-level message if present (e.g. Confidence-gating / Abstain explanation)
            if res.get("message"):
                res["message_localized"] = self.translate_text(res["message"], sl="en", tl=target_lang, timeout_sec=3.5)

            if res.get("clarification_prompt"):
                res["clarification_prompt_localized"] = self.translate_text(res["clarification_prompt"], sl="en", tl=target_lang, timeout_sec=3.5)

            # 2. Localize extracted entities (product, category, application, etc.)
            entities = res.get("entities")
            if entities and isinstance(entities, dict):
                entities_loc = {}
                for k, val in entities.items():
                    if isinstance(val, str) and val.strip():
                        entities_loc[k] = self.translate_text(val, sl="en", tl=target_lang, timeout_sec=3.5)
                    elif isinstance(val, list):
                        entities_loc[k] = [self.translate_text(str(item), sl="en", tl=target_lang, timeout_sec=3.5) for item in val]
                    else:
                        entities_loc[k] = val
                res["entities_localized"] = entities_loc

            # 3. Batch localize recommendations
            recs = res.get("recommendations", [])
            if recs:
                # Batch translate titles in one single request
                titles = [r.get("title", "") for r in recs]
                combined_titles = " \n ".join(titles)
                trans_titles_raw = self.translate_text(combined_titles, sl="en", tl=target_lang, timeout_sec=3.5)
                trans_titles = [line.strip() for line in trans_titles_raw.split("\n")]
                for idx, r in enumerate(recs):
                    if idx < len(trans_titles) and trans_titles[idx]:
                        r["title_localized"] = trans_titles[idx]
                    else:
                        r["title_localized"] = r.get("title", "")

                # Translate scope for top candidates (concise first sentence or up to 200 chars for speed & reliability)
                for r in recs[:3]:
                    scope_text = str(r.get("scope") or "").strip()
                    if scope_text and scope_text != "Not available in verified database":
                        first_sentence = scope_text.split(".")[0].strip() if "." in scope_text else scope_text[:200]
                        r["scope_localized"] = self.translate_text(first_sentence, sl="en", tl=target_lang, timeout_sec=3.5)

                # Localize reasons for top 2 candidates
                for r in recs[:2]:
                    reasons = r.get("ranking_reasons") or r.get("reasons") or []
                    if reasons:
                        combined_r = " \n ".join(reasons[:2])
                        trans_r_raw = self.translate_text(combined_r, sl="en", tl=target_lang, timeout_sec=3.5)
                        r["ranking_reasons_localized"] = [line.strip() for line in trans_r_raw.split("\n")]
        except Exception as e:
            logger.warning(f"Error during result localization: {e}")

        return res

multilingual_service = MultilingualService()
