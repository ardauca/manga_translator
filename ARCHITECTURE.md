# Architecture - Manga Çeviri Sistemi

## System Overview

```
Browser (Content Script)
    ↓ (Mouse Selection + captureVisibleTab)
Extension Service Worker
    ↓ (Screenshot)
Backend FastAPI
    ↓ (Processing Pipeline)
Browser (Overlay Render)
```

---

## Component Details

### 1. Chrome Extension

#### manifest.json
- **Manifest V3** (modern, secure)
- Permissions: `activeTab`, `tabs`, `scripting`, `storage`
- Host permissions: `<all_urls>` (tüm siteler)

#### Content Script (content.js)
Sayfada çalışan kod:

```
SelectionManager
├── Mouse events (drag rectangle)
└── Overlay rendering + tracking

OverlayManager
├── Position fixed in DOM
└── DOM mutation tracking

TrackerManager
├── Scroll listener (throttled)
├── ResizeObserver
└── MutationObserver
```

**Throttling**: Scroll event 50ms delay (performance)

#### Background Service Worker (background.js)
Extension-level kontrol:

```
MessageHandler
├── Content script messages
├── captureVisibleTab() trigger
└── Backend communication
```

#### Storage
- Chrome `storage.sync` API
- Settings persist: fontSize, opacity, sourceLang
- Cache keys stored locally (not synced)

---

### 2. Backend (Python FastAPI)

#### Architecture

```
FastAPI Server (8000)
├── Routes (/api/process, /health)
├── OCREngine (PaddleOCR)
├── ImageProcessor (OpenCV)
├── Translator (GoogleTrans)
└── CacheManager (hash-based)
```

#### Processing Pipeline (Request → Response)

```
1. Input: Base64 screenshot + coordinates
   ↓
2. Decode: PIL Image object
   ↓
3. Crop: 4-corner crop using coordinates
   ↓
4. Preprocess: ImageProcessor
   - Resize 2x (upscale for OCR)
   - Grayscale
   - Bilateral filter (denoise)
   - CLAHE (contrast)
   - Adaptive threshold
   - Morphology (optional)
   ↓
5. OCR: PaddleOCR.ocr()
   - Japanese orientation detection
   - Returns: text + confidence
   ↓
6. Translate: GoogleTranslator.translate()
   - Source: auto/ja/en
   - Target: tr
   ↓
7. Cache: Hash-based storage
   - Key: SHA256(image_hash + coords + lang)
   - TTL: 24 hours
   ↓
8. Response: JSON
   {translation, original_text, confidence}
```

#### Image Preprocessing Details

**Why 2x upscale?**
- PaddleOCR performs better on larger images
- Manga text often small, crowded

**Pipeline Justification:**
1. **Bilateral Filter**: Preserves edges while denoising
2. **CLAHE**: Adaptive contrast (better than global histogram)
3. **Adaptive Threshold**: Better for varying image backgrounds
4. **Morphology**: Optional, closes small gaps in text

**Orientation Detection:**
- PaddleOCR's `use_angle_cls=True` detects Japanese vertical/horizontal
- Automatic rotation correction

#### Cache System

```
CacheManager
├── In-memory dict (no DB needed for V0.5)
├── Key generation: SHA256(image_hash + position + lang)
├── Value: {translation, timestamp}
├── LRU eviction: oldest removed when size > max
└── TTL: 24 hours (auto-expire)
```

**Why image_hash + position?**
- Same bubble, different page: different cache keys
- Same content, different position: different visual context

---

### 3. Communication Flow

#### User Action Sequence

```
User selects bubble (drag)
    ↓
SelectionManager.onMouseUp()
    ↓
Content script sends: {action: 'CAPTURE_AND_PROCESS', coordinates}
    ↓
Background.js receives message
    ↓
chrome.tabs.captureVisibleTab() → Base64 PNG
    ↓
Background sends: {screenshot_data, coordinates, lang} → Backend
    ↓
Backend /api/process endpoint
    ↓
Returns: {translation, confidence}
    ↓
Content script renders overlay
    ↓
TrackerManager watches for scroll/resize
    ↓
Overlay stays positioned correctly
```

**Latency Targets:**
- Selection → Capture: ~100ms
- Capture → Backend: Network dependent
- Backend processing: ~500ms - 2s (depends on image size, OCR speed)
- Render: ~50ms
- Total: ~1-3s per bubble

---

## Data Structures

### Screenshot Request

```typescript
{
  screenshot_data: string,        // Base64 PNG
  coordinates: {
    x: number,                     // Pixel from left
    y: number,                     // Pixel from top
    width: number,
    height: number
  },
  source_lang: 'auto' | 'ja' | 'en',
  target_lang: 'tr'
}
```

### Processing Response

```typescript
{
  success: boolean,
  translation: string,            // Turkish text
  original_text: string,          // Detected Japanese/English
  confidence: number              // 0.0 - 1.0
}
```

### Overlay DOM Structure

```html
<div class="manga-overlay" 
     style="position: fixed; left: Xpx; top: Ypx;">
  Çevrilmiş metin
</div>
```

---

## Performance Considerations

### Bottlenecks (V0.5)

1. **PaddleOCR Model Loading**: ~2-3s on first load
   - Solution (V1): Preload in background

2. **Image Upload to Backend**: Network dependent
   - Solution (V1): Compression, Delta encoding

3. **Preprocessing**: ~200-500ms
   - Solution (V1): GPU support, model optimization

### Optimization Roadmap

- V0.5: Baseline (1-3s per bubble)
- V1: Model caching, compression (~500ms)
- V2: GPU support, quantization (~200ms)
- V3: Edge inference, local model (~100ms)

---

## Security

### CORS
- Allowed: `*` (permissive for MVP)
- Production: Restrict to extension origin

### Content Script Isolation
- DOMContentLoaded after page ready
- No access to page JavaScript
- Safe message passing via `chrome.runtime.onMessage`

### Input Validation
- Base64 screenshot size limit (10MB)
- Coordinate boundary checks
- Language code whitelist (ja, en, auto)

---

## Error Handling

### Graceful Degradation

```
If OCR fails:
  → Show "Metin bulunamadı" (no translation)

If Translation fails:
  → Show original text (untranslated)

If Backend unreachable:
  → Error toast "Backend bağlantısı başarısız"

If Overlay positioning breaks:
  → Manual reposition or dismiss
```

---

## Debugging

### Browser DevTools
- Extension logs: `chrome://extensions` → Details → Errors
- Content script: Right-click → Inspect

### Backend Logs
```bash
python app/main.py
# Shows: INFO, ERROR with timestamps
```

### Cache Stats
```
GET /api/cache/stats
{
  "size": 150,
  "max_size": 1000,
  "usage_percent": 15
}
```

---

## Deployment

### Local Development
```bash
# Terminal 1: Backend
cd backend && python app/main.py

# Terminal 2: Load extension in Chrome
# chrome://extensions > Load unpacked > select extension/
```

### Production (Future)
- Backend: Docker container on VPS
- Extension: Chrome Web Store submission
- Database: PostgreSQL for cache (V2+)
