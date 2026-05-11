import React, { useState, useEffect, useCallback } from 'react';
import './admin.css';

/* ═══════════════════════════════════════
   PIN LOCK SCREEN
   ═══════════════════════════════════════ */
const PinLock = ({ onUnlock }) => {
  const [pin, setPin] = useState('');
  const [error, setError] = useState(false);
  const [shake, setShake] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleDigit = useCallback((digit) => {
    if (pin.length >= 4) return;
    const newPin = pin + digit;
    setPin(newPin);
    setError(false);

    if (newPin.length === 4) {
      verifyPin(newPin);
    }
  }, [pin]);

  const handleBackspace = () => {
    setPin(p => p.slice(0, -1));
    setError(false);
  };

  const verifyPin = async (code) => {
    setLoading(true);
    try {
      const res = await fetch('/api/admin/pin-verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pin: code }),
      });
      const data = await res.json();
      if (data.success && data.token) {
        sessionStorage.setItem('admin_token', data.token);
        onUnlock(data.token);
      } else {
        setError(true);
        setShake(true);
        setTimeout(() => { setShake(false); setPin(''); }, 600);
      }
    } catch {
      setError(true);
      setShake(true);
      setTimeout(() => { setShake(false); setPin(''); }, 600);
    }
    setLoading(false);
  };

  const digits = [1,2,3,4,5,6,7,8,9,null,0,'⌫'];

  return (
    <div className="pin-screen">
      <div className="pin-container">
        <div className="pin-logo">🔐</div>
        <h2 className="pin-title">Admin Panel</h2>
        <p className="pin-subtitle">PIN kodni kiriting</p>

        <div className={`pin-dots ${shake ? 'shake' : ''}`}>
          {[0,1,2,3].map(i => (
            <div key={i} className={`pin-dot ${i < pin.length ? 'filled' : ''} ${error ? 'error' : ''}`} />
          ))}
        </div>

        {error && <p className="pin-error">❌ Noto'g'ri PIN. Qayta kiriting.</p>}

        <div className="pin-keypad">
          {digits.map((d, i) => (
            <button
              key={i}
              className={`pin-key ${d === null ? 'invisible' : ''} ${d === '⌫' ? 'backspace' : ''}`}
              onClick={() => {
                if (d === '⌫') handleBackspace();
                else if (d !== null) handleDigit(String(d));
              }}
              disabled={loading || d === null}
            >
              {d === null ? '' : d}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PinLock;
