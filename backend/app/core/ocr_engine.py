# app/core/ocr_engine.py - PaddleOCR Motor

from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
from typing import Optional
import logging
import os

# Disable MKLDNN issues via environment
os.environ['FLAGS_use_mkldnn'] = '0'

logger = logging.getLogger(__name__)

class OCREngine:
    """PaddleOCR kullanarak metin okuma"""
    
    def __init__(self):
        # PaddleOCR multi-dil desteği ile başlat (Resmi v3.x API)
        # JP: Japonca, EN: İngilizce
        try:
            print("[OCREngine] PaddleOCR başlatılıyor...")
            self.ocr = PaddleOCR(
                use_doc_orientation_classify=False,  # Disable document orientation
                use_doc_unwarping=False,              # Disable document unwarping
                use_textline_orientation=False,       # Disable textline orientation
                lang='japan',                         # Japonca
                device='cpu'                          # CPU mode
            )
            print("[OCREngine] ✅ PaddleOCR başarıyla yüklendi")
            logger.info("OCREngine PaddleOCR ile başlatıldı")
        except Exception as e:
            error_msg = f"OCREngine başlatma hatası: {repr(e)}"
            print(f"[OCREngine] ❌ {error_msg}")
            logger.error(error_msg)
            import traceback
            traceback.print_exc()
            self.ocr = None
            # ← self.ocr = None tutuyorum ama extract_text'te guard var
    
    def extract_text(self, image: Image.Image, source_lang: str = 'auto') -> str:
        """
        Görüntüden metin çıkar
        
        Args:
            image: PIL Image object
            source_lang: 'ja' (Japonca), 'en' (İngilizce), 'auto'
        
        Returns:
            Çıkarılan metin
        """
        try:
            if self.ocr is None:
                logger.error("OCR engine başlatılmadı")
                return ""
            
            # PIL Image'ı numpy array'e çevir
            img_array = np.array(image.convert('RGB'))
            
            # PaddleOCR v3.x: predict() kullan (eski ocr() deprecated)
            results = self.ocr.predict(img_array)
            
            text_lines = []
            for res in results:
                # PaddleOCR 3.x: Result object with .json attribute
                try:
                    data = res.json
                    logger.debug(f"[OCR JSON] {data}")
                    rec_texts = data.get('res', {}).get('rec_text', [])
                    rec_scores = data.get('res', {}).get('rec_score', [])
                    if isinstance(rec_texts, str):
                        rec_texts = [rec_texts]
                        rec_scores = [rec_scores]
                    for text, score in zip(rec_texts, rec_scores):
                        logger.debug(f"[OCR] '{text}' score={score}")
                        if score > 0.1 and str(text).strip():
                            text_lines.append(str(text))
                except Exception as e:
                    # Fallback: res olarak dict veya list gelebilir
                    logger.debug(f"[OCR FALLBACK] type={type(res)}, error={e}")
                    if isinstance(res, dict):
                        rec_texts = res.get('rec_text', [])
                        rec_scores = res.get('rec_score', [])
                        if isinstance(rec_texts, str):
                            rec_texts = [rec_texts]
                            rec_scores = [rec_scores]
                        for text, score in zip(rec_texts, rec_scores):
                            if score > 0.1 and str(text).strip():
                                text_lines.append(str(text))
                    elif isinstance(res, list):
                        for line in res:
                            if line and len(line) >= 2:
                                if isinstance(line[1], (list, tuple)):
                                    text, score = line[1][0], line[1][1]
                                else:
                                    text, score = line[1], 0.9
                                if score > 0.1 and str(text).strip():
                                    text_lines.append(str(text))
            
            extracted = ' '.join(text_lines).strip()
            logger.debug(f"[OCR FINAL] '{extracted}'")
            return extracted
        
        except Exception as e:
            logger.error(f"OCR çıkarma hatası: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return ""
    
    def extract_with_confidence(self, image: Image.Image, source_lang: str = 'auto') -> dict:
        """
        Metin ve confidence bilgisi ile çıkart
        
        Returns:
            {
                'text': str,
                'confidence': float,
                'raw_results': list
            }
        """
        try:
            if self.ocr is None:
                return {
                    'text': '',
                    'confidence': 0,
                    'raw_results': None
                }
            
            img_array = np.array(image.convert('RGB'))
            
            # PaddleOCR v3.x: predict() kullan
            results = self.ocr.predict(img_array)
            
            texts = []
            confidences = []
            
            for res in results:
                try:
                    data = res.json
                    rec_texts = data.get('res', {}).get('rec_text', [])
                    rec_scores = data.get('res', {}).get('rec_score', [])
                    if isinstance(rec_texts, str):
                        rec_texts = [rec_texts]
                        rec_scores = [rec_scores]
                    for text, score in zip(rec_texts, rec_scores):
                        texts.append(str(text))
                        confidences.append(float(score))
                except Exception as e:
                    logger.debug(f"[OCR CONF FALLBACK] {e}")
                    if isinstance(res, dict):
                        rec_texts = res.get('rec_text', [])
                        rec_scores = res.get('rec_score', [])
                        if isinstance(rec_texts, str):
                            rec_texts = [rec_texts]
                            rec_scores = [rec_scores]
                        for text, score in zip(rec_texts, rec_scores):
                            texts.append(str(text))
                            confidences.append(float(score))
                    elif isinstance(res, list):
                        for line in res:
                            if line and len(line) >= 2:
                                if isinstance(line[1], (list, tuple)):
                                    text, score = line[1][0], line[1][1]
                                else:
                                    text, score = line[1], 0.9
                                texts.append(str(text))
                                confidences.append(float(score))
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': ' '.join(texts).strip(),
                'confidence': avg_confidence,
                'raw_results': results
            }
        
        except Exception as e:
            logger.error(f"OCR confidence çıkarma hatası: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'text': '',
                'confidence': 0,
                'raw_results': None
            }
