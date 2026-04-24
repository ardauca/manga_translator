# app/core/translator.py - Çeviri Motoru

from googletrans import Translator as GoogleTranslator
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class Translator:
    """GoogleTrans kullanarak çeviri"""
    
    def __init__(self):
        self.translator = GoogleTranslator()
        logger.info("Translator initialized with googletrans")
    
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
            result = self.translator.translate(text, src_language=src, dest_language=target_lang)
            
            return result.text if result else text
        
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def detect_language(self, text: str) -> str:
        """
        Metin dilini tespit et
        """
        try:
            result = self.translator.detect(text)
            return result.lang if result else 'unknown'
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return 'unknown'
