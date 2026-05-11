# app/api/routes.py - API Endpoint'leri

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
import base64
import io
import logging
import traceback
import numpy as np
import cv2
from PIL import Image

from core.ocr_engine import OCREngine
from core.translator import Translator
from core.image_processor import ImageProcessor
from core.cache_manager import CacheManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Models
class ProcessRequest(BaseModel):
    screenshot_data: str  # Base64
    coordinates: dict  # {x, y, width, height}
    source_lang: str = "auto"
    target_lang: str = "tr"
    
    class Config:
        extra = "allow"  # Extra fields'ı ignore et

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
    print("[ENDPOINT] /api/process REQUEST RECEIVED!!!")  # ← BUNU GÖRMEK İSTİYORUZ
    try:
        print(f"\n{'='*60}")
        print(f"[DEBUG] ===== PROCESS START =====")
        print(f"[DEBUG] Request received: {request}")
        print(f"[DEBUG] Coordinates: {request.coordinates}")
        print(f"[DEBUG] Source lang: {request.source_lang}")
        print(f"[DEBUG] Target lang: {request.target_lang}")
        print(f"{'='*60}\n")
        
        # Base64'ü decode et (prefix varsa sıyır)
        screenshot_data = request.screenshot_data
        if screenshot_data.startswith('data:image'):
            screenshot_data = screenshot_data.split(',')[1]
        
        print(f"[DEBUG] 1. Screenshot data length: {len(screenshot_data)} chars")
        
        try:
            screenshot_bytes = base64.b64decode(screenshot_data)
            print(f"[DEBUG] 2. Screenshot decoded: {len(screenshot_bytes)} bytes")
        except Exception as e:
            print(f"[ERROR] Base64 decode failed: {e}")
            raise ValueError(f"Base64 decode failed: {e}")
        
        screenshot_image = Image.open(io.BytesIO(screenshot_bytes))
        print(f"[DEBUG] 3. Screenshot opened: {screenshot_image.size} - {screenshot_image.mode}")

        # Coordinates'den crop al (zoom level ile normalize)
        coords = request.coordinates
        zoom_level = getattr(request, 'zoom_level', 1.0) or 1.0
        
        # CSS pixels'i screenshot pixels'e çevir
        # captureVisibleTab() zaten zoom seviyesini uygulıyor
        # ama content script CSS pixels gönderdiği için normalize etmeliyiz
        adjusted_coords = {
            'x': int(coords['x'] * zoom_level),
            'y': int(coords['y'] * zoom_level),
            'width': int(coords['width'] * zoom_level),
            'height': int(coords['height'] * zoom_level)
        }
        
        print(f"[DEBUG] 4. Original coords: {coords}")
        print(f"[DEBUG] 4. Zoom level: {zoom_level}")
        print(f"[DEBUG] 4. Adjusted coords: {adjusted_coords}")
        
        crop_box = (adjusted_coords['x'], adjusted_coords['y'], 
                   adjusted_coords['x'] + adjusted_coords['width'], 
                   adjusted_coords['y'] + adjusted_coords['height'])
        
        cropped_image = screenshot_image.crop(crop_box)
        print(f"[DEBUG] 5. Cropped image: {cropped_image.size}")

        # Preprocessing'i DİNAMİK OLARAK TEST ET
        # İlk olarak preprocessing KAPALIYKEN dene
        use_preprocessing = False
        if use_preprocessing:
            processed_image = image_processor.preprocess(cropped_image)
            print(f"[DEBUG] 6. Preprocessing done: {processed_image.size}")
            test_image = processed_image
        else:
            # Daha agresif upscale + CLAHE contrast
            scale = 4  # 4x upscale
            new_size = (cropped_image.width * scale, cropped_image.height * scale)
            upscaled = cropped_image.resize(new_size, Image.LANCZOS)
            
            # CLAHE ile contrast artır
            cv_img = cv2.cvtColor(np.array(upscaled), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            test_image = Image.fromarray(cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB))
            print(f"[DEBUG] 6. 4x upscale + CLAHE done: {test_image.size}")
            
            # DEBUG: Resmi kaydet
            debug_path = f"C:\\Users\\ARDA\\Desktop\\debug_bubble_{adjusted_coords['x']}_{adjusted_coords['y']}.png"
            test_image.save(debug_path)
            print(f"[DEBUG] Saved debug image: {debug_path}")

        # OCR
        original_text = ocr_engine.extract_text(test_image, request.source_lang)
        print(f"[DEBUG] 7. OCR text result: '{original_text[:100]}...' (total: {len(original_text)} chars)")
        
        if not original_text or not original_text.strip():
            print(f"[WARNING] No text extracted from OCR")
            return ProcessResponse(
                success=True,
                translation="(Metin bulunamadı)",
                original_text="",
                confidence=0.0
            )

        # Translation
        print(f"[DEBUG] 8. Translation start - source={request.source_lang}, target={request.target_lang}")
        translated_text = translator.translate(original_text, request.source_lang, request.target_lang)
        print(f"[DEBUG] 9. Translation result: '{translated_text[:100]}...' (total: {len(translated_text)} chars)")

        # Cache'e kaydet
        cache_key = cache_manager.generate_key(cropped_image, adjusted_coords, {
            'source_lang': request.source_lang,
            'target_lang': request.target_lang
        })
        if cache_key:
            cache_manager.set(cache_key, translated_text)
            print(f"[DEBUG] 10. Cached with key: {cache_key[:20]}...")
        else:
            print(f"[DEBUG] 10. Cache skipped (key generation failed)")

        print(f"[DEBUG] ===== PROCESS SUCCESS =====\n")
        
        return ProcessResponse(
            success=True,
            translation=translated_text,
            original_text=original_text,
            confidence=0.95
        )

    except Exception as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        print(f"\n[ERROR] ===== PROCESS FAILED =====")
        print(f"[ERROR] Error message: {error_msg}")
        print(f"[ERROR] Full traceback:\n{tb}")
        print(f"[ERROR] ===== END ERROR =====\n")
        logger.error(f"Process error: {error_msg}\n{tb}")
        raise HTTPException(status_code=500, detail=error_msg)

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
