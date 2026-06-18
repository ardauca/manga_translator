# app/core/settings_manager.py - Backend settings

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Manga Translator"
    DEBUG: bool = False

    OCR_ENGINE: str = "paddleocr"
    TRANSLATOR_ENGINE: str = "deep-translator"
    DEFAULT_TARGET_LANG: str = "tr"

    CACHE_MAX_SIZE: int = 1000
    CACHE_TTL_HOURS: int = 24

    UPSCALE_FACTOR: int = 2
    ENABLE_DENOISE: bool = True
    ENABLE_SHARPEN: bool = False

    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
