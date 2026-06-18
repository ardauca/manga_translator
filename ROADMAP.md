# Roadmap

## V0.5 - MVP Stabilization

- [x] Manual selection in the browser
- [x] Visible tab screenshot capture
- [x] Backend crop and preprocessing
- [x] PaddleOCR integration
- [x] Translation integration
- [x] Overlay rendering
- [x] In-memory cache on `/api/process`
- [ ] Backend unit tests with mocked OCR and translator
- [ ] OCR quality tuning on a small sample set

## V1 - Usability

- [ ] Multiple overlays without clearing the previous one by default
- [ ] Retry button on failed translations
- [ ] Translation history
- [ ] Copy to clipboard
- [ ] Better long-text fitting inside selected bubbles
- [ ] Optional backend URL health check from the popup

## V2 - Quality and Speed

- [ ] Benchmark preprocessing strategies
- [ ] Add performance metrics for OCR and translation
- [ ] Persist cache between backend restarts
- [ ] Optional GPU configuration guide
- [ ] More robust language handling

## V3 - Automation

- [ ] Automatic bubble detection
- [ ] Batch processing
- [ ] Typesetting improvements
- [ ] Offline translation exploration

## Out of Scope for Now

- Chrome mobile support
- Paid translation APIs
- Multi-user backend deployment
