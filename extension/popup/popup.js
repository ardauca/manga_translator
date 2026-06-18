// popup.js - Popup controls and settings

class PopupController {
  constructor() {
    this.isSelecting = false;
    this.initElements();
    this.attachEventListeners();
    this.loadSettings();
  }

  initElements() {
    this.startBtn = document.getElementById('startSelectionBtn');
    this.stopBtn = document.getElementById('stopSelectionBtn');
    this.statusText = document.getElementById('statusText');
    this.sourceLangSelect = document.getElementById('sourceLang');
    this.fontSizeInput = document.getElementById('fontSize');
    this.fontSizeValue = document.getElementById('fontSizeValue');
    this.opacityInput = document.getElementById('opacity');
    this.opacityValue = document.getElementById('opacityValue');
    this.backendUrlInput = document.getElementById('backendUrl');
  }

  attachEventListeners() {
    this.startBtn.addEventListener('click', () => this.startSelection());
    this.stopBtn.addEventListener('click', () => this.stopSelection());
    this.fontSizeInput.addEventListener('change', (event) => this.saveSetting('fontSize', event.target.value));
    this.opacityInput.addEventListener('change', (event) => this.saveSetting('opacity', event.target.value));
    this.sourceLangSelect.addEventListener('change', (event) => this.saveSetting('sourceLang', event.target.value));
    this.backendUrlInput.addEventListener('change', (event) => this.saveSetting('backendUrl', event.target.value.trim()));

    this.fontSizeInput.addEventListener('input', (event) => {
      this.fontSizeValue.textContent = `${event.target.value}px`;
    });

    this.opacityInput.addEventListener('input', (event) => {
      this.opacityValue.textContent = `${Math.round(event.target.value * 100)}%`;
    });
  }

  startSelection() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs[0]) {
        this.updateStatus('Sekme bulunamadı', 'error');
        return;
      }

      chrome.tabs.sendMessage(tabs[0].id, { action: 'START_SELECTION' }, (response) => {
        if (chrome.runtime.lastError || !response?.success) {
          this.updateStatus('Sayfayı yenileyip tekrar dene', 'error');
          return;
        }

        this.setSelectionState(true);
        this.updateStatus('Seçim modu aktif');
      });
    });
  }

  stopSelection() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs[0]) {
        this.setSelectionState(false);
        return;
      }

      chrome.tabs.sendMessage(tabs[0].id, { action: 'STOP_SELECTION' }, () => {
        this.setSelectionState(false);
        this.updateStatus('Seçim iptal edildi');
      });
    });
  }

  setSelectionState(isSelecting) {
    this.isSelecting = isSelecting;
    chrome.storage.local.set({ selectionActive: isSelecting });
    this.updateUI();
  }

  updateUI() {
    this.startBtn.disabled = this.isSelecting;
    this.stopBtn.disabled = !this.isSelecting;
  }

  updateStatus(message, type = 'info') {
    this.statusText.textContent = message;
    this.statusText.parentElement.style.backgroundColor = type === 'error' ? '#fee2e2' : '#f0f9ff';
    this.statusText.parentElement.style.borderColor = type === 'error' ? '#fecaca' : '#bfdbfe';
  }

  saveSetting(key, value) {
    chrome.storage.sync.set({ [key]: value });
  }

  loadSettings() {
    chrome.storage.sync.get(['fontSize', 'opacity', 'sourceLang', 'backendUrl'], (data) => {
      if (data.fontSize) {
        this.fontSizeInput.value = data.fontSize;
        this.fontSizeValue.textContent = `${data.fontSize}px`;
      }

      if (data.opacity) {
        this.opacityInput.value = data.opacity;
        this.opacityValue.textContent = `${Math.round(data.opacity * 100)}%`;
      }

      if (data.sourceLang) {
        this.sourceLangSelect.value = data.sourceLang;
      }

      if (data.backendUrl) {
        this.backendUrlInput.value = data.backendUrl;
      }
    });

    chrome.storage.local.get('selectionActive', (data) => {
      this.isSelecting = Boolean(data.selectionActive);
      this.updateUI();
      this.updateStatus(this.isSelecting ? 'Seçim modu aktif' : 'Hazır');
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new PopupController();
});
