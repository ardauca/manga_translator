# app/core/ocr_engine.py - PaddleOCR Motor

from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class OCREngine:
    """PaddleOCR kullanarak metin okuma"""
    
    def __init__(self):
        # PaddleOCR multi-dil desteği ile başlat
        # JP: Japonca, EN: İngilizce
<<<<<<< HEAD
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=True,  # Orientation detection
                lang='japan'  # Default Japonca
            )
            logger.info("OCREngine PaddleOCR ile başlatıldı")
        except Exception as e:
            logger.error(f"OCREngine başlatma hatası: {e}")
            self.ocr = None
=======
        self.ocr = PaddleOCR(
            use_angle_cls=True,  # Orientation detection
            use_gpu=False,  # CPU mode
            lang='japan'  # Default Japonca
        )
        logger.info("OCREngine initialized with PaddleOCR")
>>>>>>> origin/main
    
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
<<<<<<< HEAD
            if self.ocr is None:
                logger.error("OCR engine başlatılmadı")
                return ""
            
            # PIL Image'ı numpy array'e çevir
            img_array = np.array(image)
            
=======
            # PIL Image'ı numpy array'e çevir
            img_array = np.array(image)
            
            # Dil belirleme
            if source_lang == 'auto':
                lang = 'japan'  # Default olarak Japoncayı dene
            elif source_lang == 'en':
                lang = 'en'
            elif source_lang == 'ja':
                lang = 'japan'
            else:
                lang = 'japan'
            
>>>>>>> origin/main
            # OCR yap
            result = self.ocr.ocr(img_array, cls=True)
            
            # Sonuçları birleştir
            text_lines = []
            if result:
                for line in result:
                    if line:
                        for item in line:
                            text = item[1]
                            confidence = item[2]
                            if confidence > 0.1:  # Düşük confidence'ı filtrele
                                text_lines.append(text)
            
            return ' '.join(text_lines).strip()
        
        except Exception as e:
<<<<<<< HEAD
            logger.error(f"OCR çıkarma hatası: {e}")
=======
            logger.error(f"OCR extraction error: {e}")
>>>>>>> origin/main
            return ""
    
    def extract_with_confidence(self, image: Image.Image, source_lang: str = 'auto') -> dict:
        """
        Metin ve confidence bilgisi ile çıkart
        """
        try:
<<<<<<< HEAD
            if self.ocr is None:
                return {
                    'text': '',
                    'confidence': 0,
                    'raw_results': None
                }
            
=======
>>>>>>> origin/main
            img_array = np.array(image)
            result = self.ocr.ocr(img_array, cls=True)
            
            texts = []
            confidences = []
            
            if result:
                for line in result:
                    if line:
                        for item in line:
                            texts.append(item[1])
                            confidences.append(item[2])
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': ' '.join(texts).strip(),
                'confidence': avg_confidence,
                'raw_results': result
            }
        
        except Exception as e:
<<<<<<< HEAD
            logger.error(f"OCR çıkarma hatası: {e}")
=======
            logger.error(f"OCR extraction error: {e}")
>>>>>>> origin/main
            return {
                'text': '',
                'confidence': 0,
                'raw_results': None
            }
