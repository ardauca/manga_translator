# app/core/settings_manager.py - Ayarlar

from pydantic_settings import BaseSettings
<<<<<<< HEAD
from pydantic import Field
from typing import Optional, List
=======
from typing import Optional
>>>>>>> origin/main

class Settings(BaseSettings):
    """Backend ayarları"""
    
    # Server
    APP_NAME: str = "Manga Translator"
    DEBUG: bool = False
    
    # OCR
    OCR_ENGINE: str = "paddleocr"
<<<<<<< HEAD
    
    # Translator
    TRANSLATOR_ENGINE: str = "deep-translator"
=======
    USE_GPU: bool = False
    
    # Translator
    TRANSLATOR_ENGINE: str = "googletrans"
>>>>>>> origin/main
    DEFAULT_TARGET_LANG: str = "tr"
    
    # Cache
    CACHE_MAX_SIZE: int = 1000
    CACHE_TTL_HOURS: int = 24
    
    # Preprocessing
    UPSCALE_FACTOR: int = 2
    ENABLE_DENOISE: bool = True
    ENABLE_SHARPEN: bool = False
    
    # CORS
<<<<<<< HEAD
    ALLOWED_ORIGINS: List[str] = ["*"]
=======
    ALLOWED_ORIGINS: list = ["*"]
>>>>>>> origin/main
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
