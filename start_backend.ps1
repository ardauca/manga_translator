# Backend startup script for PowerShell

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Manga Translator Backend" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "`n[*] Creating .venv with Python 3.10..." -ForegroundColor Yellow
    py -3.10 -m venv .venv
}

Write-Host "`n[*] Activating .venv..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

Write-Host "`n[*] Installing backend dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt

Write-Host "`n[*] Starting backend server..." -ForegroundColor Yellow
Set-Location backend
python app\main.py
