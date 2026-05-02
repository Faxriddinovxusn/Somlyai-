import React, { useState, useEffect } from 'react';
import { Target, AlertTriangle, TrendingUp } from 'lucide-react';
import { fetchApi } from '../utils/api';
import { useNavigate } from 'react-router-dom';

const SmartWidgets = ({ data }) => {
  const navigate = useNavigate();
  const limit = data?.user?.monthly_limit || 0;
  const expense = data?.user?.monthly_expense || 0;
  const percent = limit > 0 ? Math.min(100, Math.round((expense / limit) * 100)) : 0;
  const remaining = Math.max(0, limit - expense);

  const debts = data?.debts || { berishimKerak: 0, olishimKerak: 0, list: [] };
  const upcomingDebts = debts.list?.filter(d => {
    if (!d.due_date || d.status !== 'pending') return false;
    const due = new Date(d.due_date);
    const today = new Date();
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays >= 0 && diffDays <= 3;
  }) || [];

  const [trendData, setTrendData] = useState([]);
  
  useEffect(() => {
    const fetchTrend = async () => {
      try {
        const res = await fetchApi('/dashboard/trend');
        if (res && !res.error) setTrendData(res);
      } catch (e) {
        console.error(e);
      }
    };
    fetchTrend();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '24px', marginBottom: '24px' }}>
      
      {/* 🎯 KUNLIK MAQSAD WIDGET */}
      {limit > 0 && (
        <div className="card" style={{ padding: '16px', borderRadius: '20px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Target size={18} color="#0A84FF" />
            <span style={{ fontSize: '14px', fontWeight: '600' }}>Oylik maqsad</span>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '12px' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Foydalanildi: {percent}%</span>
            <span style={{ fontWeight: '600', color: percent >= 90 ? 'var(--danger)' : '#fff' }}>Qoldi: {remaining.toLocaleString()} UZS</span>
          </div>
          
          <div style={{ height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${percent}%`, height: '100%', background: percent >= 90 ? 'var(--danger)' : percent >= 75 ? 'var(--warning)' : 'var(--primary)', borderRadius: '4px', transition: 'width 0.3s ease' }} />
          </div>
        </div>
      )}

      {/* ⚠️ QARZ ESLATMA WIDGET */}
      {upcomingDebts.length > 0 && (
        <div className="card clickable" onClick={() => navigate('/debts')} style={{ padding: '16px', borderRadius: '20px', background: 'rgba(255, 159, 10, 0.1)', border: '1px solid rgba(255, 159, 10, 0.2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ background: '#FF9F0A', color: '#fff', padding: '8px', borderRadius: '12px' }}>
                <AlertTriangle size={20} />
              </div>
              <div>
                <p style={{ fontSize: '14px', fontWeight: '600', color: '#fff', margin: 0 }}>Qarz eslatmasi</p>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '2px 0 0' }}>
                  Yaqin kunlarda {upcomingDebts.length} ta qarz muddati
                </p>
              </div>
            </div>
            <span style={{ fontSize: '12px', fontWeight: '600', color: '#FF9F0A' }}>Ko'rish →</span>
          </div>
        </div>
      )}

      {/* 📊 HAFTALIK TREND WIDGET */}
      <div className="card clickable" onClick={() => navigate('/analytics')} style={{ padding: '16px', borderRadius: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <TrendingUp size={18} color="#30D158" />
          <span style={{ fontSize: '14px', fontWeight: '600' }}>Haftalik trend</span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '4px', height: '60px' }}>
          {trendData.length > 0 ? trendData.map((day, i) => {
            const max = Math.max(...trendData.map(d => d.total));
            const height = max > 0 ? (day.total / max) * 100 : 0;
            const isExpense = day.type === 'chiqim';
            return (
              <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                <div style={{ width: '100%', height: `${height}%`, minHeight: '4px', background: isExpense ? 'var(--danger)' : 'var(--success)', borderRadius: '4px', opacity: day.isToday ? 1 : 0.6 }} />
              </div>
            )
          }) : (
            <div style={{ width: '100%', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '12px', alignSelf: 'center' }}>Ma'lumot yo'q</div>
          )}
        </div>
        {trendData.length > 0 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '10px', color: 'var(--text-secondary)' }}>
            <span>{trendData[0]?.day}</span>
            <span>Bugun</span>
          </div>
        )}
      </div>

    </div>
  );
};

export default SmartWidgets;
