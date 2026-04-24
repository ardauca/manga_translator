# app/main.py - FastAPI Application Entry Point

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

# Add app to path
APP_DIR = Path(__file__).parent
sys.path.insert(0, str(APP_DIR))

from api.routes import router as api_router
from core.settings_manager import settings

app = FastAPI(
    title="Manga Translator Backend",
    description="Lokal manga çevirisi sistemi",
    version="0.5.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    """Server sağlık kontrolü"""
    return {
        "status": "ok",
        "version": "0.5.0"
    }

if __name__ == "__main__":
    run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
