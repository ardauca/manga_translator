// content.js - Content script (manuel seçim sistemi)

// MessageHandler - popup ve background ile iletişim
class MessageHandler {
  static init() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'START_SELECTION') {
        selectionManager.start();
      } else if (request.action === 'STOP_SELECTION') {
        selectionManager.stop();
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
  }

  start() {
    if (this.isActive) return;
    
    this.isActive = true;
    document.addEventListener('mousedown', this.onMouseDown.bind(this));
    document.addEventListener('mousemove', this.onMouseMove.bind(this));
    document.addEventListener('mouseup', this.onMouseUp.bind(this));
    
    // Feedback
    document.body.style.cursor = 'crosshair';
    console.log('[Manga Translator] Seçim modu başladı');
  }

  stop() {
    if (!this.isActive) return;
    
    this.isActive = false;
    document.removeEventListener('mousedown', this.onMouseDown.bind(this));
    document.removeEventListener('mousemove', this.onMouseMove.bind(this));
    document.removeEventListener('mouseup', this.onMouseUp.bind(this));
    
    if (this.selectionBox) {
      this.selectionBox.remove();
      this.selectionBox = null;
    }
    
    document.body.style.cursor = 'default';
    console.log('[Manga Translator] Seçim modu durduruldu');
  }

  onMouseDown(e) {
    if (!this.isActive) return;
    
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

    // Seçim koordinatlarını kaydet
    const rect = this.selectionBox.getBoundingClientRect();
    this.selectedArea = {
      x: Math.round(rect.left),
      y: Math.round(rect.top),
      width: Math.round(rect.width),
      height: Math.round(rect.height)
    };

    if (this.selectedArea.width > 20 && this.selectedArea.height > 20) {
      // Background'a screenshot talebi gönder
      chrome.runtime.sendMessage({
        action: 'CAPTURE_AND_PROCESS',
        coordinates: this.selectedArea
      }, (response) => {
        if (chrome.runtime.lastError) {
          console.error('Capture hatası:', chrome.runtime.lastError);
          return;
        }
        
        if (response && response.success) {
          // Overlay göster
          overlayManager.show(response.translation, this.selectedArea);
        }
      });
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

  show(translation, coordinates) {
    // Eski overlay'i kaldır
    this.clear();

    // Overlay container
    const overlay = document.createElement('div');
    overlay.className = 'manga-overlay';
    
    // Ayarları oku
    chrome.storage.sync.get(['fontSize', 'opacity'], (data) => {
      const fontSize = data.fontSize || 14;
      const opacity = data.opacity || 0.95;

      overlay.style.cssText = `
        position: fixed;
        left: ${coordinates.x}px;
        top: ${coordinates.y}px;
        width: ${coordinates.width}px;
        height: ${coordinates.height}px;
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
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.4;
      `;

      overlay.textContent = translation;
      document.body.appendChild(overlay);
      
      // Scroll ile hareket etmesi için tracker ekle
      trackerManager.trackOverlay(overlay, coordinates);
    });
  }

  clear() {
    const existing = document.querySelectorAll('.manga-overlay');
    existing.forEach(el => el.remove());
  }
}

// TrackerManager - Scroll ve layout değişikliklerini izle
class TrackerManager {
  constructor() {
    this.observers = new Map();
    this.scrollTimeout = null;
  }

  trackOverlay(overlay, originalCoordinates) {
    // Scroll listener
    const handleScroll = () => {
      clearTimeout(this.scrollTimeout);
      this.scrollTimeout = setTimeout(() => {
        this.updateOverlayPosition(overlay, originalCoordinates);
      }, 50); // Throttled
    };

    // ResizeObserver - layout changes
    const resizeObserver = new ResizeObserver(() => {
      this.updateOverlayPosition(overlay, originalCoordinates);
    });

    window.addEventListener('scroll', handleScroll);
    resizeObserver.observe(document.body);

    this.observers.set(overlay, { resizeObserver, scrollHandler: handleScroll });
  }

  updateOverlayPosition(overlay, originalCoordinates) {
    // Viewport relative konum hesapla
    const rect = overlay.getBoundingClientRect();
    overlay.style.left = `${rect.left + window.scrollX}px`;
    overlay.style.top = `${rect.top + window.scrollY}px`;
  }

  cleanup() {
    this.observers.forEach(({ resizeObserver, scrollHandler }) => {
      resizeObserver.disconnect();
      window.removeEventListener('scroll', scrollHandler);
    });
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
