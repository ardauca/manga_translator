# Manga Translator

Chrome extension + local Python backend for translating selected manga speech bubbles into Turkish.

The current target is a reliable MVP: the user manually selects a bubble, the extension captures the visible tab, the backend crops the selection, runs OCR, translates the text, and renders the Turkish result back on the page.

## Features

- Manual speech bubble selection with mouse drag
- Chrome Manifest V3 extension
- `chrome.tabs.captureVisibleTab()` screenshot capture
- FastAPI backend
- OpenCV preprocessing
- PaddleOCR for local OCR
- `deep-translator` Google backend for translation
- In-memory hash cache for repeated selections
- Page overlay for translated text

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
      core/translator.py
      main.py
    requirements.txt
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

## Quick Start

### Backend

PowerShell:

```powershell
.\start_backend.ps1
```

Command Prompt:

```bat
start_backend.bat
```

The scripts create `.venv`, install backend dependencies, and start the server at `http://localhost:8000`.

Manual setup:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
cd backend
python app\main.py
```

### Extension

1. Open `chrome://extensions/`.
2. Enable Developer mode.
3. Click Load unpacked.
4. Select only the `extension/` folder, not the project root.
5. Make sure the popup Backend URL is `http://localhost:8000`.

## API

### `GET /health`

Returns backend health:

```json
{
  "status": "ok",
  "version": "0.5.0"
}
```

### `POST /api/process`

Request:

```json
{
  "screenshot_data": "base64_png",
  "coordinates": { "x": 100, "y": 150, "width": 200, "height": 100 },
  "source_lang": "auto",
  "target_lang": "tr",
  "zoom_level": 1
}
```

Response:

```json
{
  "success": true,
  "translation": "Çevrilmiş metin",
  "original_text": "原文",
  "confidence": 0.92
}
```

## Current Status

This is an MVP, not a packaged production extension yet. The main next tasks are improving OCR quality on varied manga panels, reducing first-run model download friction, adding tests around the backend pipeline, and polishing overlay behavior for long text.
