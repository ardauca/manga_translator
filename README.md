# Manga Translator

Manga balonlarını Chrome üzerinde seçip Türkçeye çeviren lokal OCR destekli eklenti.

Proje iki parçadan oluşur:

- Chrome extension: balon seçimi, ekran görüntüsü alma, overlay gösterimi
- Python backend: crop, OpenCV preprocessing, PaddleOCR, çeviri ve cache

## Yetenekler

- Mouse ile manuel konuşma balonu seçimi
- Chrome Manifest V3 eklentisi
- Görünür sekmeden screenshot alma
- Seçilen alanı backend tarafında kırpma
- OpenCV ile OCR öncesi görüntü iyileştirme
- PaddleOCR ile lokal Japonca/İngilizce OCR
- `deep-translator` ile Türkçeye çeviri
- Aynı seçimler için bellek içi cache
- Sayfa üzerinde çeviri overlay'i
- Popup üzerinden kaynak dil, yazı boyutu, opaklık ve backend URL ayarı
- Backend bağlantısı yoksa anlaşılır hata mesajı

## Sınırlar

- Backend lokal çalışmalıdır; eklenti tek başına OCR yapmaz.
- İlk OCR denemesi yavaş olabilir çünkü PaddleOCR model indirip başlatır.
- Cache bellek içindedir; backend kapanınca sıfırlanır.
- Otomatik balon algılama henüz yoktur.
- Uzantı olarak proje kökü değil, yalnızca `extension/` klasörü yüklenmelidir.

## Proje Yapısı

```text
manga_translator/
  backend/
    app/
      api/routes.py
      core/cache_manager.py
      core/image_processor.py
      core/ocr_engine.py
      core/settings_manager.py
      core/translator.py
      main.py
    requirements.txt
  extension/
    background/background.js
    content/content.js
    content/style.css
    manifest.json
    popup/popup.html
    popup/popup.css
    popup/popup.js
  start_backend.ps1
  start_backend.bat
```

## Kurulum

Backend'i başlat:

```powershell
.\start_backend.ps1
```

Script `.venv` oluşturur, bağımlılıkları kurar ve backend'i `http://localhost:8000` adresinde başlatır.

Backend sağlık kontrolü:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Chrome eklentisini yükle:

1. `chrome://extensions/` sayfasını aç.
2. Developer mode'u aç.
3. Load unpacked seç.
4. Sadece `C:\Users\ARDA\Desktop\Python\manga_translator\extension` klasörünü seç.
5. Manga sayfasını yenile.

## Kullanım

1. Backend terminalini açık bırak.
2. Eklenti popup'ından seçimi başlat.
3. Manga balonunu mouse ile seç.
4. Çeviri sayfa üzerinde overlay olarak görünür.

## API

### `GET /health`

```json
{
  "status": "ok",
  "version": "0.5.0"
}
```

### `POST /api/process`

```json
{
  "screenshot_data": "base64_png",
  "coordinates": { "x": 100, "y": 150, "width": 200, "height": 100 },
  "source_lang": "auto",
  "target_lang": "tr",
  "zoom_level": 1
}
```

```json
{
  "success": true,
  "translation": "Çevrilmiş metin",
  "original_text": "原文",
  "confidence": 0.92
}
```

## Paylaşım Notu

Bu proje şu an "local companion backend" modelindedir. Başka bir kullanıcıya vermek için extension yanında backend'i de çalıştırabilecekleri bir paket gerekir. Bir sonraki ürünleşme adımı backend'i tek tıkla çalışan Windows uygulamasına paketlemektir.
