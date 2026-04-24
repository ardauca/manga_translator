// popup.js - Popup penceresi kontrol ve ayarları

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
  }

  attachEventListeners() {
    this.startBtn.addEventListener('click', () => this.startSelection());
    this.stopBtn.addEventListener('click', () => this.stopSelection());
    this.fontSizeInput.addEventListener('change', (e) => this.saveSetting('fontSize', e.target.value));
    this.opacityInput.addEventListener('change', (e) => this.saveSetting('opacity', e.target.value));
    this.sourceLangSelect.addEventListener('change', (e) => this.saveSetting('sourceLang', e.target.value));

    // Live update gösterimi
    this.fontSizeInput.addEventListener('input', (e) => {
      this.fontSizeValue.textContent = `${e.target.value}px`;
    });
    this.opacityInput.addEventListener('input', (e) => {
      this.opacityValue.textContent = `${Math.round(e.target.value * 100)}%`;
    });
  }

  startSelection() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs[0]) {
        this.updateStatus('Sekme bulunamadı', 'error');
        return;
      }

      chrome.tabs.sendMessage(tabs[0].id, { action: 'START_SELECTION' }, (response) => {
        if (chrome.runtime.lastError) {
          this.updateStatus('İçerik script yüklenmedi', 'error');
          return;
        }
        
        this.isSelecting = true;
        this.updateUI();
        this.updateStatus('Seçim modu aktif - Balonları seç');
      });
    });
  }

  stopSelection() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { action: 'STOP_SELECTION' });
      this.isSelecting = false;
      this.updateUI();
      this.updateStatus('Seçim iptal edildi');
    });
  }

  updateUI() {
    this.startBtn.disabled = this.isSelecting;
    this.stopBtn.disabled = !this.isSelecting;
  }

  updateStatus(message, type = 'info') {
    this.statusText.textContent = message;
    this.statusText.parentElement.style.backgroundColor = 
      type === 'error' ? '#fee2e2' : '#f0f9ff';
  }

  saveSetting(key, value) {
    chrome.storage.sync.set({ [key]: value });
  }

  loadSettings() {
    chrome.storage.sync.get(['fontSize', 'opacity', 'sourceLang'], (data) => {
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
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new PopupController();
});
