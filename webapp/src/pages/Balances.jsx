import React, { useState, useEffect } from 'react';
import { Plus, MoreVertical, Flag } from 'lucide-react';

const BalancesPage = ({ initData }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [balances, setBalances] = useState([]);

  useEffect(() => {
    setTimeout(() => {
      setBalances([
        { id: 1, currency: 'UZS', title: "So'm", amount: 4310000, income: 4310000, expense: 0, limit: null }
      ]);
      setLoading(false);
    }, 800);
  }, []);

  if (loading) {
    return (
      <div className="animate-fade-in">
        <h1 className="title">Balanslar</h1>
        <div className="skeleton" style={{ height: '140px', marginTop: '20px' }}></div>
        <div className="skeleton" style={{ height: '140px', marginTop: '16px' }}></div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <h1 className="title" style={{ marginBottom: '24px' }}>Balanslar</h1>

      {balances.map(b => (
        <div key={b.id} className="card" style={{ padding: '20px' }}>
          <div className="flex-between">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '24px' }}>{b.currency === 'UZS' ? '🇺🇿' : '🇺🇸'}</span>
              <span style={{ fontSize: '18px', fontWeight: '600' }}>{b.title}</span>
            </div>
            <MoreVertical className="text-secondary" />
          </div>

          <h2 style={{ fontSize: '28px', fontWeight: '800', margin: '16px 0' }}>
            {b.amount.toLocaleString()} {b.currency}
          </h2>

          <div className="flex-between" style={{ marginTop: '16px' }}>
            <div>
              <p style={{ fontSize: '13px', color: 'var(--success)' }}>&darr; Kirim</p>
              <p style={{ fontWeight: '600', fontSize: '15px' }}>{b.income.toLocaleString()}</p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p style={{ fontSize: '13px', color: 'var(--danger)' }}>&uarr; Chiqim</p>
              <p style={{ fontWeight: '600', fontSize: '15px' }}>{b.expense.toLocaleString()}</p>
            </div>
          </div>

          {/* Limit Progress Bar */}
          {b.limit && (
            <div style={{ marginTop: '20px' }}>
              <div className="flex-between" style={{ marginBottom: '8px', fontSize: '13px' }}>
                <span className="text-secondary">Limit: {b.limit.toLocaleString()}</span>
                <span style={{ color: 'var(--warning)', fontWeight: 600 }}>
                  {Math.round((b.limitUsed / b.limit) * 100)}%
                </span>
              </div>
              <div style={{ width: '100%', height: '6px', backgroundColor: 'var(--border)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ 
                  width: `${(b.limitUsed / b.limit) * 100}%`, 
                  height: '100%', 
                  backgroundColor: 'var(--warning)',
                  borderRadius: '3px'
                }}></div>
              </div>
            </div>
          )}
        </div>
      ))}

      {/* Floating Action Button */}
      <button 
        onClick={() => setIsModalOpen(true)}
        style={{
          position: 'fixed', bottom: '100px', right: '20px',
          width: '56px', height: '56px', borderRadius: '28px',
          backgroundColor: 'var(--primary)', color: 'white',
          border: 'none', boxShadow: '0 4px 12px rgba(10, 132, 255, 0.4)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', zIndex: 90
        }}
      >
        <Plus size={28} />
      </button>

      {/* Add Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h2 className="title" style={{ fontSize: '22px' }}>Yangi balans qo'shish</h2>
            
            <label style={{ display: 'block', marginTop: '20px', fontWeight: 500 }}>Sarlavha</label>
            <input type="text" className="input-field" placeholder="Masalan: So'm" />

            <label style={{ display: 'block', marginTop: '16px', fontWeight: 500 }}>Miqdor</label>
            <input type="number" className="input-field" placeholder="0" />

            <div className="flex-between" style={{ marginTop: '24px' }}>
              <button onClick={() => setIsModalOpen(false)} style={{ flex: 1, padding: '14px', background: 'transparent', border: 'none', color: 'var(--text-primary)', fontSize: '16px' }}>Bekor qilish</button>
              <button style={{ flex: 1 }} className="btn-primary">Qo'shish</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BalancesPage;
