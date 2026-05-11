import React, { useState, useEffect } from 'react';
import { ArrowLeft, User, Phone, Globe, Calendar, Clock, MessageSquare, CreditCard, Bot, MapPin, Activity, Edit2, Check, X, Trash2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const AdminUserDetail = ({ token, userId, onBack }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [aiSummary, setAiSummary] = useState(null);
  const [loadingAi, setLoadingAi] = useState(false);
  
  const [editGender, setEditGender] = useState(false);
  const [newGender, setNewGender] = useState('');

  useEffect(() => {
    fetchDetail();
  }, [userId]);

  const fetchDetail = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        setData(json);
        setNewGender(json.segment.gender);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleGetAiSummary = async () => {
    setLoadingAi(true);
    try {
      const res = await fetch(`/api/admin/users/${userId}/ai-summary`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        setAiSummary(json.summary);
      } else {
        setAiSummary("Xatolik yuz berdi. Iltimos qayta urinib ko'ring.");
      }
    } catch (e) {
      setAiSummary("Xatolik yuz berdi.");
    }
    setLoadingAi(false);
  };

  const handleSaveGender = async () => {
    try {
      const res = await fetch(`/api/admin/users/${userId}/gender`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ gender: newGender })
      });
      if (res.ok) {
        setData(prev => ({
          ...prev,
          segment: { ...prev.segment, gender: newGender }
        }));
        setEditGender(false);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteHistory = async (historyId) => {
    if(!confirm("Haqiqatan ham ushbu tarixni butunlay o'chirib yubormoqchimisiz? Ma'lumotlar qaytarilmaydi!")) return;
    try {
      const res = await fetch(`/api/admin/users/${userId}/financial-history/${historyId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setData(prev => ({
          ...prev,
          financial_history: prev.financial_history.filter(h => h._id !== historyId)
        }));
      }
    } catch(e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <div className="admin-page fade-in">
        <button className="btn-back" onClick={onBack}><ArrowLeft size={16} /> Orqaga</button>
        <div className="skeleton-row mt20" style={{ height: '200px' }}></div>
        <div className="skeleton-row" style={{ height: '200px' }}></div>
      </div>
    );
  }

  if (!data) return <div className="admin-page"><button className="btn-back" onClick={onBack}><ArrowLeft size={16} /> Orqaga</button><p>User topilmadi.</p></div>;

  const { basic, segment, financial, activity_30d, financial_history = [], user_heatmap = [], best_hour, best_day } = data;

  return (
    <div className="admin-page fade-in">
      <div className="detail-header">
        <button className="btn-back" onClick={onBack}>
          <ArrowLeft size={18} /> Orqaga
        </button>
        <h2 className="detail-title">{basic.full_name}</h2>
        <button className="btn-primary" onClick={handleGetAiSummary} disabled={loadingAi}>
          <Bot size={16} /> AI Xulosasi
        </button>
      </div>

      {aiSummary && (
        <div className="ai-summary-card card fade-in mb20">
          <div className="ai-header">
            <Bot size={20} color="#8b5cf6" />
            <h3>AI Xulosasi</h3>
          </div>
          <p className="ai-text">{aiSummary}</p>
        </div>
      )}

      {loadingAi && (
        <div className="ai-summary-card card mb20 flex-center">
          <div className="spinner"></div>
          <span style={{marginLeft: '10px', color: 'var(--text-muted)'}}>AI tahlil qilmoqda...</span>
        </div>
      )}

      <div className="detail-grid">
        {/* ASOSIY MA'LUMOTLAR */}
        <div className="card detail-card">
          <h3>Asosiy ma'lumotlar</h3>
          <div className="detail-list">
            <div className="detail-item">
              <User size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Ism familiya</span>
                <span className="value">{basic.full_name} {basic.username ? `(@${basic.username})` : ''}</span>
              </div>
            </div>
            <div className="detail-item">
              <Phone size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Telefon</span>
                <span className="value">{basic.phone_number}</span>
              </div>
            </div>
            <div className="detail-item">
              <Globe size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Til</span>
                <span className="value">{basic.language === 'uz' ? "O'zbek" : basic.language === 'ru' ? "Rus" : "Ingliz"}</span>
              </div>
            </div>
            <div className="detail-item">
              <Calendar size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Ro'yxatdan o'tgan</span>
                <span className="value">{basic.created_at}</span>
              </div>
            </div>
            <div className="detail-item">
              <Clock size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Oxirgi faollik</span>
                <span className="value">{basic.last_active}</span>
              </div>
            </div>
            <div className="detail-item">
              <MessageSquare size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Jami xabarlar</span>
                <span className="value">{basic.total_messages} ta</span>
              </div>
            </div>
            <div className="detail-item">
              <CreditCard size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Tranzaksiyalar</span>
                <span className="value">{basic.total_txs} ta</span>
              </div>
            </div>
          </div>
        </div>

        {/* SEGMENT MA'LUMOTLARI */}
        <div className="card detail-card">
          <h3>Segment ma'lumotlari</h3>
          <div className="detail-list">
            <div className="detail-item">
              <Calendar size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Yosh guruhi</span>
                <span className="value">{segment.age_group}</span>
              </div>
            </div>
            <div className="detail-item">
              <User size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Jins</span>
                {editGender ? (
                  <div className="edit-inline">
                    <select value={newGender} onChange={e => setNewGender(e.target.value)}>
                      <option value="male">Erkak</option>
                      <option value="female">Ayol</option>
                      <option value="unknown">Noma'lum</option>
                    </select>
                    <button className="btn-icon text-success" onClick={handleSaveGender}><Check size={16}/></button>
                    <button className="btn-icon text-danger" onClick={() => setEditGender(false)}><X size={16}/></button>
                  </div>
                ) : (
                  <div className="value-with-action">
                    <span className="value">
                      {segment.gender === 'male' ? '👨 Erkak' : segment.gender === 'female' ? '👩 Ayol' : '❓ Noma\'lum'}
                    </span>
                    <button className="btn-edit-text" onClick={() => setEditGender(true)}>
                      <Edit2 size={12} /> O'zgartir
                    </button>
                  </div>
                )}
              </div>
            </div>
            <div className="detail-item">
              <MapPin size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Joylashuv</span>
                <span className="value">{segment.region}, {segment.location}</span>
              </div>
            </div>
            <div className="detail-item">
              <Clock size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Timezone</span>
                <span className="value">{segment.timezone}</span>
              </div>
            </div>
            <div className="detail-item">
              <Activity size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">❤️ Qiziqishlar</span>
                <span className="value">
                  {segment.interests?.length > 0 ? segment.interests.map(i => {
                    const labels = { sport: '⚽ Sport', food: '🍔 Oziq-ovqat', fashion: '👗 Kiyim', travel: '✈️ Sayohat', education: '📚 Ta\'lim', entertainment: '🎬 O\'yin-kulgi', auto: '🚗 Mashina', health: '🏥 Sog\'liq' };
                    return labels[i] || i;
                  }).join(', ') : "Noma'lum"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* MOLIYAVIY STATISTIKA */}
        <div className="card detail-card">
          <h3>Moliyaviy Statistika</h3>
          <div className="detail-list">
            <div className="detail-item">
              <div className="detail-icon bg-success"><ArrowLeft size={16} /></div>
              <div className="detail-content">
                <span className="label">O'rtacha oylik kirim</span>
                <span className="value text-success">{financial.avg_income.toLocaleString()} UZS</span>
              </div>
            </div>
            <div className="detail-item">
              <div className="detail-icon bg-danger"><ArrowLeft size={16} style={{transform: 'rotate(180deg)'}} /></div>
              <div className="detail-content">
                <span className="label">O'rtacha oylik chiqim</span>
                <span className="value text-danger">{financial.avg_expense.toLocaleString()} UZS</span>
              </div>
            </div>
            <div className="detail-item">
              <Activity size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Daromad darajasi</span>
                <span className="value badge">{financial.income_level}</span>
              </div>
            </div>
            <div className="detail-item">
              <CreditCard size={16} className="detail-icon" />
              <div className="detail-content">
                <span className="label">Eng ko'p xarajat</span>
                <span className="value">{financial.top_expense_cat}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* DAROMAD TARIXI */}
      <div className="card mt20 full-width">
        <h3>💰 Daromad tarixi</h3>
        {financial_history.length === 0 ? (
          <div className="empty-state">Ma'lumotlar saqlanmagan</div>
        ) : (
          <div className="history-list">
            {financial_history.map(h => (
              <div key={h._id} className="history-item flex-between border-bottom p10">
                <div className="history-info">
                  <strong>{h.month}</strong>: {h.avg_income.toLocaleString()} UZS 
                  <span className={`badge ml10 ${h.income_level === 'high' ? 'bg-success' : h.income_level === 'medium' ? 'bg-primary' : 'bg-danger'}`}>
                    {h.income_level === 'high' ? "Yuqori" : h.income_level === 'medium' ? "O'rta" : "Past"}
                  </span>
                  <span className="text-success ml10"><Check size={14}/></span>
                </div>
                <button className="btn-icon text-danger" onClick={() => handleDeleteHistory(h._id)} title="O'chirish">
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ACTIVITY GRAPH */}
      <div className="card mt20 full-width">
        <h3>Faollik grafigi (Oxirgi 30 kun)</h3>
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={activity_30d} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
              <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
              <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* INDIVIDUAL HEATMAP */}
      <div className="card mt20 full-width heatmap-card">
        <h3>🔥 Aktiv Vaqtlar</h3>
        <div className="user-activity-summary">
          <span>⏰ Eng aktiv soat: <strong>{best_hour !== null && best_hour !== undefined ? `${best_hour}:00` : "Noma'lum"}</strong></span>
          <span>📅 Eng aktiv kun: <strong>{best_day || "Noma'lum"}</strong></span>
        </div>
        <div className="heatmap-container">
          <div className="heatmap-grid">
            <div className="heatmap-empty-corner"></div>
            {Array.from({length: 24}, (_, i) => i).map(h => (
              <div key={h} className="heatmap-header-x">{h}</div>
            ))}
            {['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya'].map((day, dIdx) => {
              const grid = Array(7).fill(0).map(() => Array(24).fill(0));
              (user_heatmap || []).forEach(d => {
                if (d.day >= 0 && d.day <= 6 && d.hour >= 0 && d.hour <= 23) grid[d.day][d.hour] = d.count;
              });
              const maxCount = Math.max(...(user_heatmap || []).map(d => d.count), 1);
              return (
                <React.Fragment key={day}>
                  <div className="heatmap-header-y">{day}</div>
                  {Array.from({length: 24}, (_, hIdx) => {
                    const count = grid[dIdx][hIdx];
                    const intensity = count === 0 ? 0 : Math.max(0.1, count / maxCount);
                    return (
                      <div key={`${dIdx}-${hIdx}`} className="heatmap-cell"
                        style={{ backgroundColor: count === 0 ? 'var(--bg)' : `rgba(16, 185, 129, ${intensity})` }}
                        title={`${day} ${hIdx}:00 — ${count} xabar`}
                      />
                    );
                  })}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminUserDetail;
