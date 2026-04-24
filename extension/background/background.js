// background.js - Service Worker (screenshot ve messaging)

class BackgroundWorker {
  constructor() {
    this.initMessageHandlers();
    console.log('[Manga Translator] Background service worker aktif');
  }

  initMessageHandlers() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'CAPTURE_AND_PROCESS') {
        this.captureAndProcess(request.coordinates, sender.tabId, sendResponse);
        return true; // Async response
      }
    });
  }

  async captureAndProcess(coordinates, tabId, sendResponse) {
    try {
      // Tab'ın ekran görüntüsünü al
      const screenshot = await chrome.tabs.captureVisibleTab(null, { format: 'png' });
      
      // Backend'e gönder
      const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          screenshot_data: screenshot,
          coordinates: coordinates,
          source_lang: 'auto',
          target_lang: 'tr'
        })
      });

      if (!response.ok) {
        throw new Error(`Backend hatası: ${response.status}`);
      }

      const result = await response.json();
      
      sendResponse({
        success: true,
        translation: result.translation,
        confidence: result.confidence
      });

    } catch (error) {
      console.error('[Manga Translator] Error:', error);
      sendResponse({
        success: false,
        error: error.message
      });
    }
  }
}

// Initialize
new BackgroundWorker();
