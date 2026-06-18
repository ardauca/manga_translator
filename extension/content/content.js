// content.js - Manual selection and clean translation overlays

if (window.__mangaTranslatorLoaded) {
  console.info('[Manga Translator] Content script already loaded');
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
        } else if (request.action === 'CLEAR_OVERLAYS') {
          overlayManager.clearAll();
          sendResponse({ success: true });
        } else if (request.action === 'SET_OVERLAYS_VISIBLE') {
          overlayManager.setVisible(Boolean(request.visible));
          sendResponse({ success: true });
        } else if (request.action === 'TRIM_OVERLAYS') {
          overlayManager.trim(Number(request.maxOverlays) || 8);
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
        border: 2px solid #2563EB;
        background: rgba(37, 99, 235, 0.10);
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
        overlayManager.showNotice('Selection is too small');
        return;
      }

      processor.processSelection(selectedArea);
    }
  }

  class SelectionProcessor {
    processSelection(selectedArea) {
      chrome.storage.sync.get([
        'sourceLang',
        'maxOverlays',
        'overlayTtl',
        'translationsVisible'
      ], (settings) => {
        chrome.runtime.sendMessage({
          action: 'CAPTURE_AND_PROCESS',
          coordinates: {
            x: selectedArea.x,
            y: selectedArea.y,
            width: selectedArea.width,
            height: selectedArea.height
          },
          sourceLang: settings.sourceLang || 'auto',
          preprocessingMode: 'auto',
          zoomLevel: window.devicePixelRatio || 1.0
        }, (response) => {
          if (chrome.runtime.lastError) {
            overlayManager.showNotice(chrome.runtime.lastError.message);
            return;
          }

          if (!response?.success) {
            overlayManager.showNotice(response?.error || 'Translation failed');
            return;
          }

          overlayManager.showTranslation(response, selectedArea, {
            maxOverlays: Number(settings.maxOverlays) || 8,
            overlayTtl: Number(settings.overlayTtl) || 0,
            visible: settings.translationsVisible !== false
          });
          historyManager.add(response);
        });
      });
    }
  }

  class OverlayManager {
    clearAll() {
      document.querySelectorAll('.manga-overlay, .manga-translator-notice').forEach((element) => element.remove());
    }

    setVisible(isVisible) {
      document.querySelectorAll('.manga-overlay').forEach((element) => {
        element.style.display = isVisible ? 'flex' : 'none';
      });
    }

    trim(maxOverlays) {
      const overlays = Array.from(document.querySelectorAll('.manga-overlay'));
      while (overlays.length > maxOverlays) {
        overlays.shift().remove();
      }
    }

    showTranslation(response, selectedArea, options) {
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
          background: rgba(255, 255, 255, ${opacity});
          padding: 8px;
          border-radius: 6px;
          z-index: 2147483646;
          color: #0F172A;
          text-align: center;
          overflow-wrap: anywhere;
          font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          line-height: 1.35;
          box-sizing: border-box;
          display: ${options.visible ? 'flex' : 'none'};
          align-items: center;
          justify-content: center;
          font-size: ${fontSize}px;
          font-weight: 750;
        `;

        overlay.textContent = response.translation;
        document.body.appendChild(overlay);
        this.trim(options.maxOverlays);

        if (options.overlayTtl > 0) {
          setTimeout(() => overlay.remove(), options.overlayTtl * 1000);
        }
      });
    }

    showNotice(message) {
      document.querySelectorAll('.manga-translator-notice').forEach((element) => element.remove());
      const notice = document.createElement('div');
      notice.className = 'manga-translator-notice';
      notice.textContent = message;
      notice.style.cssText = `
        position: fixed;
        right: 16px;
        bottom: 16px;
        max-width: 320px;
        padding: 10px 12px;
        background: #0F172A;
        color: white;
        border-radius: 8px;
        z-index: 2147483647;
        font: 13px Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      `;
      document.body.appendChild(notice);
      setTimeout(() => notice.remove(), 3500);
    }
  }

  class HistoryManager {
    add(response) {
      const item = {
        translation: response.translation || '',
        originalText: response.cleanedText || response.originalText || '',
        createdAt: Date.now()
      };

      chrome.storage.local.get('translationHistory', (data) => {
        const history = [item, ...(data.translationHistory || [])].slice(0, 20);
        chrome.storage.local.set({ translationHistory: history });
      });
    }
  }

  const selectionManager = new SelectionManager();
  const overlayManager = new OverlayManager();
  const processor = new SelectionProcessor();
  const historyManager = new HistoryManager();

  MessageHandler.init();
  console.info('[Manga Translator] Content script loaded');
}
