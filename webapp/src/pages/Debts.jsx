import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, MoreVertical, Calendar, ChevronRight, X, Check, Clock, Trash2, RefreshCw } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { fetchApi, showToast } from '../utils/api';
import { EmptyState, ErrorState, SkeletonPage } from '../components/StateViews';
import PageHeader from '../components/PageHeader';

const DebtsPage = ({ initData }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('give'); // 'give' or 'receive'
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  
  // Modals
  const [activeModal, setActiveModal] = useState(null); // 'action', 'date'
  const [selectedDebt, setSelectedDebt] = useState(null);
  
  const [debts, setDebts] = useState({
    berishimKerak: [],
    olishimKerak: []
  });
  
  const [summary, setSummary] = useState({
    berishimKerak: 0,
    olishimKerak: 0
  });

  const loadDebts = async (isBackground = false) => {
    if (!isBackground) setLoading(true);
    try {
      const response = await fetchApi('/debts');
      if (response && !response.error) {
        setDebts({
          berishimKerak: response.berishimKerak || [],
          olishimKerak: response.olishimKerak || []
        });
        setSummary({
          berishimKerak: (response.berishimKerak || []).reduce((sum, d) => sum + d.amount, 0),
          olishimKerak: (response.olishimKerak || []).reduce((sum, d) => sum + d.amount, 0)
        });
        setError(false);
      }
    } catch (err) {
      if (err.message !== 'OFFLINE') setError(true);
    } finally {
      if (!isBackground) setLoading(false);
      setRefreshing(false);
    }
  };

  // Animation tracking
  const [fadingOutIds, setFadingOutIds] = useState(new Set());
  const [newDebtIds, setNewDebtIds] = useState(new Set());
  const prevDebtIdsRef = useRef(new Set());

  const handleWsEvent = useCallback(() => loadDebts(true), []);

  useEffect(() => {
    loadDebts();

    const events = [
      'ws_debt.created', 'ws_debt.updated', 'ws_debt.paid',
      'ws_connected', 'ws_sync'
    ];
    events.forEach(e => window.addEventListener(e, handleWsEvent));
    return () => events.forEach(e => window.removeEventListener(e, handleWsEvent));
  }, [handleWsEvent]);

  // Detect new debt IDs for slide-down animation
  useEffect(() => {
    const allDebts = [...debts.berishimKerak, ...debts.olishimKerak];
    if (!allDebts.length) return;
    const currentIds = new Set(allDebts.map(d => d.id));
    const added = new Set();
    currentIds.forEach(id => {
      if (!prevDebtIdsRef.current.has(id)) added.add(id);
    });
    if (added.size > 0 && prevDebtIdsRef.current.size > 0) {
      setNewDebtIds(added);
      setTimeout(() => setNewDebtIds(new Set()), 500);
    }
    prevDebtIdsRef.current = currentIds;
  }, [debts]);

  const getBorderColor = (debt) => {
    if (!debt.due_date || debt.due_date === 'nomalum') return '1px solid #2C2C2E';
    
    const due = new Date(debt.due_date);
    const today = new Date();
    today.setHours(0,0,0,0);
    due.setHours(0,0,0,0);
    
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return '1px solid var(--danger)';
    if (diffDays === 0) return '1px solid #FFD60A';
    if (diffDays <= 3) return '1px solid #FF9F0A';
    
    return '1px solid #2C2C2E';
  };

  const currentDebts = debts[activeTab === 'give' ? 'berishimKerak' : 'olishimKerak']
    .filter(d => (d.name || '').toLowerCase().includes(searchQuery.toLowerCase()));

  const handleAction = (debt) => {
    setSelectedDebt(debt);
    setActiveModal('action');
  };

  const markAsPaid = async () => {
    if (!selectedDebt) return;
    const debtId = selectedDebt.id;
    const debtName = selectedDebt.name;
    const debtAmount = selectedDebt.amount;
    const debtCurrency = selectedDebt.currency;
    setActiveModal(null);
    
    // Start fade-out animation first
    setFadingOutIds(prev => new Set([...prev, debtId]));
    
    try {
      await fetchApi(`/debts/${debtId}/pay`, { method: 'POST' });
      
      const msg = activeTab === 'give' 
        ? `✅ ${debtName}ga ${debtAmount.toLocaleString()} ${debtCurrency} qaytarildi!`
        : `✅ ${debtName}dan ${debtAmount.toLocaleString()} ${debtCurrency} qaytdi!`;
      
      showToast(msg, 'success');
      
      // After animation completes, reload
      setTimeout(() => {
        setFadingOutIds(prev => { const s = new Set(prev); s.delete(debtId); return s; });
        loadDebts(false);
      }, 450);
    } catch (e) {
      setFadingOutIds(prev => { const s = new Set(prev); s.delete(debtId); return s; });
      console.error(e);
      showToast("Xato yuz berdi", "error");
    }
  };

  const handleDelete = async () => {
    if (!selectedDebt) return;
    const debtId = selectedDebt.id;
    setActiveModal(null);
    
    setFadingOutIds(prev => new Set([...prev, debtId]));
    
    try {
      await fetchApi(`/debts/${debtId}/delete`, { method: 'POST' });
      showToast("✅ Qarz o'chirildi", "success");
      setTimeout(() => {
        setFadingOutIds(prev => { const s = new Set(prev); s.delete(debtId); return s; });
        loadDebts(false);
      }, 450);
    } catch (e) {
      setFadingOutIds(prev => { const s = new Set(prev); s.delete(debtId); return s; });
      console.error(e);
      showToast("Xato yuz berdi", "error");
    }
  };

  if (loading) {
    return <SkeletonPage cards={3} />;
  }

  if (error && debts.berishimKerak.length === 0 && debts.olishimKerak.length === 0) {
    return <ErrorState onRetry={() => loadDebts()} />;
  }

  return (
    <div className="animate-fade-in" style={{ padding: '0 16px 100px' }}>
      {refreshing && (
        <div style={{ textAlign: 'center', padding: '10px', color: 'var(--text-secondary)' }}>
          <RefreshCw className="animate-spin" size={24} style={{ margin: '0 auto' }} />
        </div>
      )}
      {/* Header */}
      <div className="flex-between" style={{ padding: '16px 0', position: 'sticky', top: 0, background: 'var(--bg)', zIndex: 10 }}>
        {!isSearchOpen ? (
          <div style={{ width: '100%' }}>
            <PageHeader 
              title={t('debts.title')} 
              showLogo={true} 
              rightElement={
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button onClick={() => setIsSearchOpen(true)} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '50%', width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-primary)' }}>
                    <Search size={20} />
                  </button>
                  <button style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '50%', width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-primary)' }}>
                    <MoreVertical size={20} />
                  </button>
                </div>
              }
            />
          </div>
        ) : (
          <div style={{ display: 'flex', width: '100%', gap: '12px', alignItems: 'center' }}>
            <div style={{ flex: 1, position: 'relative' }}>
              <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
              <input 
                type="text" 
                autoFocus
                placeholder="Ism bo'yicha qidirish..." 
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                style={{ width: '100%', background: 'var(--card)', border: '1px solid var(--border)', color: '#FFF', padding: '10px 10px 10px 36px', borderRadius: '12px', outline: 'none' }}
              />
            </div>
            <button onClick={() => { setIsSearchOpen(false); setSearchQuery(''); }} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)' }}>
              Bekor
            </button>
          </div>
        )}
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <div style={{ flex: 1, background: 'rgba(239, 68, 58, 0.1)', border: '1px solid rgba(239, 68, 58, 0.2)', padding: '16px', borderRadius: '16px' }}>
          <p style={{ fontSize: '13px', color: 'var(--danger)', fontWeight: '600', marginBottom: '8px' }}>{t('debts.i_should_give')}</p>
          <p style={{ fontWeight: '800', fontSize: '18px', color: '#FFF' }}>{summary.berishimKerak.toLocaleString()} UZS</p>
        </div>
        <div style={{ flex: 1, background: 'rgba(48, 209, 88, 0.1)', border: '1px solid rgba(48, 209, 88, 0.2)', padding: '16px', borderRadius: '16px' }}>
          <p style={{ fontSize: '13px', color: 'var(--success)', fontWeight: '600', marginBottom: '8px' }}>{t('debts.i_should_receive')}</p>
          <p style={{ fontWeight: '800', fontSize: '18px', color: '#FFF' }}>{summary.olishimKerak.toLocaleString()} UZS</p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', background: 'var(--card)', padding: '4px', borderRadius: '12px', marginBottom: '24px' }}>
        {[
          { id: 'give', label: t('debts.i_should_give') },
          { id: 'receive', label: t('debts.i_should_receive') }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              flex: 1, padding: '10px 0', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', transition: '0.2s',
              background: activeTab === tab.id ? (tab.id === 'give' ? 'var(--danger)' : 'var(--success)') : 'transparent',
              color: activeTab === tab.id ? '#FFF' : 'var(--text-secondary)'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* List */}
      <div>
        {currentDebts.length === 0 ? (
          <EmptyState 
            icon="🤝" 
            title="Qarzlar yo'q" 
            subtitle={"Kimga qarz berib, kimdan olishingizni bu yerda kuzating!"}
            example={<span>💬 Botga yozing: <strong>"Jasurga 100 ming berdim"</strong></span>}
          />
        ) : (
          currentDebts.map(d => {
            const isOlishim = activeTab === 'receive';
            return (
              <div 
                key={d.id}
                className={fadingOutIds.has(d.id) ? 'fade-out-shrink' : (newDebtIds.has(d.id) ? 'slide-down-enter' : '')}
                style={{ 
                  background: 'var(--card)', borderRadius: '16px', padding: '16px', marginBottom: '12px', 
                  border: getBorderColor(d) 
                }}
              >
                <div className="flex-between" style={{ marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' }}>
                      👤
                    </div>
                    <span style={{ fontSize: '16px', fontWeight: '600' }}>{d.name}</span>
                  </div>
                  <button onClick={() => handleAction(d)} style={{ background: 'var(--bg)', border: 'none', width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-primary)' }}>
                    <MoreVertical size={18} />
                  </button>
                </div>
                
                <h3 style={{ fontSize: '24px', fontWeight: 'bold', margin: '0 0 16px', color: isOlishim ? 'var(--success)' : 'var(--danger)' }}>
                  {isOlishim ? '+' : '-'} {d.amount.toLocaleString()} <span style={{ fontSize: '14px', fontWeight: '600' }}>{d.currency}</span>
                </h3>
                
                <div className="flex-between">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{d.desc}</span>
                  </div>
                  {d.due_date && d.due_date !== 'nomalum' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--bg)', padding: '4px 8px', borderRadius: '8px' }}>
                      <Calendar size={14} color="var(--text-secondary)" />
                      <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-primary)' }}>
                        {new Date(d.due_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })}
                      </span>
                    </div>
                  )}
                </div>
                <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid var(--border)', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Qarzlar • So'm
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Action Modal */}
      {activeModal === 'action' && selectedDebt && (
        <div className="modal-overlay" onClick={() => setActiveModal(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ paddingBottom: '30px' }}>
            <div className="flex-between" style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>
                  👤
                </div>
                <div>
                  <h3 style={{ fontSize: '18px', fontWeight: 'bold' }}>{selectedDebt.name}</h3>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{activeTab === 'give' ? t('debts.i_should_give') : t('debts.i_should_receive')}</p>
                </div>
              </div>
              <button onClick={() => setActiveModal(null)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)' }}><X size={20} /></button>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <button onClick={markAsPaid} className="card flex-between" style={{ padding: '16px', background: 'rgba(48, 209, 88, 0.1)', border: '1px solid rgba(48, 209, 88, 0.2)', marginBottom: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Check size={20} color="var(--success)" />
                  <span style={{ fontWeight: '600', color: 'var(--success)', fontSize: '16px' }}>Qaytdi</span>
                </div>
                <ChevronRight size={20} color="var(--success)" />
              </button>
              
              <button onClick={() => setActiveModal('date')} className="card flex-between" style={{ padding: '16px', background: 'var(--bg)', border: '1px solid var(--border)', marginBottom: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Clock size={20} color="var(--warning)" />
                  <span style={{ fontWeight: '600', fontSize: '16px' }}>Muddatni uzaytirish</span>
                </div>
                <ChevronRight size={20} color="var(--text-secondary)" />
              </button>
              
              <button onClick={handleDelete} className="card flex-between" style={{ padding: '16px', background: 'rgba(255, 69, 58, 0.05)', border: '1px solid rgba(255, 69, 58, 0.2)', marginBottom: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Trash2 size={20} color="var(--danger)" />
                  <span style={{ fontWeight: '600', color: 'var(--danger)', fontSize: '16px' }}>O'chirish</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Date Picker Modal (Simulation) */}
      {activeModal === 'date' && (
        <div className="modal-overlay" onClick={() => setActiveModal('action')}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '20px', textAlign: 'center' }}>Muddatni tanlang</h3>
            <input type="date" style={{ width: '100%', padding: '16px', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '12px', color: '#FFF', fontSize: '18px', outline: 'none', marginBottom: '24px' }} defaultValue={selectedDebt?.due_date || selectedDebt?.date?.split('T')[0]} />
            <button onClick={() => { showToast('✅ Muddat uzaytirildi', 'success'); setActiveModal(null); }} style={{ width: '100%', padding: '16px', background: 'var(--primary)', color: '#FFF', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: 'bold' }}>
              Saqlash
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DebtsPage;
