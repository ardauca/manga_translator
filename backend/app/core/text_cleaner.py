# app/core/text_cleaner.py - OCR text cleanup helpers

import re


class TextCleaner:
    """Normalize OCR output before translation."""

    @staticmethod
    def clean(text: str, source_lang: str = "auto") -> str:
        if not text:
            return ""

        cleaned = text.replace("\r", " ").replace("\n", " ")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        cleaned = TextCleaner._join_hyphenated_words(cleaned)
        cleaned = TextCleaner._normalize_punctuation_spacing(cleaned)

        if source_lang == "en":
            cleaned = TextCleaner._normalize_english(cleaned)

        return cleaned.strip()

    @staticmethod
    def _join_hyphenated_words(text: str) -> str:
        # OCR often reads manga line breaks as "PROMIS- ING"; join obvious fragments.
        return re.sub(r"\b([A-Za-z]{2,})-\s+([A-Za-z]{2,})\b", r"\1\2", text)

    @staticmethod
    def _normalize_punctuation_spacing(text: str) -> str:
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = re.sub(r"([({\[])\s+", r"\1", text)
        text = re.sub(r"\s+([)}\]])", r"\1", text)
        return text

    @staticmethod
    def _normalize_english(text: str) -> str:
        # Keep expressive manga punctuation but avoid all-caps shouting when OCR returns every word uppercase.
        words = re.findall(r"[A-Za-z]+", text)
        if words and sum(word.isupper() and len(word) > 1 for word in words) / len(words) > 0.75:
            return text.title().replace("'Re", "'re").replace("'Ll", "'ll").replace("'Ve", "'ve")
        return text
