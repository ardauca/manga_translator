# Setup

## Gereksinimler

- Windows
- Python 3.10
- Google Chrome
- PaddleOCR modelleri için yeterli disk alanı

## Backend

Önerilen yol:

```powershell
.\start_backend.ps1
```

Manuel kurulum:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
cd backend
python app\main.py
```

Kontrol:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Chrome Extension

1. `chrome://extensions/` adresini aç.
2. Developer mode'u etkinleştir.
3. Load unpacked seç.
4. Sadece `extension/` klasörünü seç. Proje kökünü seçme.
5. Popup'ta Backend URL değerini `http://localhost:8000` olarak bırak.

## Sık Karşılaşılan Durumlar

- `Failed to fetch`: Backend kapalıdır veya port 8000 erişilemiyordur.
- `ssl_key.pem` uyarısı: Proje kökü uzantı olarak yüklenmiştir. Uzantıyı kaldırıp `extension/` klasöründen yükle.
- İlk OCR yavaş: PaddleOCR ilk kullanımda model indirir ve yükler.
- Content script hatası: Eklentiyi reload edip manga sayfasını yenile.
