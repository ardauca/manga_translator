// popup.js - Reader-focused popup controls

class PopupController {
  constructor() {
    this.isSelecting = false;
    this.initElements();
    this.attachEventListeners();
    this.loadSettings();
    this.refreshBackendStatus();
    this.renderHistory();
  }

  initElements() {
    this.toggleSelectionBtn = document.getElementById('toggleSelectionBtn');
    this.translationsVisibleInput = document.getElementById('translationsVisible');
    this.clearHistoryBtn = document.getElementById('clearHistoryBtn');
    this.statusText = document.getElementById('statusText');
    this.backendBadge = document.getElementById('backendBadge');
    this.sourceLangSelect = document.getElementById('sourceLang');
    this.backendUrlInput = document.getElementById('backendUrl');
    this.maxOverlaysInput = document.getElementById('maxOverlays');
    this.maxOverlaysValue = document.getElementById('maxOverlaysValue');
    this.overlayTtlSelect = document.getElementById('overlayTtl');
    this.overlayTtlValue = document.getElementById('overlayTtlValue');
    this.fontSizeInput = document.getElementById('fontSize');
    this.fontSizeValue = document.getElementById('fontSizeValue');
    this.opacityInput = document.getElementById('opacity');
    this.opacityValue = document.getElementById('opacityValue');
    this.historyList = document.getElementById('historyList');
  }

  attachEventListeners() {
    this.toggleSelectionBtn.addEventListener('click', () => this.toggleSelection());
    this.translationsVisibleInput.addEventListener('change', (event) => {
      this.saveSetting('translationsVisible', event.target.checked);
      this.setPageTranslationsVisible(event.target.checked);
    });
    this.clearHistoryBtn.addEventListener('click', () => this.clearHistory());

    this.maxOverlaysInput.addEventListener('input', (event) => {
      const value = Number(event.target.value);
      this.maxOverlaysValue.textContent = value;
      this.saveSetting('maxOverlays', value);
      this.sendActiveTabMessage({ action: 'TRIM_OVERLAYS', maxOverlays: value });
    });

    this.overlayTtlSelect.addEventListener('change', (event) => {
      const value = Number(event.target.value);
      this.overlayTtlValue.textContent = this.formatTtl(value);
      this.saveSetting('overlayTtl', value);
    });

    this.fontSizeInput.addEventListener('input', (event) => {
      const value = Number(event.target.value);
      this.fontSizeValue.textContent = `${value}px`;
      this.saveSetting('fontSize', value);
    });

    this.opacityInput.addEventListener('input', (event) => {
      const value = Number(event.target.value);
      this.opacityValue.textContent = `${Math.round(value * 100)}%`;
      this.saveSetting('opacity', value);
    });

    this.sourceLangSelect.addEventListener('change', (event) => this.saveSetting('sourceLang', event.target.value));
    this.backendUrlInput.addEventListener('change', (event) => {
      this.saveSetting('backendUrl', event.target.value.trim());
      this.refreshBackendStatus();
    });

    chrome.storage.onChanged.addListener((changes, areaName) => {
      if (areaName === 'local' && changes.translationHistory) {
        this.renderHistory();
      }
    });
  }

  toggleSelection() {
    if (this.isSelecting) {
      this.stopSelection();
    } else {
      this.startSelection();
    }
  }

  startSelection() {
    this.sendActiveTabMessage({ action: 'START_SELECTION' }, (response) => {
      if (!response?.success) {
        this.updateStatus('Refresh the page and try again', 'error');
        return;
      }

      this.setSelectionState(true);
      this.updateStatus('Click and drag over a speech bubble');
    });
  }

  stopSelection() {
    this.sendActiveTabMessage({ action: 'STOP_SELECTION' }, () => {
      this.setSelectionState(false);
      this.updateStatus('Ready to translate');
    });
  }

  setPageTranslationsVisible(isVisible) {
    this.sendActiveTabMessage({ action: 'SET_OVERLAYS_VISIBLE', visible: isVisible }, () => {
      this.updateStatus(isVisible ? 'Translations visible' : 'Translations hidden');
    });
  }

  sendActiveTabMessage(message, callback = () => {}) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs[0]) {
        callback({ success: false });
        return;
      }

      chrome.tabs.sendMessage(tabs[0].id, message, (response) => {
        if (chrome.runtime.lastError) {
          callback({ success: false, error: chrome.runtime.lastError.message });
          return;
        }
        callback(response);
      });
    });
  }

  refreshBackendStatus() {
    this.backendBadge.className = 'status-dot status-muted';
    chrome.runtime.sendMessage({ action: 'CHECK_BACKEND' }, (response) => {
      if (chrome.runtime.lastError || !response?.success) {
        this.backendBadge.className = 'status-dot status-error';
        this.updateStatus('Backend is offline', 'error');
        return;
      }

      this.backendBadge.className = 'status-dot status-ok';
      this.updateStatus('Ready to translate');
    });
  }

  setSelectionState(isSelecting) {
    this.isSelecting = isSelecting;
    chrome.storage.local.set({ selectionActive: isSelecting });
    this.toggleSelectionBtn.textContent = isSelecting ? 'Pause' : 'Start Reading';
    this.toggleSelectionBtn.classList.toggle('is-active', isSelecting);
  }

  updateStatus(message, type = 'info') {
    this.statusText.textContent = message;
    this.statusText.parentElement.style.color = type === 'error' ? '#DC2626' : '#64748B';
  }

  saveSetting(key, value) {
    chrome.storage.sync.set({ [key]: value });
  }

  loadSettings() {
    chrome.storage.sync.get([
      'fontSize',
      'opacity',
      'sourceLang',
      'backendUrl',
      'maxOverlays',
      'overlayTtl',
      'translationsVisible'
    ], (data) => {
      const fontSize = data.fontSize || 14;
      const opacity = data.opacity || 0.95;
      const maxOverlays = data.maxOverlays || 8;
      const overlayTtl = data.overlayTtl ?? 0;
      const translationsVisible = data.translationsVisible !== false;

      this.fontSizeInput.value = fontSize;
      this.fontSizeValue.textContent = `${fontSize}px`;
      this.opacityInput.value = opacity;
      this.opacityValue.textContent = `${Math.round(opacity * 100)}%`;
      this.maxOverlaysInput.value = maxOverlays;
      this.maxOverlaysValue.textContent = maxOverlays;
      this.overlayTtlSelect.value = overlayTtl;
      this.overlayTtlValue.textContent = this.formatTtl(Number(overlayTtl));
      this.translationsVisibleInput.checked = translationsVisible;
      this.sourceLangSelect.value = data.sourceLang || 'auto';
      this.backendUrlInput.value = data.backendUrl || 'http://localhost:8000';
    });

    chrome.storage.local.get('selectionActive', (data) => {
      this.setSelectionState(Boolean(data.selectionActive));
    });
  }

  renderHistory() {
    chrome.storage.local.get('translationHistory', (data) => {
      const history = (data.translationHistory || []).slice(0, 3);
      this.historyList.textContent = '';

      if (!history.length) {
        const empty = document.createElement('p');
        empty.className = 'empty-state';
        empty.textContent = 'Translations will appear here after you select a bubble.';
        this.historyList.appendChild(empty);
        return;
      }

      for (const item of history) {
        const row = document.createElement('div');
        row.className = 'history-item';

        const translation = document.createElement('div');
        translation.className = 'history-translation';
        translation.textContent = item.translation || '';

        const original = document.createElement('div');
        original.className = 'history-original';
        original.textContent = item.originalText || item.cleanedText || '';

        row.appendChild(translation);
        if (original.textContent) {
          row.appendChild(original);
        }
        this.historyList.appendChild(row);
      }
    });
  }

  clearHistory() {
    chrome.storage.local.set({ translationHistory: [] }, () => {
      this.renderHistory();
      this.updateStatus('Recent translations cleared');
    });
  }

  formatTtl(seconds) {
    if (!seconds) return 'Never';
    if (seconds < 60) return `${seconds}s`;
    return `${Math.round(seconds / 60)}m`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new PopupController();
});
