# Roadmap - Manga Çeviri Sistemi

## V0.5 - Foundation (Şu an ✅)

**Hedef**: Tek bir bubble tamamen düzgün şekilde çevrilsin.

### Must-Have
- [x] Chrome Extension (Manifest V3)
- [x] Manuel seçim (mouse drag rectangle)
- [x] `chrome.tabs.captureVisibleTab()`
- [x] Backend crop işlemi
- [x] OpenCV preprocessing
- [x] PaddleOCR metin okuma
- [x] GoogleTrans çeviri
- [x] Basic DOM overlay
- [x] Scroll tracking (throttled)

### Scope
- Popup show/hide değil
- Multi-bubble değil
- Settings minimal
- Cache V1'de

---

## V1 - Usability

**Timeline**: ~2 hafta sonra

### Özellikler
- [ ] Cache sistemi (hash-tabanlı)
- [ ] ResizeObserver + MutationObserver integration
- [ ] Settings panel (font size, opacity, source lang)
- [ ] Multiple sequential bubbles
- [ ] Overlay repositioning (drag)
- [ ] Error handling ve retry

### Backend Improvements
- [ ] Cache stats endpoint
- [ ] Performance metrics
- [ ] Logging improvements

---

## V2 - Power User Features

**Timeline**: ~4 hafta sonra

### Özellikler
- [ ] Keyboard shortcuts (Ctrl+Shift+S)
- [ ] Translation history
- [ ] Copy to clipboard
- [ ] Hover translate (preview)
- [ ] Batch processing
- [ ] Custom font support

### UX
- [ ] Better error messages
- [ ] Loading spinner
- [ ] Undo/redo (basic)

---

## V3 - AI & Automation

**Timeline**: ~8 hafta sonra

### Big Features
- [ ] Auto bubble detection (YOLOv8)
- [ ] AI text cleanup (non-essential text removal)
- [ ] Typesetting (text wrapping, size fitting)
- [ ] Manga-specific fonts
- [ ] Offline translation model (optional)

### Advanced
- [ ] Multi-language support beyond JP/EN
- [ ] Style transfer (manga font matching)
- [ ] Sound effects translation
- [ ] Context-aware translation

---

## Won't Do (Scope Out)

- ❌ Mobile support (Chrome mobile yapısı farklı)
- ❌ UI beautification (functional >> pretty)
- ❌ Multiple backends (complexity)
- ❌ Real-time collaboration
- ❌ DL/paid translation APIs

---

## Success Metrics

1. **V0.5**: Tek bubble %90+ accuracy, <5 saniye işlem
2. **V1**: 10 sequential bubble %95+ accuracy, <1 saniye each
3. **V2**: Power users happy, 10+ active users
4. **V3**: Kullanıcı hiç tıklamadan çevirir (full auto)

---

## Current Blockers / Considerations

1. **PaddleOCR Model Size**: ~500MB (ilk download'da yavaş)
   - Çözüm: Background'da model caching

2. **Manga Image Variety**: Different art styles
   - Çözüm: Adaptive preprocessing (V2)

3. **Translation Quality**: GoogleTrans'ın kısıtlaması
   - Fallback: LibreTranslate (V2)

4. **Performance**: PaddleOCR + PyTorch heavy
   - Çözüm: Quantization, GPU support (V2)
