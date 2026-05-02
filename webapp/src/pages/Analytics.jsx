import React, { useState, useEffect, useCallback } from 'react';
import { ExternalLink, RefreshCw } from 'lucide-react';
import { fetchApi } from '../utils/api';
import PageHeader from '../components/PageHeader';

const AnalyticsPage = ({ initData }) => {
  const [loading, setLoading] = useState(true);
  const [channels, setChannels] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadChannels = async (bg = false) => {
    if (!bg) setLoading(true);
    try {
      const res = await fetchApi('/channels');
      if (res && !res.error) {
        setChannels(Array.isArray(res) ? res : []);
      }
    } catch (err) {
      if (err.message !== 'OFFLINE') window.dispatchEvent(new Event('api_server_error'));
    } finally {
      if (!bg) setLoading(false);
      setRefreshing(false);
    }
  };

  const handleWsEvent = useCallback(() => loadChannels(true), []);

  useEffect(() => {
    loadChannels();
    const events = ['ws_connected', 'ws_sync'];
    events.forEach(e => window.addEventListener(e, handleWsEvent));
    return () => events.forEach(e => window.removeEventListener(e, handleWsEvent));
  }, [handleWsEvent]);

  const openChannel = (link) => {
    if (window.Telegram?.WebApp?.openTelegramLink && link.includes('t.me')) {
      window.Telegram.WebApp.openTelegramLink(link);
    } else {
      window.open(link, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="animate-fade-in" style={{ padding: '16px' }}>
        <div className="skeleton" style={{ height: '40px', borderRadius: '12px', marginBottom: '24px' }}></div>
        <div className="skeleton" style={{ height: '100px', borderRadius: '16px', marginBottom: '16px' }}></div>
        <div className="skeleton" style={{ height: '100px', borderRadius: '16px', marginBottom: '16px' }}></div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ padding: '0 16px 100px' }}>
      {refreshing && (
        <div style={{ textAlign: 'center', padding: '10px', color: 'var(--text-secondary)' }}>
          <RefreshCw className="animate-spin" size={24} style={{ margin: '0 auto' }} />
        </div>
      )}
      
      {/* HEADER */}
      <div style={{ marginBottom: '24px', paddingTop: '16px' }}>
        <PageHeader title="Tavsiyalar" showLogo={true} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.5' }}>
          Biz tavsiya etgan foydali kanallarga obuna bo'ling va eng so'nggi yangiliklardan xabardor bo'ling.
        </p>
      </div>

      {/* CHANNELS LIST */}
      <div>
        {channels.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 20px', background: 'var(--card)', borderRadius: '24px', border: '1px dashed var(--border)' }}>
            <p style={{ color: 'var(--text-secondary)' }}>Hozircha tavsiya etilgan kanallar yo'q.</p>
          </div>
        ) : (
          channels.map((channel, idx) => (
            <div key={idx} style={{ 
              background: 'var(--card)', 
              borderRadius: '20px', 
              padding: '20px', 
              marginBottom: '16px', 
              border: '1px solid var(--border)',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ 
                  width: '56px', height: '56px', borderRadius: '16px', 
                  background: 'linear-gradient(135deg, var(--primary), #5AC8FA)', 
                  display: 'flex', alignItems: 'center', justifyContent: 'center', 
                  color: '#fff', fontSize: '24px', flexShrink: 0 
                }}>
                  📢
                </div>
                <div>
                  <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '4px', color: 'var(--text-primary)' }}>{channel.name}</h3>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{channel.description || 'Somly AI tavsiya etadi'}</p>
                </div>
              </div>
              
              <button 
                onClick={() => openChannel(channel.link)}
                style={{ 
                  width: '100%', padding: '14px', 
                  background: 'rgba(10, 132, 255, 0.1)', 
                  color: 'var(--primary)', 
                  border: '1px solid rgba(10, 132, 255, 0.2)', 
                  borderRadius: '12px', 
                  fontSize: '15px', fontWeight: 'bold', 
                  cursor: 'pointer', 
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                  transition: '0.2s'
                }}
              >
                Obuna bo'lish <ExternalLink size={18} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AnalyticsPage;
