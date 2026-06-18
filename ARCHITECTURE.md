# Architecture

## Overview

```text
Chrome content script
  -> user selects a bubble
Chrome background service worker
  -> captures the visible tab
FastAPI backend
  -> crops, preprocesses, OCRs, translates, caches
Chrome content script
  -> renders translated overlay on the page
```

## Chrome Extension

- `popup/` controls selection mode and user settings.
- `content/content.js` runs on manga pages, draws the selection box, and renders overlays.
- `background/background.js` captures screenshots and calls the backend.
- Settings are stored with `chrome.storage.sync`; transient selection state uses `chrome.storage.local`.

## Backend

- `main.py` creates the FastAPI app.
- `api/routes.py` owns request validation, screenshot decoding, crop bounds, cache use, OCR, and translation orchestration.
- `core/image_processor.py` contains OpenCV preprocessing.
- `core/ocr_engine.py` wraps PaddleOCR lazy loading.
- `core/translator.py` wraps `deep-translator`.
- `core/cache_manager.py` provides in-memory TTL cache.

## Data Flow

1. The content script sends viewport coordinates to the background worker.
2. The background worker captures the visible tab and sends the base64 PNG to `/api/process`.
3. The backend scales coordinates by `zoom_level`, clamps the crop to the screenshot bounds, and checks the cache.
4. If there is no cache hit, the backend preprocesses the crop, runs OCR, translates the result, and stores it in cache.
5. The extension receives the translation and places an absolute-positioned overlay on the page.

## Known Tradeoffs

- The backend is local and assumes `http://localhost:8000` by default.
- The cache is in memory and disappears when the backend restarts.
- PaddleOCR has a heavy first-run cost because models may need to download and initialize.
- Manual selection is simpler and more predictable than automatic bubble detection for this MVP.
