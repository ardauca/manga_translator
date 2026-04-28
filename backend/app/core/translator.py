# app/core/translator.py - Çeviri Motoru

from deep_translator import GoogleTranslator
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class Translator:
    """GoogleTranslator kullanarak çeviri (deep-translator)"""
    
    def __init__(self):
        logger.info("Translator başlatıldı (deep-translator)")
    
    def translate(self, text: str, source_lang: str = 'auto', target_lang: str = 'tr') -> str:
        """
        Metni çevir
        
        Args:
            text: Çevrilecek metin
            source_lang: Kaynak dil (auto, ja, en, etc.)
            target_lang: Hedef dil (tr)
        
        Returns:
            Çevrilmiş metin
        """
        try:
            if not text or not text.strip():
                return ""
            
            # Dil kodları normalize et
            if source_lang == 'auto':
                src = 'auto'
            elif source_lang == 'ja':
                src = 'ja'
            elif source_lang == 'en':
                src = 'en'
            else:
                src = 'auto'
            
            # Çeviri yap
            translator = GoogleTranslator(source_lang=src, target_lang=target_lang)
            result = translator.translate(text)
            
            return result if result else text
        
        except Exception as e:
            logger.error(f"Çeviri hatası: {e}")
            return text
    
    def detect_language(self, text: str) -> str:
        """
        Metin dilini tespit et
        """
        try:
            from deep_translator import detect
            result = detect(text)
            return result if result else 'unknown'
        except Exception as e:
            logger.error(f"Dil tespit hatası: {e}")
            return 'unknown'
