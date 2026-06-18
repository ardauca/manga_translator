# app/core/translator.py - Translation engine

import logging
import time

from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)


class Translator:
    """Translate OCR text with deep-translator's Google backend."""

    def __init__(self):
        logger.info("Translator initialized")

    @staticmethod
    def _normalize_source_lang(source_lang: str) -> str:
        return source_lang if source_lang in {"auto", "ja", "en"} else "auto"

    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "tr") -> str:
        if not text or not text.strip():
            return ""

        src = self._normalize_source_lang(source_lang)
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            try:
                result = GoogleTranslator(source=src, target=target_lang).translate(text)
                if result:
                    return result
            except Exception as exc:
                logger.warning("Translation attempt %s/%s failed: %s", attempt, max_retries, exc)
                if attempt < max_retries:
                    time.sleep(1)

        logger.warning("Translation failed after retries; returning original text")
        return text

    def detect_language(self, text: str) -> str:
        try:
            from deep_translator import single_detection

            return single_detection(text, api_key=None) or "unknown"
        except Exception as exc:
            logger.warning("Language detection failed: %s", exc)
            return "unknown"
