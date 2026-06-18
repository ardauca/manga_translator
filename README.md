# Manga Translator

Local-first Chrome extension for translating selected manga speech bubbles into Turkish.

The project has two parts:

- Chrome extension: selection UI, screenshot capture, page overlays
- Python backend: crop, image preprocessing, PaddleOCR, translation and cache

## Features

- Manual speech bubble selection with mouse drag
- Chrome Manifest V3 extension
- Visible tab screenshot capture
- Backend-side crop and coordinate validation
- OpenCV preprocessing for OCR
- Local PaddleOCR for Japanese and English OCR
- `deep-translator` translation to Turkish
- In-memory cache for repeated selections
- Multiple page overlays
- Overlay close, retry and copy controls
- Optional OCR text under the translation
- Popup settings for source language, OCR mode, font size, opacity and backend URL
- Popup backend health/cache status
- Clear backend cache and clear page overlays controls

## Free / Local-First Model

The current project does not require a paid API key.

- OCR runs locally with PaddleOCR.
- The backend runs on the user's machine.
- There is no hosted server cost.
- Translation uses `deep-translator` with a free web-backed Google flow.

Important: the translation provider is free but not guaranteed for heavy or commercial-scale use. It may rate-limit or change behavior. A future version can add LibreTranslate or offline translation fallback.

## Limits

- The extension needs the local backend; it does not run OCR by itself.
- First OCR use can be slow because PaddleOCR downloads and initializes models.
- Cache is in memory and resets when the backend stops.
- Automatic bubble detection is not implemented yet.
- Load only the `extension/` folder in Chrome, not the project root.

## Project Structure

```text
manga_translator/
  backend/
    app/
      api/routes.py
      core/cache_manager.py
      core/image_processor.py
      core/ocr_engine.py
      core/settings_manager.py
      core/text_cleaner.py
      core/translator.py
      main.py
    requirements.txt
    tests/
  extension/
    background/background.js
    content/content.js
    content/style.css
    manifest.json
    popup/popup.html
    popup/popup.css
    popup/popup.js
  start_backend.ps1
  start_backend.bat
```

## Setup

Start the backend:

```powershell
.\start_backend.ps1
```

The script creates `.venv`, installs dependencies and starts the backend at `http://localhost:8000`.

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Load the Chrome extension:

1. Open `chrome://extensions/`.
2. Enable Developer mode.
3. Click Load unpacked.
4. Select only the `extension/` folder.
5. Refresh the manga page.

## Usage

1. Keep the backend terminal open.
2. Open the extension popup.
3. Check that Backend is Online.
4. Click Start Select.
5. Drag over a manga speech bubble.
6. Use overlay buttons:
   - `x`: close
   - `r`: retry OCR/translation
   - `c`: copy translation

## OCR Modes

- `auto`: default balanced preprocessing
- `light`: grayscale only
- `strong`: aggressive adaptive threshold
- `invert`: inverted grayscale for unusual panels
- `raw`: no preprocessing

## Tests

Run lightweight tests without loading OCR models:

```powershell
py -3.10 -m unittest discover backend\tests
```

## API

### `GET /health`

```json
{
  "status": "ok",
  "version": "0.5.0",
  "app": "Manga Translator"
}
```

### `GET /api/status`

Returns backend, cache and OCR model status.

### `POST /api/process`

```json
{
  "screenshot_data": "base64_png",
  "coordinates": { "x": 100, "y": 150, "width": 200, "height": 100 },
  "source_lang": "auto",
  "target_lang": "tr",
  "zoom_level": 1,
  "preprocessing_mode": "auto"
}
```

```json
{
  "success": true,
  "translation": "Translated text",
  "original_text": "OCR raw text",
  "cleaned_text": "OCR cleaned text",
  "confidence": 0.92,
  "cached": false,
  "preprocessing_mode": "auto",
  "processing_ms": 840
}
```

## Sharing Plan

This is currently a local companion backend project. To share it with non-technical users, package the backend as a one-click Windows app and ship it with the extension folder.
