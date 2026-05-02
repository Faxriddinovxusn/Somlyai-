/**
 * WebSocket Service for Somly AI Mini App.
 *
 * Responsibilities:
 * 1. Persistent connection with auto-reconnect (exponential backoff, max 5 attempts).
 * 2. Background visibility optimization — when the app tab is hidden, incoming
 *    events are suppressed and a `needsSync` flag is set. When the tab becomes
 *    visible again a single `ws_sync` event fires so every mounted component
 *    can re-fetch its data in one batch.
 * 3. Dispatches granular `CustomEvent`s on `window` so React components can
 *    subscribe via standard `addEventListener` without any coupling to this module.
 */

import { getUserId } from './api';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeout = null;
    this.isConnected = false;
    this.userId = getUserId();

    /** When true, events arrived while the tab was hidden. */
    this.needsSync = false;

    // Bind visibility handler once
    this._onVisibilityChange = this._onVisibilityChange.bind(this);
    document.addEventListener('visibilitychange', this._onVisibilityChange);
  }

  /* ────────── Connection lifecycle ────────── */

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws?user_id=${this.userId}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('[WS] Connected.');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      window.dispatchEvent(new CustomEvent('ws_connected'));
    };

    this.ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (!payload.event) return;

        // If app is in background, suppress real-time dispatches.
        // Just flag that a sync is needed when user returns.
        if (document.visibilityState === 'hidden') {
          this.needsSync = true;
          return;
        }

        console.log(`[WS] Event: ${payload.event}`, payload.data);
        window.dispatchEvent(
          new CustomEvent(`ws_${payload.event}`, { detail: payload.data })
        );
      } catch (e) {
        console.error('[WS] Message parse error:', e);
      }
    };

    this.ws.onclose = () => {
      this.isConnected = false;
      console.log('[WS] Disconnected.');
      window.dispatchEvent(new CustomEvent('ws_disconnected'));
      this._scheduleReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('[WS] Error:', err);
      // onerror is always followed by onclose — reconnect logic lives there.
    };
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /* ────────── Reconnection with exponential backoff ────────── */

  _scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnect attempts reached.');
      window.dispatchEvent(new CustomEvent('ws_offline_mode'));
      return;
    }
    this.reconnectAttempts++;
    // Exponential backoff: 1s → 2s → 4s → 8s → 16s
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 16000);
    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})...`);
    this.reconnectTimeout = setTimeout(() => this.connect(), delay);
  }

  /* ────────── Background / Foreground optimization ────────── */

  _onVisibilityChange() {
    if (document.visibilityState === 'visible' && this.needsSync) {
      this.needsSync = false;
      console.log('[WS] Tab returned to foreground — dispatching ws_sync.');
      window.dispatchEvent(new CustomEvent('ws_sync'));
    }
  }
}

export const wsService = new WebSocketService();
