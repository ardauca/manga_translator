# Setup

## Requirements

- Windows
- Python 3.10
- Google Chrome
- Disk space for PaddleOCR model downloads

## Backend

Recommended:

```powershell
.\start_backend.ps1
```

Manual:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
cd backend
python app\main.py
```

Check:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Chrome Extension

1. Open `chrome://extensions/`.
2. Enable Developer mode.
3. Click Load unpacked.
4. Select only the `extension/` folder.
5. Do not select the project root.
6. Keep Backend URL as `http://localhost:8000` unless you changed the backend port.

## Common Issues

- `Failed to fetch`: backend is not running or port 8000 is not reachable.
- `ssl_key.pem` warning: the project root was loaded as the extension. Remove it and load only `extension/`.
- Slow first OCR: PaddleOCR downloads and initializes models on first use.
- Content script error: reload the extension and refresh the manga page.
