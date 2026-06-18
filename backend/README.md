# Manga Translator Backend

FastAPI service for processing selected manga speech bubbles.

## Run

From the project root:

```powershell
.\start_backend.ps1
```

Manual:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
cd backend
python app\main.py
```

## Endpoints

- `GET /health`
- `GET /api/status`
- `POST /api/process`
- `POST /api/process-with-cache`
- `GET /api/cache/stats`
- `DELETE /api/cache`

## Pipeline

1. Decode base64 screenshot.
2. Normalize selected coordinates with browser zoom/device pixel ratio.
3. Crop the selected area.
4. Check in-memory cache.
5. Preprocess image with selected OCR mode.
6. Extract text with PaddleOCR.
7. Clean OCR text.
8. Translate with `deep-translator`.
9. Cache and return translation, OCR confidence and processing time.

## Tests

```powershell
py -3.10 -m unittest discover backend\tests
```
