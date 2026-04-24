# Manga Translator - Backend

Lokal OCR ve çeviri için Python FastAPI backend.

## Bağımlılıklar

- FastAPI
- Uvicorn
- OpenCV (cv2)
- PaddleOCR
- googletrans
- Pillow
- python-multipart

## Kurulum

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
python app/main.py
```

Server `http://localhost:8000` adresinde çalışacak.

## API Endpoints

### POST `/api/process`

Manga bubble çevirisi işlemi.

**Request:**
```json
{
  "screenshot_data": "base64_encoded_image",
  "coordinates": {
    "x": 100,
    "y": 150,
    "width": 200,
    "height": 100
  },
  "source_lang": "ja",
  "target_lang": "tr"
}
```

**Response:**
```json
{
  "success": true,
  "translation": "Çevrilmiş metin",
  "confidence": 0.95,
  "original_text": "原文"
}
```

### GET `/health`

Server sağlık kontrolü.
