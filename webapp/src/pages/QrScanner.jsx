import React, { useRef, useEffect, useState, useCallback } from 'react';
import jsQR from 'jsqr';
import { fetchApi } from '../utils/api';

const QrScanner = ({ onClose, onSuccess }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const [status, setStatus] = useState('loading'); // loading, scanning, found, error, result
  const [errorMsg, setErrorMsg] = useState('');
  const [receipt, setReceipt] = useState(null);
  const [saving, setSaving] = useState(false);
  const [category, setCategory] = useState('Oziq-ovqat');

  const categories = [
    { emoji: '🍔', label: 'Oziq-ovqat' },
    { emoji: '🛍', label: 'Xaridlar' },
    { emoji: '🏠', label: 'Uy-joy' },
    { emoji: '💊', label: 'Tibbiyot' },
    { emoji: '📦', label: 'Boshqa xarajatlar' },
  ];

  const getUserId = () => window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 0;

  const stopCamera = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
  }, []);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setStatus('scanning');
        scanLoop();
      }
    } catch (e) {
      console.error('Camera error:', e);
      setStatus('error');
      setErrorMsg('📷 Kamera ishlamadi.\nChek rasmini botga to\'g\'ridan-to\'g\'ri yuboring.');
    }
  }, []);

  const scanLoop = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState !== video.HAVE_ENOUGH_DATA) {
      animationRef.current = requestAnimationFrame(scanLoop);
      return;
    }

    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: 'dontInvert' });

    if (code && code.data) {
      // QR topildi!
      stopCamera();
      setStatus('found');
      handleQrFound(code.data);
      return;
    }

    animationRef.current = requestAnimationFrame(scanLoop);
  }, []);

  const handleQrFound = async (qrData) => {
    try {
      const res = await fetchApi('/qr-scan', {
        method: 'POST',
        body: JSON.stringify({ url: qrData, user_id: getUserId() })
      });

      if (res.error && !res.fiscal) {
        setStatus('error');
        setErrorMsg('Bu QR kod fiskal chek emas.\nFaqat O\'zbekiston fiskal cheklari qo\'llab-quvvatlanadi.');
        return;
      }

      if (!res.success || !res.total) {
        setStatus('error');
        setErrorMsg('⚠️ Chek ma\'lumotlari olinmadi.\nSummani qo\'lda kiriting.');
        return;
      }

      setReceipt(res);
      setStatus('result');
    } catch (e) {
      setStatus('error');
      setErrorMsg('📡 Xatolik yuz berdi.\nQayta urinib ko\'ring.');
    }
  };

  const handleSave = async () => {
    if (!receipt || saving) return;
    setSaving(true);
    try {
      const itemsCount = receipt.items?.length || 0;
      const shop = receipt.shop_name || "Do'kon";

      await fetchApi('/transactions', {
        method: 'POST',
        body: JSON.stringify({
          user_id: getUserId(),
          type: 'chiqim',
          amount: receipt.total,
          currency: 'UZS',
          category,
          description: `${shop} — ${itemsCount} ta mahsulot`,
          date: new Date().toISOString().split('T')[0],
          source: 'qr_scan',
          affects_balance: true
        })
      });

      if (onSuccess) onSuccess();
      if (onClose) onClose();
    } catch (e) {
      alert('Saqlashda xatolik: ' + e.message);
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  const formatNum = (n) => n ? n.toLocaleString('uz-UZ') : '0';

  // ── Error / Camera denied ──
  if (status === 'error') {
    return (
      <div style={overlayStyle}>
        <div style={modalStyle}>
          <div style={{ textAlign: 'center', padding: '40px 20px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📷</div>
            <p style={{ whiteSpace: 'pre-line', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{errorMsg}</p>
            <div style={{ display: 'flex', gap: '12px', marginTop: '24px', justifyContent: 'center' }}>
              <button onClick={() => { setStatus('loading'); startCamera(); }} style={btnSecondary}>🔄 Qayta urinish</button>
              <button onClick={onClose} style={btnPrimary}>Yopish</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Receipt Result ──
  if (status === 'result' && receipt) {
    return (
      <div style={overlayStyle}>
        <div style={{ ...modalStyle, maxHeight: '90vh', overflowY: 'auto' }}>
          <div style={{ padding: '24px 20px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '20px', fontWeight: 700 }}>🧾 Chek ma'lumotlari</h2>

            {receipt.shop_name && (
              <div style={infoRow}><span>🏪 Do'kon</span><strong>{receipt.shop_name}</strong></div>
            )}
            {receipt.date && (
              <div style={infoRow}><span>📅 Sana</span><strong>{receipt.date}</strong></div>
            )}
            <div style={infoRow}><span>💵 Jami</span><strong style={{color: '#FF453A'}}>{formatNum(receipt.total)} UZS</strong></div>

            {receipt.items?.length > 0 && (
              <div style={{ margin: '16px 0', background: 'var(--bg)', borderRadius: '12px', padding: '12px' }}>
                <p style={{ fontWeight: 600, marginBottom: '8px', fontSize: '14px' }}>Mahsulotlar:</p>
                {receipt.items.slice(0, 8).map((item, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: '13px' }}>
                    <span style={{color: 'var(--text-secondary)'}}>• {item.name}</span>
                    <span>{formatNum(item.price)} UZS</span>
                  </div>
                ))}
                {receipt.items.length > 8 && (
                  <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: '4px' }}>... va yana {receipt.items.length - 8} ta</p>
                )}
              </div>
            )}

            <div style={{ margin: '16px 0' }}>
              <p style={{ fontWeight: 600, marginBottom: '8px', fontSize: '14px' }}>Kategoriya:</p>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {categories.map(c => (
                  <button
                    key={c.label}
                    onClick={() => setCategory(c.label)}
                    style={{
                      padding: '8px 14px', borderRadius: '10px', fontSize: '13px',
                      border: category === c.label ? '2px solid var(--primary)' : '1px solid var(--border)',
                      background: category === c.label ? 'rgba(10,132,255,0.1)' : 'var(--bg)',
                      color: category === c.label ? 'var(--primary)' : 'var(--text-secondary)',
                      cursor: 'pointer', fontWeight: category === c.label ? 600 : 400
                    }}
                  >
                    {c.emoji} {c.label}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <button onClick={onClose} style={{ ...btnSecondary, flex: 1 }}>❌ Bekor</button>
              <button onClick={handleSave} disabled={saving} style={{ ...btnPrimary, flex: 2, opacity: saving ? 0.6 : 1 }}>
                {saving ? 'Saqlanmoqda...' : '✅ Saqlash'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Camera / Scanning ──
  return (
    <div style={overlayStyle}>
      <div style={{ position: 'relative', width: '100%', height: '100%' }}>
        <video ref={videoRef} style={{ width: '100%', height: '100%', objectFit: 'cover' }} playsInline muted />
        <canvas ref={canvasRef} style={{ display: 'none' }} />

        {/* Scanner overlay */}
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
        }}>
          {/* Scan frame */}
          <div style={{
            width: '250px', height: '250px', border: '3px solid rgba(255,255,255,0.8)',
            borderRadius: '20px', position: 'relative',
            boxShadow: '0 0 0 9999px rgba(0,0,0,0.5)'
          }}>
            {/* Corner accents */}
            <div style={{ ...cornerStyle, top: -3, left: -3, borderTop: '4px solid #0A84FF', borderLeft: '4px solid #0A84FF' }} />
            <div style={{ ...cornerStyle, top: -3, right: -3, borderTop: '4px solid #0A84FF', borderRight: '4px solid #0A84FF' }} />
            <div style={{ ...cornerStyle, bottom: -3, left: -3, borderBottom: '4px solid #0A84FF', borderLeft: '4px solid #0A84FF' }} />
            <div style={{ ...cornerStyle, bottom: -3, right: -3, borderBottom: '4px solid #0A84FF', borderRight: '4px solid #0A84FF' }} />

            {/* Scan line animation */}
            <div style={{
              position: 'absolute', left: '10%', right: '10%', height: '2px',
              background: 'linear-gradient(90deg, transparent, #0A84FF, transparent)',
              animation: 'scanLine 2s ease-in-out infinite',
              top: '50%'
            }} />
          </div>

          <p style={{ color: '#fff', marginTop: '24px', fontSize: '16px', fontWeight: 500, textShadow: '0 1px 4px rgba(0,0,0,0.5)' }}>
            {status === 'loading' ? '⏳ Kamera ochilmoqda...' : status === 'found' ? '✅ QR topildi!' : '📷 Chekni ramkaga joylashtiring'}
          </p>
        </div>

        {/* Close button */}
        <button onClick={() => { stopCamera(); onClose(); }} style={{
          position: 'absolute', top: '16px', right: '16px', width: '44px', height: '44px',
          borderRadius: '22px', background: 'rgba(0,0,0,0.5)', border: 'none',
          color: '#fff', fontSize: '20px', cursor: 'pointer', backdropFilter: 'blur(10px)'
        }}>✕</button>
      </div>

      <style>{`
        @keyframes scanLine {
          0%, 100% { top: 10%; }
          50% { top: 85%; }
        }
      `}</style>
    </div>
  );
};

/* ═══ Styles ═══ */
const overlayStyle = {
  position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
  background: '#000', zIndex: 9999, display: 'flex',
  alignItems: 'center', justifyContent: 'center'
};

const modalStyle = {
  background: 'var(--card, #1c1c1e)', borderRadius: '24px',
  width: '90%', maxWidth: '400px'
};

const infoRow = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  padding: '10px 0', borderBottom: '1px solid var(--border, #333)'
};

const btnPrimary = {
  padding: '14px 24px', background: 'var(--primary, #0A84FF)', color: '#fff',
  border: 'none', borderRadius: '14px', fontSize: '15px', fontWeight: 600, cursor: 'pointer'
};

const btnSecondary = {
  padding: '14px 24px', background: 'var(--bg, #2c2c2e)', color: 'var(--text, #fff)',
  border: '1px solid var(--border, #444)', borderRadius: '14px', fontSize: '15px', cursor: 'pointer'
};

const cornerStyle = {
  position: 'absolute', width: '30px', height: '30px', borderRadius: '4px'
};

export default QrScanner;
