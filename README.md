# Manga Çeviri Sistemi 📖➡️

**%100 Ücretsiz, Lokal OCR, Chrome Extension + Python Backend**

Japonca / İngilizce manga okurken konuşma balonlarını seçin ve doğrudan Türkçe olarak okuyun. Popup değil, **orijinal metni doğal şekilde Türkçeyle değiştir**.

## 🎯 Hedef

```
Kullanıcı Manga Okur
    ↓
Konuşma Balonunu Seçer
    ↓
Türkçe Çevirisi Görünür
    ↓
Sanki Manga Baştan Türkçeymiş Gibi Hisset
```

## ✨ Özellikler (V0.5)

- ✅ Manuel bubble seçimi (mouse drag)
- ✅ `chrome.tabs.captureVisibleTab()` ile ekran görüntüsü
- ✅ OpenCV preprocessing (upscale, grayscale, contrast, threshold)
- ✅ **PaddleOCR** - Lokal, Japoncayı çok iyi okuyor
- ✅ **GoogleTrans** - Ücretsiz, API key yok
- ✅ DOM overlay (popup değil, doğrudan sayfada)
- ✅ Scroll ile birlikte hareket
- ✅ Hash-tabanlı cache

## 🚫 Yapılmayan Hatalar

- ❌ OCR.space kullanmadık (Paralı + API key)
- ❌ Tesseract kullanmadık (Mangalar için zayıf)
- ❌ React gereksizliği eklemedik (Vanilla JS)
- ❌ Popup fixed yapmadık (positioning absolute + tracking)
- ❌ Bubble auto-detection (V3'te)

## 🏗️ Teknoloji Yığını

| Katman | Teknoloji | Sebep |
|--------|-----------|-------|
| **OCR** | PaddleOCR | Ücretsiz, lokal, Japoncayı çok iyi okuyor |
| **Çeviri** | GoogleTrans | Ücretsiz, API key yok |
| **Backend** | FastAPI + Python | Hızlı, OpenCV desteği güçlü |
| **Frontend** | Chrome Extension Manifest V3 | Modern, güvenli |
| **Preprocessing** | OpenCV | Profesyonel image processing |

## 📁 Proje Yapısı

```
manga-translator/
├── extension/                 # Chrome Extension
│   ├── manifest.json
│   ├── popup/
│   │   ├── popup.html
│   │   ├── popup.css
│   │   └── popup.js
│   ├── content/              # Content script
│   │   ├── content.js
│   │   └── style.css
│   └── background/
│       └── background.js     # Service worker
│
├── backend/                   # Python FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   ├── ocr_engine.py
│   │   │   ├── image_processor.py
│   │   │   ├── translator.py
│   │   │   └── cache_manager.py
│   │   └── utils/
│   │       └── logger.py
│   └── requirements.txt
│
├── README.md
├── ROADMAP.md
└── ARCHITECTURE.md
```

## 🚀 Kurulum

### Backend Kurulumu

```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

Server `http://localhost:8000` adresinde çalışacak.

### Extension Kurulumu

1. Chrome'u açın
2. `chrome://extensions/` adresine gidin
3. "Geliştirici modu"nu açın (sağ üst)
4. "Paketlenmemiş uzantıyı yükle" tıklayın
5. `extension/` klasörünü seçin

## 📖 Kullanım

1. **Seçim Modunu Başlat**: Extension'ı açın, "Seçim Modunu Başlat" butonuna tıklayın
2. **Balonu Seç**: Konuşma balonunun üzerine fare ile drag yapın
3. **Türkçe Oku**: Overlay otomatik yerleşir ve Türkçe metni gösterir
4. **Scroll Edin**: Overlay scroll ile birlikte hareket eder

## 📋 API Endpoints

### POST `/api/process`
Manga bubble'ını işle

**Request:**
```json
{
  "screenshot_data": "base64_image",
  "coordinates": {"x": 100, "y": 150, "width": 200, "height": 100},
  "source_lang": "ja",
  "target_lang": "tr"
}
```

**Response:**
```json
{
  "success": true,
  "translation": "Çevrilmiş metin",
  "original_text": "原文",
  "confidence": 0.95
}
```

### GET `/health`
Server sağlık kontrolü

## 🗺️ Roadmap

- **V0.5** (Şu an): Temel işlevsellik
- **V1**: Cache, scroll tracking, ayarlar
- **V2**: Hotkeys, history, retry
- **V3**: Auto bubble detection, AI cleanup

Detaylar için [ROADMAP.md](./ROADMAP.md)

## 🏗️ Mimari

Detaylar için [ARCHITECTURE.md](./ARCHITECTURE.md)

## 📝 Lisans

Burada lisans bilgisi eklenebilir.

---

**Nihai Başarı Kriteri**: Kullanıcı bunu kapatınca normal manga okuyamıyor hissi yaşasın. 💪
