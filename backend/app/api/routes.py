# app/api/routes.py - API endpoints

import base64
import io
import logging
import traceback

from fastapi import APIRouter, HTTPException
from PIL import Image
from pydantic import BaseModel

from core.cache_manager import CacheManager
from core.image_processor import ImageProcessor
from core.ocr_engine import OCREngine
from core.translator import Translator

logger = logging.getLogger(__name__)

router = APIRouter()


class Coordinates(BaseModel):
    x: int
    y: int
    width: int
    height: int


class ProcessRequest(BaseModel):
    screenshot_data: str
    coordinates: Coordinates
    source_lang: str = "auto"
    target_lang: str = "tr"
    zoom_level: float = 1.0

    class Config:
        extra = "ignore"


class ProcessResponse(BaseModel):
    success: bool
    translation: str
    original_text: str
    confidence: float


ocr_engine = OCREngine()
translator = Translator()
image_processor = ImageProcessor()
cache_manager = CacheManager()


def _decode_screenshot(screenshot_data: str) -> Image.Image:
    if screenshot_data.startswith("data:image"):
        screenshot_data = screenshot_data.split(",", 1)[1]

    try:
        screenshot_bytes = base64.b64decode(screenshot_data, validate=True)
        image = Image.open(io.BytesIO(screenshot_bytes))
        image.load()
        return image.convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid screenshot data: {exc}") from exc


def _adjust_coordinates(coords: Coordinates, zoom_level: float, image: Image.Image) -> dict:
    zoom = zoom_level if zoom_level and zoom_level > 0 else 1.0
    adjusted = {
        "x": int(coords.x * zoom),
        "y": int(coords.y * zoom),
        "width": int(coords.width * zoom),
        "height": int(coords.height * zoom),
    }

    if adjusted["width"] <= 0 or adjusted["height"] <= 0:
        raise HTTPException(status_code=400, detail="Selection size must be greater than zero")

    left = max(0, adjusted["x"])
    top = max(0, adjusted["y"])
    right = min(image.width, adjusted["x"] + adjusted["width"])
    bottom = min(image.height, adjusted["y"] + adjusted["height"])

    if right <= left or bottom <= top:
        raise HTTPException(status_code=400, detail="Selection is outside the screenshot bounds")

    return {
        "x": left,
        "y": top,
        "width": right - left,
        "height": bottom - top,
    }


def _crop_image(image: Image.Image, coords: dict) -> Image.Image:
    return image.crop((
        coords["x"],
        coords["y"],
        coords["x"] + coords["width"],
        coords["y"] + coords["height"],
    ))


@router.post("/process", response_model=ProcessResponse)
async def process_manga(request: ProcessRequest):
    try:
        screenshot_image = _decode_screenshot(request.screenshot_data)
        adjusted_coords = _adjust_coordinates(request.coordinates, request.zoom_level, screenshot_image)
        cropped_image = _crop_image(screenshot_image, adjusted_coords)

        cache_key = cache_manager.generate_key(cropped_image, adjusted_coords, {
            "source_lang": request.source_lang,
            "target_lang": request.target_lang,
        })
        cached = cache_manager.get(cache_key) if cache_key else None
        if cached:
            logger.info("Cache hit for manga selection")
            return ProcessResponse(
                success=True,
                translation=cached["translation"],
                original_text=cached.get("original_text", "[cached]"),
                confidence=float(cached.get("confidence", 1.0)),
            )

        processed_image = image_processor.preprocess(cropped_image)
        ocr_result = ocr_engine.extract_with_confidence(processed_image, request.source_lang)
        original_text = ocr_result.get("text", "")
        confidence = float(ocr_result.get("confidence") or 0.0)

        if not original_text.strip():
            return ProcessResponse(
                success=True,
                translation="(Metin bulunamadi)",
                original_text="",
                confidence=0.0,
            )

        translated_text = translator.translate(original_text, request.source_lang, request.target_lang)

        if cache_key:
            cache_manager.set(cache_key, {
                "translation": translated_text,
                "original_text": original_text,
                "confidence": confidence,
            })

        return ProcessResponse(
            success=True,
            translation=translated_text,
            original_text=original_text,
            confidence=confidence,
        )

    except HTTPException:
        raise
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error("Process error: %s\n%s", exc, tb)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/process-with-cache", response_model=ProcessResponse)
async def process_with_cache(request: ProcessRequest):
    """Backward-compatible alias for clients that used the old cache endpoint."""
    return await process_manga(request)


@router.get("/cache/stats")
async def cache_stats():
    return cache_manager.get_stats()


@router.delete("/cache")
async def clear_cache():
    cache_manager.clear()
    return {"success": True}
