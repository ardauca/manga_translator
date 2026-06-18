// content.js - Manual selection and overlay rendering

if (window.__mangaTranslatorLoaded) {
  console.log('[Manga Translator] Content script already loaded');
} else {
  window.__mangaTranslatorLoaded = true;

  class MessageHandler {
    static init() {
      chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
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

  class SelectionManager {
    constructor() {
      this.isActive = false;
      this.startX = 0;
      this.startY = 0;
      this.selectionBox = null;

      this.onMouseDownBound = this.onMouseDown.bind(this);
      this.onMouseMoveBound = this.onMouseMove.bind(this);
      this.onMouseUpBound = this.onMouseUp.bind(this);
    }

    start() {
      if (this.isActive) return;

      this.isActive = true;
      document.body.classList.add('manga-selection-active');
      document.body.style.cursor = 'crosshair';
      document.addEventListener('mousedown', this.onMouseDownBound, true);
      document.addEventListener('mousemove', this.onMouseMoveBound, true);
      document.addEventListener('mouseup', this.onMouseUpBound, true);
      chrome.storage.local.set({ selectionActive: true });
    }

    stop() {
      if (!this.isActive) return;

      this.isActive = false;
      document.body.classList.remove('manga-selection-active');
      document.body.style.cursor = '';
      document.removeEventListener('mousedown', this.onMouseDownBound, true);
      document.removeEventListener('mousemove', this.onMouseMoveBound, true);
      document.removeEventListener('mouseup', this.onMouseUpBound, true);
      chrome.storage.local.set({ selectionActive: false });

      if (this.selectionBox) {
        this.selectionBox.remove();
        this.selectionBox = null;
      }
    }

    onMouseDown(event) {
      if (!this.isActive || this.selectionBox) return;

      event.preventDefault();
      this.startX = event.clientX;
      this.startY = event.clientY;
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
        z-index: 2147483647;
        box-sizing: border-box;
      `;
      document.body.appendChild(this.selectionBox);
    }

    onMouseMove(event) {
      if (!this.isActive || !this.selectionBox) return;

      event.preventDefault();
      const width = Math.abs(event.clientX - this.startX);
      const height = Math.abs(event.clientY - this.startY);
      const left = Math.min(this.startX, event.clientX);
      const top = Math.min(this.startY, event.clientY);

      this.selectionBox.style.left = `${left}px`;
      this.selectionBox.style.top = `${top}px`;
      this.selectionBox.style.width = `${width}px`;
      this.selectionBox.style.height = `${height}px`;
    }

    onMouseUp(event) {
      if (!this.isActive || !this.selectionBox) return;

      event.preventDefault();
      const rect = this.selectionBox.getBoundingClientRect();
      const selectedArea = {
        x: Math.round(rect.left),
        y: Math.round(rect.top),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        pageX: Math.round(rect.left + window.scrollX),
        pageY: Math.round(rect.top + window.scrollY)
      };

      this.selectionBox.remove();
      this.selectionBox = null;

      if (selectedArea.width < 8 || selectedArea.height < 8) {
        overlayManager.showNotice('Seçim çok küçük');
        return;
      }

      chrome.storage.sync.get('sourceLang', (data) => {
        chrome.runtime.sendMessage({
          action: 'CAPTURE_AND_PROCESS',
          coordinates: {
            x: selectedArea.x,
            y: selectedArea.y,
            width: selectedArea.width,
            height: selectedArea.height
          },
          sourceLang: data.sourceLang || 'auto',
          zoomLevel: window.devicePixelRatio || 1.0
        }, (response) => {
          if (chrome.runtime.lastError) {
            overlayManager.showNotice(chrome.runtime.lastError.message);
            return;
          }

          if (response?.success) {
            overlayManager.show(response.translation, selectedArea);
          } else {
            overlayManager.showNotice(response?.error || 'Çeviri alınamadı');
          }
        });
      });
    }
  }

  class OverlayManager {
    clear() {
      document.querySelectorAll('.manga-overlay, .manga-translator-notice').forEach((element) => element.remove());
    }

    show(translation, selectedArea) {
      this.clear();

      const overlay = document.createElement('div');
      overlay.className = 'manga-overlay';

      chrome.storage.sync.get(['fontSize', 'opacity'], (data) => {
        const fontSize = data.fontSize || 14;
        const opacity = data.opacity || 0.95;
        const pageX = selectedArea.pageX || selectedArea.x;
        const pageY = selectedArea.pageY || selectedArea.y;

        overlay.style.cssText = `
          position: absolute;
          left: ${pageX}px;
          top: ${pageY}px;
          width: ${selectedArea.width}px;
          min-height: ${selectedArea.height}px;
          background: white;
          opacity: ${opacity};
          padding: 8px;
          border-radius: 4px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
          z-index: 2147483646;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: ${fontSize}px;
          font-weight: 600;
          color: #111827;
          text-align: center;
          overflow-wrap: anywhere;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          line-height: 1.4;
          box-sizing: border-box;
          cursor: default;
        `;

        overlay.textContent = translation;
        document.body.appendChild(overlay);
      });
    }

    showNotice(message) {
      this.clear();
      const notice = document.createElement('div');
      notice.className = 'manga-translator-notice';
      notice.textContent = message;
      notice.style.cssText = `
        position: fixed;
        right: 16px;
        bottom: 16px;
        max-width: 320px;
        padding: 10px 12px;
        background: #111827;
        color: white;
        border-radius: 6px;
        z-index: 2147483647;
        font: 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
      `;
      document.body.appendChild(notice);
      setTimeout(() => notice.remove(), 3500);
    }
  }

  const selectionManager = new SelectionManager();
  const overlayManager = new OverlayManager();

  MessageHandler.init();
  console.log('[Manga Translator] Content script loaded');
}
