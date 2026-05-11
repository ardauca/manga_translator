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
        # Lazy loading - modelleri ilk kullanımda yükle
        self.ocr_ja = None
        self.ocr_en = None
        self.ja_loaded = False
        self.en_loaded = False
        print("[OCREngine] ✅ OCREngine başlatıldı (Lazy loading modu)")
        logger.info("OCREngine başlatıldı - modeller ilk kullanımda yüklenecek")
    
    def _load_ja_model(self):
        """Japonca modeli yükle (ilk kullanımda)"""
        if self.ja_loaded:
            return
        
        try:
            print("[OCREngine] PaddleOCR başlatılıyor (Japonca modeli)...")
            self.ocr_ja = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang='japan',
                device='cpu',
                enable_mkldnn=False
            )
            self.ja_loaded = True
            print("[OCREngine] ✅ Japonca modeli başarıyla yüklendi")
            logger.info("Japonca OCR modeli yüklendi")
        except Exception as e:
            error_msg = f"Japonca OCR modeli başlatma hatası: {repr(e)}"
            print(f"[OCREngine] ❌ {error_msg}")
            logger.error(error_msg)
            import traceback
            traceback.print_exc()
            self.ocr_ja = None
    
    def _load_en_model(self):
        """İngilizce modeli yükle (ilk kullanımda)"""
        if self.en_loaded:
            return
        
        try:
            print("[OCREngine] PaddleOCR başlatılıyor (İngilizce modeli)...")
            self.ocr_en = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang='en',
                device='cpu',
                enable_mkldnn=False
            )
            self.en_loaded = True
            print("[OCREngine] ✅ İngilizce modeli başarıyla yüklendi")
            logger.info("İngilizce OCR modeli yüklendi")
        except Exception as e:
            error_msg = f"İngilizce OCR modeli başlatma hatası: {repr(e)}"
            print(f"[OCREngine] ❌ {error_msg}")
            logger.error(error_msg)
            import traceback
            traceback.print_exc()
            self.ocr_en = None
    
    def extract_text(self, image: Image.Image, source_lang: str = 'auto') -> str:
        """
        Görüntüden metin çıkar
        
        Args:
            image: PIL Image object
            source_lang: 'ja' (Japonca), 'en' (İngilizce), 'auto' (default: Japonca)
        
        Returns:
            Çıkarılan metin
        """
        try:
            # Model yükle (lazy loading)
            if source_lang == 'en':
                self._load_en_model()
                ocr = self.ocr_en
            else:
                self._load_ja_model()
                ocr = self.ocr_ja
            
            if ocr is None:
                print(f"[OCR ERROR] OCR modeli yüklenemedil")
                return ""
            
            img_array = np.array(image.convert('RGB'))
            print(f"[OCR] Image array shape: {img_array.shape}")
            
            results = ocr.predict(img_array)
            print(f"[OCR] Predict sonucu type: {type(results)}, len: {len(results) if hasattr(results, '__len__') else 'N/A'}")
            
            text_lines = []
            for i, res in enumerate(results):
                # Result object'i yazdır - ne geldiğini görmek için
                print(f"[OCR DEBUG] Result[{i}] type: {type(res)}")
                print(f"[OCR DEBUG] Result[{i}] json: {res.json}")
                
                data = res.json
                # Pipeline sonucu: 'rec_texts' veya 'rec_text' olabilir
                rec_texts = (data.get('rec_texts') or 
                            data.get('rec_text') or 
                            data.get('res', {}).get('rec_texts') or
                            data.get('res', {}).get('rec_text') or [])
                rec_scores = (data.get('rec_scores') or
                             data.get('rec_score') or
                             data.get('res', {}).get('rec_scores') or
                             data.get('res', {}).get('rec_score') or [])
                
                print(f"[OCR DEBUG] rec_texts: {rec_texts}, rec_scores: {rec_scores}")
                
                if isinstance(rec_texts, str):
                    rec_texts = [rec_texts]
                    rec_scores = [rec_scores] if rec_scores else [1.0]
                
                for text, score in zip(rec_texts, rec_scores):
                    score_val = float(score) if score else 0
                    print(f"[OCR DEBUG] text='{text}', score={score_val}")
                    if score_val > 0.3 and str(text).strip():
                        text_lines.append(str(text).strip())
            
            result = ' '.join(text_lines).strip()
            print(f"[OCR FINAL] Extracted text: '{result}'")
            return result
        
        except Exception as e:
            import traceback
            print(f"[OCR ERROR] {repr(e)}")
            print(f"[OCR ERROR] Traceback:")
            traceback.print_exc()
            return ""
    
    def extract_with_confidence(self, image: Image.Image, source_lang: str = 'auto') -> dict:
        """
        Metin ve confidence bilgisi ile çıkart
        
        Args:
            image: PIL Image object
            source_lang: 'ja' (Japonca), 'en' (İngilizce), 'auto' (default: Japonca)
        
        Returns:
            {
                'text': str,
                'confidence': float,
                'raw_results': list
            }
        """
        try:
            # Model yükle (lazy loading)
            if source_lang == 'en':
                self._load_en_model()
                ocr = self.ocr_en
            else:
                self._load_ja_model()
                ocr = self.ocr_ja
            
            if ocr is None:
                print(f"[OCR ERROR] OCR modeli yüklenemedil")
                return {
                    'text': '',
                    'confidence': 0,
                    'raw_results': None
                }
            
            img_array = np.array(image.convert('RGB'))
            results = ocr.predict(img_array)
            
            texts = []
            confidences = []
            
            for i, res in enumerate(results):
                print(f"[OCR DEBUG] Result[{i}] type: {type(res)}")
                print(f"[OCR DEBUG] Result[{i}] json: {res.json}")
                
                data = res.json
                rec_texts = (data.get('rec_texts') or 
                            data.get('rec_text') or 
                            data.get('res', {}).get('rec_texts') or
                            data.get('res', {}).get('rec_text') or [])
                rec_scores = (data.get('rec_scores') or
                             data.get('rec_score') or
                             data.get('res', {}).get('rec_scores') or
                             data.get('res', {}).get('rec_score') or [])
                
                print(f"[OCR DEBUG] rec_texts: {rec_texts}, rec_scores: {rec_scores}")
                
                if isinstance(rec_texts, str):
                    rec_texts = [rec_texts]
                    rec_scores = [rec_scores] if rec_scores else [1.0]
                
                for text, score in zip(rec_texts, rec_scores):
                    score_val = float(score) if score else 0
                    if score_val > 0.3 and str(text).strip():
                        texts.append(str(text).strip())
                        confidences.append(score_val)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            result_text = ' '.join(texts).strip()
            print(f"[OCR CONFIDENCE] text='{result_text}', avg_conf={avg_confidence:.2f}")
            
            return {
                'text': result_text,
                'confidence': avg_confidence,
                'raw_results': results
            }
        
        except Exception as e:
            import traceback
            print(f"[OCR ERROR] {repr(e)}")
            print(f"[OCR ERROR] Traceback:")
            traceback.print_exc()
            return {
                'text': '',
                'confidence': 0,
                'raw_results': None
            }
