# Architecture

## Model

Manga Translator uses a local companion backend model.

```text
Chrome popup
  -> backend health, settings, selection controls
Content script
  -> user selects a speech bubble
Background service worker
  -> checks backend, captures visible tab, sends request
FastAPI backend
  -> crop, preprocess, OCR, clean text, translate, cache
Content script
  -> renders overlay with close / retry / copy controls
```

## Extension

- `popup/`: backend status, settings and action controls
- `content/content.js`: selection box, page notices and translation overlays
- `background/background.js`: backend discovery, health checks, screenshot capture and API calls
- `manifest.json`: Chrome Manifest V3 definition

The extension must be loaded from `extension/`, not from the project root.

## Backend

- `main.py`: FastAPI app and CORS
- `api/routes.py`: request validation, screenshot decode, crop, cache, OCR and translation orchestration
- `core/image_processor.py`: OpenCV preprocessing modes
- `core/ocr_engine.py`: PaddleOCR model loading and result parsing
- `core/text_cleaner.py`: OCR text cleanup before translation
- `core/translator.py`: `deep-translator` wrapper
- `core/cache_manager.py`: in-memory TTL cache
- `core/settings_manager.py`: environment-backed settings

## Request Flow

1. Popup checks `/health` and `/api/status`.
2. Content script sends selected viewport coordinates to the background worker.
3. Background worker checks backend availability.
4. Background worker captures the visible tab.
5. Backend scales coordinates by device pixel ratio and clamps the crop to image bounds.
6. Backend checks cache using image, coordinates, languages and preprocessing mode.
7. If no cache hit, backend preprocesses, OCRs, cleans and translates the text.
8. Content script creates an overlay with translation, confidence, timing and controls.

## Tradeoffs

- Local backend keeps image processing local and avoids server cost.
- Local backend requires an extra running process.
- Free translation is convenient but not guaranteed at scale.
- Browser-only OCR is currently avoided because model size and performance are poor for this use case.
