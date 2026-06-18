# Setup

## Requirements

- Windows
- Python 3.10
- Google Chrome
- Enough disk space for PaddleOCR model downloads

## Backend

Use the helper script:

```powershell
.\start_backend.ps1
```

Or install manually:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
cd backend
python app\main.py
```

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Chrome Extension

1. Go to `chrome://extensions/`.
2. Enable Developer mode.
3. Click Load unpacked.
4. Pick the `extension/` directory. Do not pick the project root.
5. Open the popup and confirm Backend URL is `http://localhost:8000`.

## Common Issues

- First OCR run is slow because PaddleOCR may download and initialize models.
- If the popup says the content script is not loaded, refresh the manga page after installing or reloading the extension.
- If translation fails, verify the backend terminal for errors and check that the machine has internet access.
