# Backend startup script for PowerShell
# Activates venv310 and starts the server

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Manga Translator Backend" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Activate venv310
Write-Host "`n[*] Activating venv310..." -ForegroundColor Yellow
& .\venv310\Scripts\Activate.ps1

# Verify Python environment
Write-Host "`n[*] Verifying Python environment..." -ForegroundColor Yellow
python -c "import sys; print('Python:', sys.executable); print('Version:', sys.version.split()[0])"

# Start backend
Write-Host "`n[*] Starting backend server..." -ForegroundColor Yellow
cd backend
python app/main.py
