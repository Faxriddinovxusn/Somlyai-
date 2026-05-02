import React, { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';

/**
 * EmptyState — premium bo'sh holat komponenti.
 * Har sahifa uchun o'ziga xos illustration, sarlavha, tavsif ko'rsatadi.
 */
export const EmptyState = ({ icon, title, subtitle, example, style = {} }) => (
  <div className="animate-fade-in" style={{ 
    textAlign: 'center', padding: '48px 24px', 
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    ...style
  }}>
    {/* Illustration Circle */}
    <div style={{ 
      width: '96px', height: '96px', borderRadius: '50%',
      background: 'rgba(255,255,255,0.03)', 
      border: '1px solid rgba(255,255,255,0.06)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      marginBottom: '24px', fontSize: '42px'
    }}>
      {icon || '📭'}
    </div>
    
    <h3 style={{ 
      fontSize: '18px', fontWeight: '700', color: '#fff', 
      marginBottom: '10px', letterSpacing: '-0.3px' 
    }}>
      {title}
    </h3>
    
    <p style={{ 
      fontSize: '14px', color: 'var(--text-secondary)', 
      lineHeight: '1.6', maxWidth: '280px', marginBottom: example ? '20px' : '0'
    }}>
      {subtitle}
    </p>

    {example && (
      <div style={{ 
        background: 'rgba(255,255,255,0.03)', 
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: '14px', padding: '14px 20px',
        fontSize: '14px', color: 'var(--text-secondary)',
        maxWidth: '280px', lineHeight: '1.5'
      }}>
        {example}
      </div>
    )}
  </div>
);


/**
 * ErrorState — server xatosi komponenti.
 * "Qayta urinish" tugmasi bilan.
 */
export const ErrorState = ({ onRetry, message }) => (
  <div className="animate-fade-in" style={{ 
    textAlign: 'center', padding: '48px 24px', 
    display: 'flex', flexDirection: 'column', alignItems: 'center'
  }}>
    <div style={{ 
      width: '80px', height: '80px', borderRadius: '50%',
      background: 'rgba(255,69,58,0.08)', 
      border: '1px solid rgba(255,69,58,0.15)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      marginBottom: '20px', fontSize: '36px'
    }}>
      ⚠️
    </div>
    
    <h3 style={{ 
      fontSize: '17px', fontWeight: '700', color: '#fff', 
      marginBottom: '8px' 
    }}>
      {message || "Xato yuz berdi"}
    </h3>
    
    <p style={{ 
      fontSize: '13px', color: 'var(--text-secondary)', 
      marginBottom: '24px', lineHeight: '1.5'
    }}>
      Serverga ulanib bo'lmadi. Internet aloqangizni tekshiring.
    </p>

    {onRetry && (
      <button onClick={onRetry} style={{ 
        display: 'flex', alignItems: 'center', gap: '8px',
        padding: '12px 28px', background: 'var(--primary)', 
        color: '#fff', border: 'none', borderRadius: '14px', 
        fontSize: '15px', fontWeight: '600', cursor: 'pointer'
      }}>
        <RefreshCw size={16} />
        Qayta urinish
      </button>
    )}
  </div>
);


/**
 * SkeletonPage — karta shaklida pulsating skeleton.
 * 0.5s kechikish, 2s dan keyin "Yuklanmoqda..." matni.
 */
export const SkeletonPage = ({ cards = 3 }) => {
  const [showSkeleton, setShowSkeleton] = useState(false);
  const [showText, setShowText] = useState(false);

  useEffect(() => {
    const t1 = setTimeout(() => setShowSkeleton(true), 500);
    const t2 = setTimeout(() => setShowText(true), 2000);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, []);

  if (!showSkeleton) return null;

  return (
    <div className="animate-fade-in" style={{ padding: '16px' }}>
      {/* Header skeleton */}
      <div className="flex-between" style={{ marginBottom: '24px' }}>
        <div className="skeleton" style={{ height: '32px', width: '140px', borderRadius: '8px' }}></div>
        <div className="skeleton" style={{ height: '32px', width: '32px', borderRadius: '50%' }}></div>
      </div>

      {/* Card skeletons */}
      {[...Array(cards)].map((_, i) => (
        <div key={i} className="skeleton" style={{ 
          height: i === 0 ? '160px' : '100px', 
          borderRadius: '20px', 
          marginBottom: '16px' 
        }}></div>
      ))}

      {/* Loading text */}
      {showText && (
        <div style={{ 
          textAlign: 'center', padding: '16px',
          animation: 'fadeIn 0.3s ease-out'
        }}>
          <p style={{ 
            fontSize: '14px', color: 'var(--text-secondary)', 
            fontWeight: '500'
          }}>
            Yuklanmoqda...
          </p>
        </div>
      )}
    </div>
  );
};


/**
 * OfflineBanner — sariq banner "📡 Offline rejim"
 */
export const OfflineBanner = () => (
  <div style={{ 
    background: 'linear-gradient(135deg, #F59E0B, #D97706)',
    color: '#000', padding: '10px 16px', 
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    gap: '8px', fontSize: '14px', fontWeight: '600',
    position: 'sticky', top: 0, zIndex: 50,
    borderRadius: '0 0 16px 16px'
  }}>
    📡 Offline rejim
  </div>
);
