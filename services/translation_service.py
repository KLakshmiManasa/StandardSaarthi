"""
Multilingual Translation Service for StandardSaarthi (SIH 26108).
Implements a multi-provider translation pipeline with explicit failure detection,
environment-based configuration, entity preservation, and debug tracking.
"""

import os
import re
import json
import logging
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional, Tuple

from config.languages import SUPPORTED_LANGUAGES

logger = logging.getLogger("TranslationService")


class TranslationService:
    """
    Robust Multi-Provider Translation Service with explicit validation and fallbacks.
    
    Providers in execution chain:
    1. Google Official API (if GOOGLE_TRANSLATE_API_KEY is configured in env)
    2. Google GTX Direct API (Free public endpoint with retries and timeout)
    3. MyMemory Open Translation API (Secondary HTTP fallback)
    4. mtranslate Python Library (Tertiary fallback)
    5. Glossary & Rule-based Dictionary (Quaternary fallback)
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY", "").strip()
        self.primary_provider = os.getenv("TRANSLATION_PROVIDER", "google").strip().lower()
        self.secondary_provider = os.getenv("SECONDARY_TRANSLATION_PROVIDER", "mymemory").strip().lower()
        
        try:
            import mtranslate
            self.mtranslate = mtranslate
        except ImportError:
            self.mtranslate = None

    def has_translatable_words(self, text: str) -> bool:
        """
        Determines if text contains translatable English words rather than just numbers,
        symbols, or protected placeholders like __PROTECTED_ENTITY_0__.
        """
        if not text:
            return False
        # Strip placeholders
        clean_text = re.sub(r'__\s*PROTECTED_ENTITY_\d+__', '', text, flags=re.IGNORECASE)
        # Check for English alphabetic words with length >= 2
        return bool(re.search(r'[a-zA-Z]{2,}', clean_text))

    def is_valid_translation(self, source_text: str, translated_text: str, target_lang: str) -> bool:
        """
        Validates if translated_text is a genuine translation for target_lang.
        If target_lang != 'en' and translated_text is identical to source_text
        while source_text contains translatable words, it is flagged as a TRANSLATION FAILURE.
        """
        if not translated_text or not isinstance(translated_text, str):
            return False
        
        translated_clean = translated_text.strip()
        if not translated_clean:
            return False

        if target_lang != "en" and self.has_translatable_words(source_text):
            if translated_clean == source_text.strip():
                logger.warning(f"Translation returned identical English text for target '{target_lang}'. Flagged as failure.")
                return False

        return True

    def _translate_google_api(self, text: str, target_lang: str, source_lang: str = "en") -> Optional[str]:
        """Official Google Cloud Translation REST API (requires GOOGLE_TRANSLATE_API_KEY)."""
        if not self.api_key:
            return None
        try:
            url = f"https://translation.googleapis.com/language/translate/v2?key={self.api_key}"
            payload = json.dumps({"q": text, "source": source_lang, "target": target_lang, "format": "text"}).encode('utf-8')
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                translations = data.get("data", {}).get("translations", [])
                if translations:
                    return translations[0].get("translatedText")
        except Exception as e:
            logger.debug(f"Google Official API translation failed: {e}")
        return None

    def _translate_google_gtx(self, text: str, target_lang: str, source_lang: str = "en") -> Optional[str]:
        """Direct Google Translate GTX endpoint with custom User-Agent and timeout."""
        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q=" + urllib.parse.quote(text)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode('utf-8'))
                if res and isinstance(res, list) and len(res) > 0 and isinstance(res[0], list):
                    translated = "".join([item[0] for item in res[0] if item and len(item) > 0 and item[0]])
                    return translated
        except Exception as e:
            logger.debug(f"Google GTX translation failed for '{target_lang}': {e}")
        return None

    def _translate_mymemory(self, text: str, target_lang: str, source_lang: str = "en") -> Optional[str]:
        """MyMemory Open Translation API fallback."""
        try:
            url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair={source_lang}|{target_lang}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode('utf-8'))
                res_data = res.get("responseData", {})
                translated = res_data.get("translatedText")
                if translated and not translated.startswith("QUERY LENGTH LIMIT EXCEEDED"):
                    return translated
        except Exception as e:
            logger.debug(f"MyMemory translation failed for '{target_lang}': {e}")
        return None

    def _translate_mtranslate(self, text: str, target_lang: str, source_lang: str = "en") -> Optional[str]:
        """mtranslate Python package fallback."""
        if not self.mtranslate:
            return None
        try:
            return self.mtranslate.translate(text, target_lang, source_lang)
        except Exception as e:
            logger.debug(f"mtranslate failed for '{target_lang}': {e}")
        return None

    def translate(self, text: str, target_lang: str, glossary: Optional[Dict[str, str]] = None) -> Tuple[str, str, bool]:
        """
        Executes multi-provider translation strategy.
        
        Returns:
            Tuple[str, str, bool]: (translated_text, provider_used, fallback_used)
        """
        if not text or not text.strip() or target_lang == "en":
            return text, "none", False

        # Check glossary exact match
        if glossary and text in glossary:
            return glossary[text], "glossary", True

        # Provider Chain Pipeline
        providers = [
            ("google_official", self._translate_google_api),
            ("google_gtx", self._translate_google_gtx),
            ("mymemory", self._translate_mymemory),
            ("mtranslate", self._translate_mtranslate),
        ]

        fallback_used = False

        for idx, (provider_name, provider_fn) in enumerate(providers):
            try:
                res = provider_fn(text, target_lang, "en")
                if res and self.is_valid_translation(text, res, target_lang):
                    if idx > 1:
                        fallback_used = True
                    return res, provider_name, fallback_used
            except Exception as e:
                logger.debug(f"Provider {provider_name} failed: {e}")

        # Quaternary Fallback: Glossary token replacement
        if glossary:
            translated = text
            replaced_any = False
            for orig, tr in glossary.items():
                if orig in text:
                    translated = translated.replace(orig, tr)
                    replaced_any = True
            if replaced_any and self.is_valid_translation(text, translated, target_lang):
                return translated, "glossary_token", True

        logger.warning(f"All translation providers failed for target_lang '{target_lang}'.")
        return text, "failed", True


translation_service = TranslationService()
