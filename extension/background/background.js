// background.js - Service Worker (screenshot ve messaging)

class BackgroundWorker {
  constructor() {
    this.initMessageHandlers();
    console.log('[Manga Translator] Background service worker aktif');
  }

  initMessageHandlers() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'CAPTURE_AND_PROCESS') {
        this.captureAndProcess(request.coordinates, request.sourceLang, sendResponse);
        return true; // Async response
      }
    });
  }

  async captureAndProcess(coordinates, sourceLang, sendResponse) {
    try {
      console.log('[Manga Translator] ===== CAPTURE START =====');
      console.log('[Manga Translator] Coordinates:', coordinates);
      console.log('[Manga Translator] Source Lang:', sourceLang);
      
      // Tab'ın ekran görüntüsünü al (data URL format)
      console.log('[Manga Translator] Capturing visible tab...');
      const screenshotDataUrl = await chrome.tabs.captureVisibleTab(null, { format: 'png' });
      console.log('[Manga Translator] Screenshot captured:', screenshotDataUrl.length, 'chars');
      
      // Data URL'den base64'ü çıkar (data:image/png;base64, kısmını kaldır)
      const base64Data = screenshotDataUrl.replace(/^data:image\/png;base64,/, '');
      console.log('[Manga Translator] Base64 extracted:', base64Data.length, 'chars');
      
      const requestPayload = {
        screenshot_data: base64Data,
        coordinates: coordinates,
        source_lang: sourceLang || 'auto',
        target_lang: 'tr'
      };
      
      console.log('[Manga Translator] Sending to backend...');
      console.log('[Manga Translator] URL: http://localhost:8000/api/process');
      console.log('[Manga Translator] Payload keys:', Object.keys(requestPayload));
      
      // Backend'e gönder
      const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestPayload)
      });

      console.log('[Manga Translator] Backend response status:', response.status);
      console.log('[Manga Translator] Backend response headers:', response.headers.get('content-type'));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[Manga Translator] Backend error response:', errorText);
        throw new Error(`Backend hatası: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('[Manga Translator] Backend result:', result);
      console.log('[Manga Translator] Translation:', result.translation);
      console.log('[Manga Translator] ===== CAPTURE SUCCESS =====\n');
      
      sendResponse({
        success: true,
        translation: result.translation,
        confidence: result.confidence
      });

    } catch (error) {
      console.error('[Manga Translator] ===== CAPTURE ERROR =====');
      console.error('[Manga Translator] Error:', error.message);
      console.error('[Manga Translator] Error stack:', error.stack);
      console.error('[Manga Translator] ===== END ERROR =====\n');
      
      sendResponse({
        success: false,
        error: error.message
      });
    }
  }
}

// Initialize
new BackgroundWorker();
