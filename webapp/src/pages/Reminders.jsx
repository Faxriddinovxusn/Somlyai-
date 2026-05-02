import React, { useState, useEffect } from 'react';
import { Bell, Clock, CheckCircle, XCircle, Edit2, Archive, Trash2, Calendar } from 'lucide-react';
import { fetchApi } from '../utils/api';
import { useTranslation } from 'react-i18next';
import PageHeader from '../components/PageHeader';

const RemindersPage = ({ initData }) => {
  const [reminders, setReminders] = useState([]);
  const [archive, setArchive] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('active'); // 'active' or 'archive'
  const { t } = useTranslation();

  const loadReminders = async () => {
    setLoading(true);
    try {
      const activeData = await fetchApi('/reminders?status=pending');
      const archiveData = await fetchApi('/reminders?status=archive');
      setReminders(activeData || []);
      setArchive(archiveData || []);
    } catch (err) {
      console.error('Failed to load reminders', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReminders();
  }, []);

  const handleStatusChange = async (id, status) => {
    try {
      await fetchApi(`/reminders/${id}/status`, {
        method: 'POST',
        body: JSON.stringify({ status })
      });
      loadReminders();
    } catch (err) {
      console.error('Failed to update status', err);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Eslatmani o\'chirasizmi?')) {
      try {
        await fetchApi(`/reminders/${id}`, { method: 'DELETE' });
        loadReminders();
      } catch (err) {
        console.error('Failed to delete reminder', err);
      }
    }
  };

  const formatDateTime = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleString('uz-UZ', {
      day: 'numeric',
      month: 'long',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const currentList = activeTab === 'active' ? reminders : archive;

  return (
    <div className="page-container" style={{ padding: '20px', paddingBottom: '100px' }}>
      <header style={{ marginBottom: '24px' }}>
        <PageHeader title="Eslatmalar" showLogo={true} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          Vaqtida bajarilishi kerak bo'lgan ishlar ro'yxati
        </p>
      </header>

      {/* Tabs */}
      <div style={{ 
        display: 'flex', 
        background: 'rgba(255,255,255,0.05)', 
        borderRadius: '12px', 
        padding: '4px',
        marginBottom: '20px'
      }}>
        <button 
          onClick={() => setActiveTab('active')}
          style={{
            flex: 1,
            padding: '10px',
            borderRadius: '10px',
            border: 'none',
            background: activeTab === 'active' ? 'var(--primary)' : 'transparent',
            color: activeTab === 'active' ? '#fff' : 'var(--text-secondary)',
            fontWeight: 600,
            transition: '0.3s'
          }}
        >
          Faol
        </button>
        <button 
          onClick={() => setActiveTab('archive')}
          style={{
            flex: 1,
            padding: '10px',
            borderRadius: '10px',
            border: 'none',
            background: activeTab === 'archive' ? 'var(--primary)' : 'transparent',
            color: activeTab === 'archive' ? '#fff' : 'var(--text-secondary)',
            fontWeight: 600,
            transition: '0.3s'
          }}
        >
          Arxiv
        </button>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <div className="spinner"></div>
        </div>
      ) : currentList.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-secondary)' }}>
          <div style={{ marginBottom: '16px', opacity: 0.5 }}>
            {activeTab === 'active' ? <Clock size={48} /> : <Archive size={48} />}
          </div>
          <p>{activeTab === 'active' ? 'Hozircha faol eslatmalar yo\'q' : 'Arxiv bo\'sh'}</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {currentList.map((rem) => (
            <div key={rem.id} className="glass-card" style={{ 
              padding: '16px', 
              borderRadius: '16px',
              border: '1px solid rgba(255,255,255,0.1)',
              background: 'rgba(255,255,255,0.03)',
              position: 'relative',
              overflow: 'hidden'
            }}>
              {/* Type Indicator */}
              <div style={{ 
                position: 'absolute', 
                top: 0, 
                left: 0, 
                width: '4px', 
                height: '100%', 
                background: rem.type === 'financial' ? 'var(--warning)' : 'var(--primary)' 
              }}></div>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', fontSize: '12px' }}>
                  <Calendar size={14} />
                  {formatDateTime(rem.scheduled_time)}
                </div>
                {activeTab === 'active' && (
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button onClick={() => handleDelete(rem.id)} style={{ background: 'none', border: 'none', color: 'var(--danger)', opacity: 0.7 }}>
                      <Trash2 size={16} />
                    </button>
                  </div>
                )}
              </div>

              <p style={{ fontSize: '16px', fontWeight: 500, marginBottom: '16px', color: '#fff' }}>
                {rem.message}
              </p>

              {activeTab === 'active' && (
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button 
                    onClick={() => handleStatusChange(rem.id, 'done')}
                    style={{ 
                      flex: 1, 
                      padding: '8px', 
                      borderRadius: '8px', 
                      border: 'none', 
                      background: 'rgba(16, 185, 129, 0.1)', 
                      color: '#10B981',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '6px',
                      fontSize: '13px',
                      fontWeight: 600
                    }}
                  >
                    <CheckCircle size={16} /> Bajarildi
                  </button>
                  <button 
                    onClick={() => handleStatusChange(rem.id, 'cancelled')}
                    style={{ 
                      flex: 1, 
                      padding: '8px', 
                      borderRadius: '8px', 
                      border: 'none', 
                      background: 'rgba(239, 68, 68, 0.1)', 
                      color: '#EF4444',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '6px',
                      fontSize: '13px',
                      fontWeight: 600
                    }}
                  >
                    <XCircle size={16} /> Bekor
                  </button>
                </div>
              )}

              {activeTab === 'archive' && (
                <div style={{ 
                  fontSize: '12px', 
                  color: rem.status === 'done' ? '#10B981' : '#EF4444',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  {rem.status === 'done' ? <CheckCircle size={14} /> : <XCircle size={14} />}
                  {rem.status === 'done' ? 'Bajarilgan' : 'Bekor qilingan'}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RemindersPage;
