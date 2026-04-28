// content.js - Content script (manuel seçim sistemi)

// ✅ ÇÖZÜM 2: Double injection guard
if (window.__mangaTranslatorLoaded) {
  console.log('[Manga Translator] Already loaded, skipping duplicate injection');
} else {
  window.__mangaTranslatorLoaded = true;
  console.log('[Manga Translator] Loading content script...');

// MessageHandler - popup ve background ile iletişim
class MessageHandler {
  static init() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      console.log('[Manga Translator] Content: Mesaj alındı:', request.action);
      
      if (request.action === 'START_SELECTION') {
        selectionManager.start();
        sendResponse({ success: true });
      } else if (request.action === 'STOP_SELECTION') {
        selectionManager.stop();
        sendResponse({ success: true });
      }
    });
  }
}

// SelectionManager - Manuel bubble seçimi
class SelectionManager {
  constructor() {
    this.isActive = false;
    this.startX = 0;
    this.startY = 0;
    this.selectionBox = null;
    this.selectedArea = null;
    
    // Listener functions stored as instance properties to allow removal
    this.onMouseDownBound = this.onMouseDown.bind(this);
    this.onMouseMoveBound = this.onMouseMove.bind(this);
    this.onMouseUpBound = this.onMouseUp.bind(this);
  }

  start() {
    if (this.isActive) return;
    
    this.isActive = true;
    document.addEventListener('mousedown', this.onMouseDownBound);
    document.addEventListener('mousemove', this.onMouseMoveBound);
    document.addEventListener('mouseup', this.onMouseUpBound);
    
    // Feedback
    document.body.style.cursor = 'crosshair';
    console.log('[Manga Translator] Seçim modu başladı');
  }

  stop() {
    if (!this.isActive) return;
    
    this.isActive = false;
    document.removeEventListener('mousedown', this.onMouseDownBound);
    document.removeEventListener('mousemove', this.onMouseMoveBound);
    document.removeEventListener('mouseup', this.onMouseUpBound);
    
    if (this.selectionBox) {
      this.selectionBox.remove();
      this.selectionBox = null;
    }
    
    document.body.style.cursor = 'default';
    console.log('[Manga Translator] Seçim modu durduruldu');
  }

  onMouseDown(e) {
    if (!this.isActive) return;
    if (this.selectionBox) return; // ✅ ÇÖZÜM 1: Double mousedown guard
    
    this.startX = e.clientX;
    this.startY = e.clientY;

    // Selection box oluştur
    this.selectionBox = document.createElement('div');
    this.selectionBox.className = 'manga-selection-box';
    this.selectionBox.style.cssText = `
      position: fixed;
      left: ${this.startX}px;
      top: ${this.startY}px;
      width: 0;
      height: 0;
      border: 2px dashed #2563eb;
      background: rgba(37, 99, 235, 0.1);
      pointer-events: none;
      z-index: 999999;
      box-sizing: border-box;
    `;
    document.body.appendChild(this.selectionBox);
    console.log('[Manga Translator] Selection box başladı:', { x: this.startX, y: this.startY });
  }

  onMouseMove(e) {
    if (!this.isActive || !this.selectionBox) return;

    const width = Math.abs(e.clientX - this.startX);
    const height = Math.abs(e.clientY - this.startY);
    const left = Math.min(this.startX, e.clientX);
    const top = Math.min(this.startY, e.clientY);

    this.selectionBox.style.left = `${left}px`;
    this.selectionBox.style.top = `${top}px`;
    this.selectionBox.style.width = `${width}px`;
    this.selectionBox.style.height = `${height}px`;
  }

  onMouseUp(e) {
    if (!this.isActive || !this.selectionBox) return;

    // ✅ VIEWPORT coordinates (position:fixed kullanıyor)
    const rect = this.selectionBox.getBoundingClientRect();
    
    // Viewport coordinates'i OLDUĞU GİBİ KUL
    // position:fixed için viewport koordinatlar doğru
    this.selectedArea = {
      x: Math.round(rect.left),
      y: Math.round(rect.top),
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      // Ayrıca page koordinatlarını da sakla (backend için)
      pageX: Math.round(rect.left + window.scrollX),
      pageY: Math.round(rect.top + window.scrollY)
    };

    console.log('[Manga Translator] Selection box bitti (viewport):', {
      viewport: { x: this.selectedArea.x, y: this.selectedArea.y },
      page: { x: this.selectedArea.pageX, y: this.selectedArea.pageY },
      size: { w: this.selectedArea.width, h: this.selectedArea.height },
      scroll: { scrollX: window.scrollX, scrollY: window.scrollY }
    });

    // Minimum 5x5 test için (production'da 20x20)
    if (this.selectedArea.width > 5 && this.selectedArea.height > 5) {
      // Background'a screenshot talebi gönder
      console.log('[Manga Translator] Seçim yapıldı, backend çağrısı başlıyor...');
      
      // Popup'tan kaydedilmiş dili oku
      chrome.storage.sync.get('sourceLang', (data) => {
        const sourceLang = data.sourceLang || 'auto';
        console.log('[Manga Translator] Kaynak dil seçildi:', sourceLang);
        
        // ✅ FIX: Sadece backend'in istediği fields'ları gönder
        const cleanCoordinates = {
          x: this.selectedArea.x,
          y: this.selectedArea.y,
          width: this.selectedArea.width,
          height: this.selectedArea.height
        };
        
        console.log('[Manga Translator] Sending to background:', { cleanCoordinates, sourceLang });
        
        chrome.runtime.sendMessage({
          action: 'CAPTURE_AND_PROCESS',
          coordinates: cleanCoordinates,
          sourceLang: sourceLang
        }, (response) => {
          console.log('[Manga Translator] Content: Response alındı:', response);
          
          if (chrome.runtime.lastError) {
            console.error('[Manga Translator] Content: Capture hatası:', chrome.runtime.lastError);
            return;
          }
          
          if (response && response.success) {
            console.log('[Manga Translator] Content: Overlay gösteriliyor - Çeviri:', response.translation);
            // ✅ FIX: page coordinates kullan çünkü position: absolute
            // Overlay bubble'la birlikte scroll edecek
            overlayManager.show(response.translation, this.selectedArea);
          } else {
            console.error('[Manga Translator] Content: Response başarısız', response);
          }
        });
      });
    } else {
      console.log('[Manga Translator] Seçim çok küçük, yoksay:', this.selectedArea);
    }

    // Selection box'ı temizle
    if (this.selectionBox) {
      this.selectionBox.remove();
      this.selectionBox = null;
    }
  }
}

// OverlayManager - Çeviri overlay gösterimi
class OverlayManager {
  constructor() {
    this.overlays = new Map();
  }

  show(translation, selectedArea) {
    // Eski overlay'i kaldır
    this.clear();

    // Overlay container
    const overlay = document.createElement('div');
    overlay.className = 'manga-overlay';
    
    // Ayarları oku
    chrome.storage.sync.get(['fontSize', 'opacity'], (data) => {
      const fontSize = data.fontSize || 14;
      const opacity = data.opacity || 0.95;

      // ✅ DOĞRU: position: absolute + page coordinates
      // Overlay bubble'la birlikte page'de kalır ve scroll ile birlikte hareket eder
      const pageX = selectedArea.pageX || selectedArea.x;
      const pageY = selectedArea.pageY || selectedArea.y;
      
      console.log('[Manga Translator] Overlay show:', {
        position: 'absolute (page coordinates)',
        coords: { x: pageX, y: pageY },
        size: { w: selectedArea.width, h: selectedArea.height }
      });

      overlay.style.cssText = `
        position: absolute;
        left: ${pageX}px;
        top: ${pageY}px;
        width: ${selectedArea.width}px;
        height: ${selectedArea.height}px;
        background: white;
        opacity: ${opacity};
        padding: 8px;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        z-index: 999998;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: ${fontSize}px;
        font-weight: 600;
        color: #111827;
        text-align: center;
        word-wrap: break-word;
        overflow: visible;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.4;
        box-sizing: border-box;
      `;

      overlay.textContent = translation;
      document.body.appendChild(overlay);
      
      console.log('[Manga Translator] Overlay appended to DOM');
      
      // Debug: immediate computed style check
      setTimeout(() => {
        if (overlay.parentElement) {
          const rect = overlay.getBoundingClientRect();
          console.log('[Manga Translator] Overlay rect:', {
            left: rect.left,
            top: rect.top,
            width: rect.width,
            height: rect.height,
            visible: rect.height > 0
          });
        }
      }, 50);
      
      // No tracker needed for absolute positioning - it scrolls naturally
    });
  }

  clear() {
    const existing = document.querySelectorAll('.manga-overlay');
    existing.forEach(el => el.remove());
  }
}

// TrackerManager - Deprecated (position: absolute naturally scrolls)
class TrackerManager {
  constructor() {
    this.observers = new Map();
  }

  trackOverlay(overlay, coordinates) {
    // No-op: position: absolute naturally follows page scrolling
    // This manager kept for backward compatibility
  }

  updateOverlayPosition(overlay, coordinates) {
    // No-op
  }

  cleanup() {
    this.observers.clear();
  }
}

// Global instances
const selectionManager = new SelectionManager();
const overlayManager = new OverlayManager();
const trackerManager = new TrackerManager();

// İnitialize
MessageHandler.init();
console.log('[Manga Translator] Content script yüklendi');

} // ← Guard kapanış

