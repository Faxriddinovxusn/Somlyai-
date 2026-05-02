// Central API logic with Offline Caching and Error Handling

const API_BASE_URL = '/api'; // Using relative path so Vite proxy handles it

// Simple helper to get the current user ID
export const getUserId = () => {
  return window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 123456789; // fallback
};

// ═══════════════════════════════════════
// TOAST NOTIFICATION SYSTEM
// ═══════════════════════════════════════

let toastTimeout = null;

export const showToast = (message, type = 'error', duration = 4000) => {
  const existing = document.getElementById('somly-toast');
  if (existing) existing.remove();
  if (toastTimeout) clearTimeout(toastTimeout);

  const toast = document.createElement('div');
  toast.id = 'somly-toast';

  const bgColor = type === 'error' ? 'rgba(255, 69, 58, 0.95)'
    : type === 'warning' ? 'rgba(255, 159, 10, 0.95)'
    : type === 'success' ? 'rgba(48, 209, 88, 0.95)'
    : 'rgba(44, 44, 46, 0.95)';

  toast.style.cssText = `
    position: fixed; top: 20px; left: 16px; right: 16px;
    background: ${bgColor};
    color: #FFF; padding: 14px 16px; border-radius: 14px;
    font-weight: 600; font-size: 14px; z-index: 9999;
    display: flex; align-items: center; gap: 10px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    animation: slideDown 0.3s ease-out;
    backdrop-filter: blur(20px);
    line-height: 1.4;
  `;
  toast.innerHTML = `<span style="flex:1">${message}</span><button onclick="this.parentElement.remove()" style="background:rgba(255,255,255,0.2); border:none; color:#FFF; padding:4px 10px; border-radius:8px; font-weight:600; font-size:12px; cursor:pointer">✕</button>`;

  document.body.appendChild(toast);

  toastTimeout = setTimeout(() => {
    if (toast.parentElement) {
      toast.style.animation = 'slideUp 0.3s ease-in forwards';
      setTimeout(() => toast.remove(), 300);
    }
  }, duration);
};

// ═══════════════════════════════════════
// API FETCH WITH CACHE & ERROR HANDLING
// ═══════════════════════════════════════

export const fetchApi = async (endpoint, options = {}, retryCount = 0) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Auto-inject user_id
  let finalUrl = url;
  if (!options.method || options.method === 'GET' || (options.method === 'DELETE' && !options.body)) {
    const separator = url.includes('?') ? '&' : '?';
    finalUrl = `${url}${separator}user_id=${getUserId()}`;
  } else if (options.body && typeof options.body === 'string') {
    try {
      const parsed = JSON.parse(options.body);
      parsed.user_id = getUserId();
      options.body = JSON.stringify(parsed);
    } catch (e) {
      // ignore
    }
  }

  const isGet = !options.method || options.method === 'GET';
  const cacheKey = `cache_${endpoint}`;

  // ── Offline check ──
  if (!navigator.onLine) {
    if (isGet) {
      // Return from Cache
      const cachedData = localStorage.getItem(cacheKey);
      if (cachedData) {
        console.log(`[Cache Hit] Returning offline data for ${endpoint}`);
        return JSON.parse(cachedData);
      }
      throw new Error('OFFLINE_NO_CACHE');
    } else {
      // Block action offline
      showToast('📡 Bu amal uchun internet kerak.', 'warning');
      throw new Error('OFFLINE_ACTION_BLOCKED');
    }
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout

    const response = await fetch(finalUrl, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      }
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const status = response.status;
      if (status >= 500) {
        showToast('⚠️ Server xatosi. Qayta urinib ko\'ring.', 'error');
        throw new Error('SERVER_ERROR');
      }
      if (status === 429 && retryCount < 1) {
        await new Promise(r => setTimeout(r, 2000));
        return fetchApi(endpoint, options, retryCount + 1);
      }
      throw new Error(`HTTP Error: ${status}`);
    }

    const data = await response.json();
    
    // Save to Cache if GET
    if (isGet) {
      localStorage.setItem(cacheKey, JSON.stringify(data));
    }
    
    return data;
    
  } catch (error) {
    if (error.name === 'AbortError') {
      showToast('⏳ So\'rov uzoq davom etdi. Qayta urinib ko\'ring.', 'warning');
      throw new Error('TIMEOUT');
    }
    
    // Connection refused / network error -> auto retry -> then fallback to cache if GET
    if (error.message === 'Failed to fetch' || error.message.includes('NetworkError')) {
      if (retryCount < 1) {
        await new Promise(r => setTimeout(r, 1000));
        return fetchApi(endpoint, options, retryCount + 1);
      }
      
      // If GET, try cache as fallback even if technically "online" but fetch failed
      if (isGet) {
        const cachedData = localStorage.getItem(cacheKey);
        if (cachedData) {
          console.log(`[Fallback] Fetch failed, returning cache for ${endpoint}`);
          return JSON.parse(cachedData);
        }
      }
      
      window.dispatchEvent(new Event('api_server_error'));
      throw new Error('SERVER_ERROR');
    }
    
    throw error;
  }
};

// ═══════════════════════════════════════
// BOT NOTIFICATION
// ═══════════════════════════════════════

export const notifyBot = async (message) => {
  try {
    if (!navigator.onLine) return; // Silent return if offline
    await fetchApi('/notify_action', {
      method: 'POST',
      body: JSON.stringify({ message })
    });
  } catch (err) {
    console.error("Failed to notify bot:", err);
  }
};

let _exchangeRatesCache = null;
let _exchangeRatesPromise = null;

export const getExchangeRates = async () => {
  if (_exchangeRatesCache) return _exchangeRatesCache;
  if (_exchangeRatesPromise) return _exchangeRatesPromise;
  
  _exchangeRatesPromise = fetchApi('/exchange-rates')
    .then(data => {
      _exchangeRatesCache = data?.rates || {};
      return _exchangeRatesCache;
    })
    .catch(err => {
      console.warn("Failed to fetch exchange rates:", err);
      return {};
    });
    
  return _exchangeRatesPromise;
};
