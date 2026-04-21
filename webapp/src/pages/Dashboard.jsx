import React, { useState, useEffect } from 'react';
import { Plus, ArrowUpRight, ArrowDownRight, Handshake, ChevronRight } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const DashboardPage = ({ initData }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mock data for initial UI build
  useEffect(() => {
    setTimeout(() => {
      setData({
        balances: [
          { currency: 'UZS', amount: 4310000 }
        ],
        stats: [
          { name: 'Kirim', value: 4310000, color: 'var(--success)' },
          { name: 'Chiqim', value: 1200000, color: 'var(--danger)' },
          { name: 'Qarz', value: 300000, color: 'var(--warning)' }
        ],
        debts: {
          berishimKerak: 150000,
          olishimKerak: 450000
        },
        transactions: [
          { id: 1, type: 'chiqim', amount: 45000, category: '🍔 Ovqat', date: 'Bugun, 14:30' },
          { id: 2, type: 'kirim', amount: 4000000, category: '💼 Maosh', date: 'Bugun, 09:00' },
          { id: 3, type: 'qarz', amount: 100000, category: '🤝 Jasur', date: 'Kecha, 18:00' },
        ]
      });
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return (
      <div className="animate-fade-in">
        <div className="skeleton" style={{ height: '120px', marginBottom: '24px' }}></div>
        <div className="flex-between" style={{ gap: '16px', marginBottom: '24px' }}>
          <div className="skeleton" style={{ height: '60px', flex: 1 }}></div>
          <div className="skeleton" style={{ height: '60px', flex: 1 }}></div>
        </div>
        <div className="skeleton" style={{ height: '200px', marginBottom: '24px' }}></div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* Top Balance */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #1C1C1E 0%, #2C2C2E 100%)' }}>
        <p className="subtitle" style={{ color: '#EBEBF5' }}>Umumiy balans</p>
        <h1 style={{ fontSize: '36px', fontWeight: '800', margin: '8px 0', color: 'var(--success)' }}>
          {data.balances[0].amount.toLocaleString()} <span style={{ fontSize: '20px' }}>UZS</span>
        </h1>
      </div>

      {/* Quick Actions */}
      <div className="flex-between" style={{ gap: '16px', marginBottom: '24px' }}>
        <button className="card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '16px', border: 'none', color: 'var(--primary)' }}>
          <Plus size={20} />
          <span style={{ fontWeight: 600 }}>Yangi balans</span>
        </button>
        <button className="card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '16px', border: 'none', color: 'var(--text-primary)' }}>
          <Plus size={20} />
          <span style={{ fontWeight: 600 }}>Tranzaksiya</span>
        </button>
      </div>

      {/* Stats Widget */}
      <div className="card">
        <div className="flex-between" style={{ marginBottom: '16px' }}>
          <h2 className="title" style={{ fontSize: '20px', margin: 0 }}>Statistika</h2>
          <ChevronRight size={20} className="text-secondary" />
        </div>
        <div style={{ height: '160px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data.stats}
                innerRadius={50}
                outerRadius={70}
                paddingAngle={5}
                dataKey="value"
              >
                {data.stats.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex-between" style={{ marginTop: '16px' }}>
          {data.stats.map(s => (
            <div key={s.name} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: s.color }}></div>
              <span className="subtitle" style={{ fontSize: '14px' }}>{s.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Debts Widget */}
      <div className="card">
        <div className="flex-between" style={{ marginBottom: '16px' }}>
          <h2 className="title" style={{ fontSize: '20px', margin: 0 }}>Qarzlar</h2>
          <span style={{ color: 'var(--primary)', fontSize: '14px', fontWeight: 500 }}>Barchasi &rarr;</span>
        </div>
        <div className="flex-between" style={{ gap: '12px' }}>
          <div style={{ flex: 1, background: 'rgba(239, 68, 58, 0.1)', padding: '12px', borderRadius: '12px' }}>
            <p style={{ fontSize: '12px', color: 'var(--danger)' }}>Berishim kerak</p>
            <p style={{ fontWeight: 'bold', marginTop: '4px' }}>{data.debts.berishimKerak.toLocaleString()} UZS</p>
          </div>
          <div style={{ flex: 1, background: 'rgba(48, 209, 88, 0.1)', padding: '12px', borderRadius: '12px' }}>
            <p style={{ fontSize: '12px', color: 'var(--success)' }}>Olishim kerak</p>
            <p style={{ fontWeight: 'bold', marginTop: '4px' }}>{data.debts.olishimKerak.toLocaleString()} UZS</p>
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <h2 className="title" style={{ fontSize: '20px', marginTop: '24px' }}>Bugun</h2>
      {data.transactions.map(t => (
        <div key={t.id} className="card flex-between" style={{ padding: '16px', marginBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ 
              width: '40px', height: '40px', borderRadius: '12px', 
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              backgroundColor: t.type === 'kirim' ? 'rgba(48, 209, 88, 0.1)' : 
                               t.type === 'chiqim' ? 'rgba(239, 68, 58, 0.1)' : 'rgba(255, 159, 10, 0.1)'
            }}>
              {t.type === 'kirim' ? <ArrowDownRight color="var(--success)" /> : 
               t.type === 'chiqim' ? <ArrowUpRight color="var(--danger)" /> : 
               <Handshake color="var(--warning)" />}
            </div>
            <div>
              <p style={{ fontWeight: '600', fontSize: '16px' }}>{t.category}</p>
              <p className="subtitle" style={{ fontSize: '13px', marginTop: '2px' }}>{t.date}</p>
            </div>
          </div>
          <p style={{ 
            fontWeight: '700', 
            color: t.type === 'kirim' ? 'var(--success)' : 
                   t.type === 'chiqim' ? 'var(--text-primary)' : 'var(--warning)'
          }}>
            {t.type === 'chiqim' ? '-' : '+'}{t.amount.toLocaleString()} UZS
          </p>
        </div>
      ))}
    </div>
  );
};

export default DashboardPage;
