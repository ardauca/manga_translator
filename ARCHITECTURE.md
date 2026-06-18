# Architecture

## Model

Proje local companion backend modeliyle çalışır. Chrome extension kullanıcı etkileşimini yönetir; ağır OCR ve çeviri işi lokal FastAPI backend'e gider.

```text
Content script
  -> kullanıcı balonu seçer
Background service worker
  -> visible tab screenshot alır
FastAPI backend
  -> crop, preprocess, OCR, translate, cache
Content script
  -> çeviri overlay'i basar
```

## Extension

- `popup/`: seçim başlatma, ayarlar ve backend URL girişi
- `content/content.js`: seçim kutusu, hata bildirimi ve çeviri overlay'i
- `background/background.js`: screenshot alma, backend health check, `/api/process` çağrısı
- `manifest.json`: Chrome Manifest V3 tanımı

Önemli not: Extension yalnızca `extension/` klasöründen yüklenmelidir. Proje kökü yüklenirse `.venv` gibi klasörler de Chrome tarafından paket parçası gibi taranır.

## Backend

- `main.py`: FastAPI uygulaması ve CORS
- `api/routes.py`: request doğrulama, screenshot decode, crop, cache, OCR, translate
- `core/image_processor.py`: OpenCV preprocessing
- `core/ocr_engine.py`: PaddleOCR model yönetimi ve sonuç parse etme
- `core/translator.py`: `deep-translator` entegrasyonu
- `core/cache_manager.py`: TTL destekli bellek içi cache
- `core/settings_manager.py`: environment tabanlı ayarlar

## Veri Akışı

1. Content script viewport koordinatlarını background worker'a yollar.
2. Background worker backend `/health` kontrolü yapar.
3. Backend uygunsa visible tab screenshot alınır.
4. Screenshot ve koordinatlar `/api/process` endpoint'ine gider.
5. Backend koordinatları zoom seviyesine göre ölçekler ve screenshot sınırlarına kırpar.
6. Cache hit varsa direkt sonuç döner.
7. Cache miss varsa OpenCV preprocessing, PaddleOCR ve çeviri çalışır.
8. Sonuç cache'e yazılır ve extension overlay gösterir.

## Tradeofflar

- Lokal backend gizlilik ve maliyet açısından iyi, kurulum açısından ek adım gerektirir.
- Hosted backend kullanıcı deneyimini kolaylaştırır ama sunucu maliyeti ve gizlilik sorumluluğu doğurur.
- Tarayıcı içinde OCR şu an bu proje için pratik değildir; model boyutu ve performans sorunları yüksek olur.
