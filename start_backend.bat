@echo off
REM Backend başlatma scripti - venv310 kullanarak başlatır

echo ======================================
echo Manga Translator Backend
echo ======================================

REM venv310 aktif et
echo.
echo [*] Aktivating venv310...
call venv310\Scripts\activate.bat

REM Python versiyonunu kontrol et
echo.
echo [*] Verifying Python environment...
python -c "import sys; print('Python:', sys.executable); print('Version:', sys.version.split()[0])"

REM Backend başlat
echo.
echo [*] Starting backend server...
cd backend
python app/main.py

pause
