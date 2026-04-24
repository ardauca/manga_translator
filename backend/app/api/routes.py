# app/api/routes.py - API Endpoint'leri

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
import base64
import io
from PIL import Image

from core.ocr_engine import OCREngine
from core.translator import Translator
from core.image_processor import ImageProcessor
from core.cache_manager import CacheManager

router = APIRouter()

# Models
class ProcessRequest(BaseModel):
    screenshot_data: str  # Base64
    coordinates: dict  # {x, y, width, height}
    source_lang: str = "auto"
    target_lang: str = "tr"

class ProcessResponse(BaseModel):
    success: bool
    translation: str
    original_text: str
    confidence: float

# Instances
ocr_engine = OCREngine()
translator = Translator()
image_processor = ImageProcessor()
cache_manager = CacheManager()

@router.post("/process", response_model=ProcessResponse)
async def process_manga(request: ProcessRequest):
    """
    Manga bubble'ını işle:
    1. Screenshot'tan crop al
    2. Preprocessing yap
    3. OCR oku
    4. Türkçeye çevir
    5. Sonuç dön
    """
    try:
        # Base64'ü decode et
        screenshot_bytes = base64.b64decode(request.screenshot_data)
        screenshot_image = Image.open(io.BytesIO(screenshot_bytes))

        # Coordinates'den crop al
        coords = request.coordinates
        crop_box = (coords['x'], coords['y'], 
                   coords['x'] + coords['width'], 
                   coords['y'] + coords['height'])
        
        cropped_image = screenshot_image.crop(crop_box)

        # Preprocessing
        processed_image = image_processor.preprocess(cropped_image)

        # OCR
        original_text = ocr_engine.extract_text(processed_image, request.source_lang)
        
        if not original_text.strip():
            raise HTTPException(status_code=400, detail="Metin bulunamadı")

        # Translation
        translated_text = translator.translate(original_text, request.source_lang, request.target_lang)

        # Cache'e kaydet
        cache_key = cache_manager.generate_key(cropped_image, coords, request)
        cache_manager.set(cache_key, translated_text)

        return ProcessResponse(
            success=True,
            translation=translated_text,
            original_text=original_text,
            confidence=0.95  # TODO: OCR confidence'dan al
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-with-cache", response_model=ProcessResponse)
async def process_with_cache(request: ProcessRequest):
    """
    Cache kontrol ile işleme
    """
    try:
        coords = request.coordinates
        
        # Screenshot'ı crop al
        screenshot_bytes = base64.b64decode(request.screenshot_data)
        screenshot_image = Image.open(io.BytesIO(screenshot_bytes))
        
        crop_box = (coords['x'], coords['y'], 
                   coords['x'] + coords['width'], 
                   coords['y'] + coords['height'])
        cropped_image = screenshot_image.crop(crop_box)

        # Cache kontrol
        cache_key = cache_manager.generate_key(cropped_image, coords, request)
        cached = cache_manager.get(cache_key)
        
        if cached:
            return ProcessResponse(
                success=True,
                translation=cached,
                original_text="[cached]",
                confidence=1.0
            )

        # Cache miss - normal işleme devam et
        return await process_manga(request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
