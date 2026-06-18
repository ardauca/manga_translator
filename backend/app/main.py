# app/main.py - FastAPI application entry point

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

APP_DIR = Path(__file__).parent
sys.path.insert(0, str(APP_DIR))

from api.routes import router as api_router
from core.settings_manager import settings

app = FastAPI(
    title="Manga Translator Backend",
    description="Local OCR and translation backend for manga bubbles",
    version="0.5.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Server health check."""
    return {
        "status": "ok",
        "version": "0.5.0",
        "app": settings.APP_NAME,
    }


if __name__ == "__main__":
    run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
