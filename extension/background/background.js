// background.js - Service worker for backend communication and screenshot capture

class BackgroundWorker {
  constructor() {
    this.initMessageHandlers();
  }

  initMessageHandlers() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'CAPTURE_AND_PROCESS') {
        this.captureAndProcess(request, sendResponse);
        return true;
      }

      if (request.action === 'CHECK_BACKEND') {
        this.checkBackend(sendResponse);
        return true;
      }

    });
  }

  async captureAndProcess(request, sendResponse) {
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
          coordinates: request.coordinates,
          source_lang: request.sourceLang || 'auto',
          target_lang: request.targetLang || 'tr',
          zoom_level: request.zoomLevel || 1.0,
          preprocessing_mode: request.preprocessingMode || 'auto'
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Backend error ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      sendResponse({
        success: true,
        backendUrl,
        translation: result.translation,
        originalText: result.original_text,
        cleanedText: result.cleaned_text,
        confidence: result.confidence
      });
    } catch (error) {
      sendResponse({
        success: false,
        error: this.toUserMessage(error)
      });
    }
  }

  async checkBackend(sendResponse) {
    try {
      const backendUrl = await this.findReachableBackend();
      const status = await this.fetchJson(`${backendUrl}/api/status`);
      sendResponse({
        success: true,
        backendUrl,
        status
      });
    } catch (error) {
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
    try {
      const response = await this.fetchWithTimeout(`${url}/health`, { cache: 'no-store' }, 2500);
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  async fetchJson(url) {
    const response = await this.fetchWithTimeout(url, { cache: 'no-store' }, 2500);
    if (!response.ok) {
      throw new Error(`Backend error ${response.status}`);
    }
    return response.json();
  }

  async fetchWithTimeout(url, options, timeoutMs) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      return await fetch(url, { ...options, signal: controller.signal });
    } finally {
      clearTimeout(timer);
    }
  }

  toUserMessage(error) {
    if (error.message === 'BACKEND_UNREACHABLE') {
      return 'Backend is not running. Start it with start_backend.ps1 and check the Backend URL.';
    }

    if (error.message === 'Failed to fetch') {
      return 'Backend connection failed. Check http://localhost:8000.';
    }

    return error.message;
  }
}

new BackgroundWorker();
