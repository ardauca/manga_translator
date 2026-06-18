@echo off
setlocal

echo ======================================
echo Manga Translator Backend
echo ======================================

if not exist ".venv\Scripts\activate.bat" (
  echo.
  echo [*] Creating .venv with Python 3.10...
  py -3.10 -m venv .venv
  if errorlevel 1 exit /b %errorlevel%
)

echo.
echo [*] Activating .venv...
call .venv\Scripts\activate.bat
if errorlevel 1 exit /b %errorlevel%

echo.
echo [*] Installing backend dependencies...
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
if errorlevel 1 exit /b %errorlevel%

echo.
echo [*] Starting backend server...
cd backend
python app\main.py

endlocal
