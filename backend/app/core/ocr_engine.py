# app/core/ocr_engine.py - PaddleOCR wrapper

import logging
import os
from typing import Any

import numpy as np
from paddleocr import PaddleOCR
from PIL import Image

os.environ["FLAGS_use_mkldnn"] = "0"

logger = logging.getLogger(__name__)


class OCREngine:
    """Lazy-loading OCR engine for Japanese and English manga text."""

    def __init__(self):
        self.ocr_ja = None
        self.ocr_en = None
        logger.info("OCR engine initialized; models will load on first use")

    def _load_model(self, source_lang: str):
        if source_lang == "en":
            if self.ocr_en is None:
                logger.info("Loading English OCR model")
                self.ocr_en = self._create_model("en")
            return self.ocr_en

        if self.ocr_ja is None:
            logger.info("Loading Japanese OCR model")
            self.ocr_ja = self._create_model("japan")
        return self.ocr_ja

    @staticmethod
    def _create_model(lang: str):
        return PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            lang=lang,
            device="cpu",
            enable_mkldnn=False,
        )

    def extract_text(self, image: Image.Image, source_lang: str = "auto") -> str:
        return self.extract_with_confidence(image, source_lang)["text"]

    def extract_with_confidence(self, image: Image.Image, source_lang: str = "auto") -> dict:
        try:
            ocr = self._load_model(source_lang)
            img_array = np.array(image.convert("RGB"))
            results = ocr.predict(img_array)
            texts, confidences = self._parse_results(results)

            text = " ".join(texts).strip()
            confidence = sum(confidences) / len(confidences) if confidences else 0.0
            logger.info("OCR extracted %s characters with %.2f confidence", len(text), confidence)

            return {
                "text": text,
                "confidence": confidence,
                "raw_results": results,
            }
        except Exception:
            logger.exception("OCR failed")
            return {
                "text": "",
                "confidence": 0.0,
                "raw_results": None,
            }

    @staticmethod
    def _parse_results(results: list[Any]) -> tuple[list[str], list[float]]:
        texts: list[str] = []
        confidences: list[float] = []

        for result in results:
            data = getattr(result, "json", {}) or {}
            payload = data.get("res", data)
            rec_texts = payload.get("rec_texts") or payload.get("rec_text") or []
            rec_scores = payload.get("rec_scores") or payload.get("rec_score") or []

            if isinstance(rec_texts, str):
                rec_texts = [rec_texts]
            if isinstance(rec_scores, (int, float)):
                rec_scores = [rec_scores]
            if not rec_scores:
                rec_scores = [1.0] * len(rec_texts)

            for text, score in zip(rec_texts, rec_scores):
                score_value = float(score or 0.0)
                clean_text = str(text).strip()
                if clean_text and score_value >= 0.3:
                    texts.append(clean_text)
                    confidences.append(score_value)

        return texts, confidences
