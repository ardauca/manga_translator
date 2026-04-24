# app/core/translator.py - Çeviri Motoru

<<<<<<< HEAD
from deep_translator import GoogleTranslator
=======
from googletrans import Translator as GoogleTranslator
>>>>>>> origin/main
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class Translator:
<<<<<<< HEAD
    """GoogleTranslator kullanarak çeviri (deep-translator)"""
    
    def __init__(self):
        logger.info("Translator başlatıldı (deep-translator)")
=======
    """GoogleTrans kullanarak çeviri"""
    
    def __init__(self):
        self.translator = GoogleTranslator()
        logger.info("Translator initialized with googletrans")
>>>>>>> origin/main
    
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
<<<<<<< HEAD
            translator = GoogleTranslator(source_language=src, target_language=target_lang)
            result = translator.translate(text)
            
            return result if result else text
        
        except Exception as e:
            logger.error(f"Çeviri hatası: {e}")
=======
            result = self.translator.translate(text, src_language=src, dest_language=target_lang)
            
            return result.text if result else text
        
        except Exception as e:
            logger.error(f"Translation error: {e}")
>>>>>>> origin/main
            return text
    
    def detect_language(self, text: str) -> str:
        """
        Metin dilini tespit et
        """
        try:
<<<<<<< HEAD
            from deep_translator import detect
            result = detect(text)
            return result if result else 'unknown'
        except Exception as e:
            logger.error(f"Dil tespit hatası: {e}")
=======
            result = self.translator.detect(text)
            return result.lang if result else 'unknown'
        except Exception as e:
            logger.error(f"Language detection error: {e}")
>>>>>>> origin/main
            return 'unknown'
