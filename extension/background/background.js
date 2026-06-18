// background.js - Service worker for screenshot capture and backend calls

class BackgroundWorker {
  constructor() {
    this.initMessageHandlers();
    console.log('[Manga Translator] Background service worker active');
  }

  initMessageHandlers() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'CAPTURE_AND_PROCESS') {
        this.captureAndProcess(request.coordinates, request.sourceLang, request.zoomLevel, sendResponse);
        return true;
      }
    });
  }

  async captureAndProcess(coordinates, sourceLang, zoomLevel, sendResponse) {
    try {
      const backendUrl = await this.findReachableBackend();
      const screenshotDataUrl = await chrome.tabs.captureVisibleTab(null, { format: 'png' });
      const base64Data = screenshotDataUrl.replace(/^data:image\/png;base64,/, '');

      const response = await fetch(`${backendUrl}/api/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          screenshot_data: base64Data,
          coordinates,
          source_lang: sourceLang || 'auto',
          target_lang: 'tr',
          zoom_level: zoomLevel || 1.0
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Backend error ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      sendResponse({
        success: true,
        translation: result.translation,
        originalText: result.original_text,
        confidence: result.confidence
      });
    } catch (error) {
      console.error('[Manga Translator] Capture/process failed:', error);
      sendResponse({
        success: false,
        error: this.toUserMessage(error)
      });
    }
  }

  async findReachableBackend() {
    const settings = await chrome.storage.sync.get('backendUrl');
    const configuredUrl = this.normalizeBackendUrl(settings.backendUrl || 'http://localhost:8000');
    const candidates = [
      configuredUrl,
      'http://127.0.0.1:8000',
      'http://localhost:8000'
    ].filter((url, index, urls) => url && urls.indexOf(url) === index);

    for (const url of candidates) {
      if (await this.healthCheck(url)) {
        return url;
      }
    }

    throw new Error('BACKEND_UNREACHABLE');
  }

  normalizeBackendUrl(url) {
    return String(url || '').trim().replace(/\/$/, '');
  }

  async healthCheck(url) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 2500);

    try {
      const response = await fetch(`${url}/health`, {
        method: 'GET',
        cache: 'no-store',
        signal: controller.signal
      });
      return response.ok;
    } catch (error) {
      return false;
    } finally {
      clearTimeout(timer);
    }
  }

  toUserMessage(error) {
    if (error.message === 'BACKEND_UNREACHABLE') {
      return 'Backend çalışmıyor. Önce start_backend.ps1 dosyasını çalıştır ve popup Backend URL değerini kontrol et.';
    }

    if (error.message === 'Failed to fetch') {
      return 'Backend bağlantısı başarısız. Backend açık mı ve http://localhost:8000 erişilebilir mi?';
    }

    return error.message;
  }
}

new BackgroundWorker();
