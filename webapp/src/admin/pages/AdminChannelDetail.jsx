import React, { useState, useEffect } from 'react';
import { ArrowLeft, Users, Download, UserX, CheckCircle, Clock, TrendingUp, AlertTriangle, RefreshCw } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';

const AdminChannelDetail = ({ token, navigateTo, channelLink, channelName }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all'); // 'all' | 'left'
  
  // Filters
  const [filterDate, setFilterDate] = useState('all');
  const [filterRegion, setFilterRegion] = useState('');
  const [filterAge, setFilterAge] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  useEffect(() => {
    if (!channelLink) {
      navigateTo('channels');
      return;
    }
    fetchData();
  }, [channelLink]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/channel-stats?link=${encodeURIComponent(channelLink)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const json = await res.json();
      setData(json);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleExport = (usersList, filename) => {
    if (!usersList || !usersList.length) return;
    
    const headers = ['№', 'Ism', 'Telefon', 'Sana', 'Viloyat', 'Yosh', 'Holat'];
    const rows = usersList.map((u, i) => [
      i + 1,
      `"${u.name || ''}"`,
      `"${u.phone || ''}"`,
      `"${u.date || ''}"`,
      `"${u.region || ''}"`,
      `"${u.age_group || ''}"`,
      `"${u.status || ''}"`
    ]);

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${filename}_${new Date().toISOString().substring(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="admin-page fade-in">
        <button className="btn-back mb20" onClick={() => navigateTo('channels')} style={backBtnStyle}>
          <ArrowLeft size={18} /> Kanallarga qaytish
        </button>
        <h1 className="page-title">📊 Statistika yuklanmoqda...</h1>
        <div className="dashboard-grid mb20">
          {[1,2,3,4].map(i => <div key={i} className="skeleton-card" style={{height: 120, borderRadius: '16px'}} />)}
        </div>
        <div className="skeleton-card" style={{height: 300, borderRadius: '16px'}} />
      </div>
    );
  }

  if (!data) return (
    <div className="admin-page fade-in">
      <button className="btn-back mb20" onClick={() => navigateTo('channels')} style={backBtnStyle}>
        <ArrowLeft size={18} /> Kanallarga qaytish
      </button>
      <div className="card" style={{textAlign: 'center', padding: '40px'}}>
        <AlertTriangle size={48} style={{color: '#ef4444', marginBottom: '16px'}} />
        <h2>Ma'lumot yuklanmadi</h2>
        <p style={{color: 'var(--text-light)'}}>Qayta urinib ko'ring</p>
        <button className="btn-primary mt20" onClick={fetchData}><RefreshCw size={16}/> Qayta yuklash</button>
      </div>
    </div>
  );

  const { summary, conversion, chart, users } = data;
  
  // Pie Chart
  const COLORS = ['#10b981', '#f59e0b', '#ef4444'];
  const pieData = [
    { name: "Obuna bo'lganlar", value: conversion.subscribed },
    { name: 'Kutmoqda', value: conversion.not_subscribed },
    { name: 'Chiqib ketganlar', value: conversion.left }
  ].filter(d => d.value > 0);

  const totalAction = conversion.clicked || 1;

  // Date helpers
  const todayStr = new Date().toISOString().substring(0, 10);
  const weekAgo = new Date(); weekAgo.setDate(weekAgo.getDate() - 7);
  const monthAgo = new Date(); monthAgo.setMonth(monthAgo.getMonth() - 1);

  // Separate users
  const leftUsers = users.filter(u => u.status === 'Chiqib ketgan');
  const activeOrPendingUsers = users;

  // Apply filters
  const applyFilters = (list) => list.filter(u => {
    if (filterRegion && u.region !== filterRegion) return false;
    if (filterAge && u.age_group !== filterAge) return false;
    if (filterStatus && u.status !== filterStatus) return false;
    if (filterDate !== 'all') {
      const uDateStr = (u.date || '').substring(0, 10);
      if (filterDate === 'today' && uDateStr !== todayStr) return false;
      const uDate = new Date(u.date);
      if (filterDate === 'week' && uDate < weekAgo) return false;
      if (filterDate === 'month' && uDate < monthAgo) return false;
    }
    return true;
  });

  const filteredUsers = applyFilters(activeTab === 'left' ? leftUsers : activeOrPendingUsers);

  // Unique values for filters
  const regions = [...new Set(users.map(u => u.region).filter(r => r && r !== "Noma'lum"))];
  const ageGroups = [...new Set(users.map(u => u.age_group).filter(a => a && a !== "Noma'lum"))];

  // Custom pie label
  const renderCustomLabel = ({ name, percent }) => `${(percent * 100).toFixed(0)}%`;

  return (
    <div className="admin-page fade-in" style={{paddingBottom: '40px'}}>
      {/* Back Button */}
      <button className="btn-back mb20" onClick={() => navigateTo('channels')} style={backBtnStyle}>
        <ArrowLeft size={18} /> Kanallarga qaytish
      </button>

      {/* Title */}
      <div style={{marginBottom: '28px'}}>
        <h1 className="page-title" style={{margin: 0}}>📢 {channelName}</h1>
        <p style={{color: 'var(--text-light)', marginTop: '4px', fontSize: '14px'}}>{channelLink}</p>
      </div>

      {/* ═══ UMUMIY RAQAMLAR ═══ */}
      <div className="dashboard-grid mb20">
        <StatCard icon={<Users size={24}/>} color="#3b82f6" title="Bot orqali o'tganlar" value={summary.total_passed} />
        <StatCard icon={<TrendingUp size={24}/>} color="#10b981" title="Bugun" value={`+${summary.today}`} />
        <StatCard icon={<Clock size={24}/>} color="#f59e0b" title="Bu hafta" value={`+${summary.week}`} />
        <StatCard icon={<Clock size={24}/>} color="#8b5cf6" title="Bu oy" value={`+${summary.month}`} />
      </div>

      {/* ═══ CHARTS ═══ */}
      <div className="charts-grid mb20">
        {/* LINE CHART */}
        <div className="chart-card card">
          <h3 className="chart-title" style={{marginBottom: '20px'}}>📈 O'sish dinamikasi</h3>
          <div style={{ width: '100%', height: 300 }}>
            {chart.length > 0 ? (
              <ResponsiveContainer>
                <LineChart data={chart} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="date" stroke="var(--text-light)" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-light)" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.15)' }}
                    labelStyle={{ color: 'var(--text)', fontWeight: 600 }}
                    itemStyle={{ color: 'var(--text)' }}
                    formatter={(value) => [`${value} kishi`, 'Yangi obunalar']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    name="Yangi obunalar" 
                    stroke="#3b82f6" 
                    strokeWidth={3} 
                    dot={{ r: 5, strokeWidth: 2, fill: '#fff' }} 
                    activeDot={{ r: 7, stroke: '#3b82f6', strokeWidth: 2 }} 
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-light)'}}>
                📭 Hali ma'lumot yo'q
              </div>
            )}
          </div>
        </div>

        {/* PIE CHART — KONVERSIYA */}
        <div className="chart-card card">
          <h3 className="chart-title" style={{marginBottom: '20px'}}>🎯 Kanal konversiyasi</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ width: '100%', height: '220px' }}>
              {pieData.length > 0 ? (
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={85}
                      paddingAngle={4}
                      dataKey="value"
                      label={renderCustomLabel}
                      labelLine={false}
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: 'var(--card-bg)', border: 'none', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} 
                      formatter={(value, name) => [`${value} kishi`, name]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-light)'}}>
                  Ma'lumot yo'q
                </div>
              )}
            </div>

            {/* Konversiya raqamlari */}
            <div style={{padding: '0 8px'}}>
              <ConversionRow icon="👆" label="Tugma bosganlar" value={conversion.clicked} percent="100" color="var(--text)" />
              <ConversionRow icon="✅" label="Obuna bo'lganlar" value={conversion.subscribed} percent={((conversion.subscribed / totalAction) * 100).toFixed(1)} color="#10b981" />
              <ConversionRow icon="⏳" label="Hali obuna bo'lmaganlar" value={conversion.not_subscribed} percent={((conversion.not_subscribed / totalAction) * 100).toFixed(1)} color="#f59e0b" />
              <ConversionRow icon="🚫" label="Kanaldan chiqganlar" value={conversion.left} percent={((conversion.left / totalAction) * 100).toFixed(1)} color="#ef4444" />
            </div>
          </div>
        </div>
      </div>

      {/* ═══ TABS: Barcha userlar / Chiqib ketganlar ═══ */}
      <div className="card mb20">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '20px' }}>
          <div style={{display: 'flex', gap: '8px'}}>
            <TabBtn active={activeTab === 'all'} onClick={() => setActiveTab('all')}>
              👥 Barcha ({users.length})
            </TabBtn>
            <TabBtn active={activeTab === 'left'} onClick={() => setActiveTab('left')} danger>
              🚫 Chiqib ketganlar ({leftUsers.length})
            </TabBtn>
          </div>
          
          <button 
            className="btn-primary" 
            onClick={() => handleExport(filteredUsers, activeTab === 'left' ? `Chiqib_ketganlar_${channelName}` : `Bot_orqali_${channelName}`)} 
            style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}
          >
            <Download size={16} /> 📥 CSV yuklab olish
          </button>
        </div>

        {/* Filtrlar */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '10px', marginBottom: '16px' }}>
          <select value={filterDate} onChange={e => setFilterDate(e.target.value)} style={selectStyle}>
            <option value="all">📅 Sana (Barchasi)</option>
            <option value="today">Bugun</option>
            <option value="week">Bu hafta</option>
            <option value="month">Bu oy</option>
          </select>
          
          <select value={filterRegion} onChange={e => setFilterRegion(e.target.value)} style={selectStyle}>
            <option value="">📍 Viloyat (Barchasi)</option>
            {regions.map(r => <option key={r} value={r}>{r}</option>)}
          </select>

          <select value={filterAge} onChange={e => setFilterAge(e.target.value)} style={selectStyle}>
            <option value="">👤 Yosh (Barchasi)</option>
            {ageGroups.map(a => <option key={a} value={a}>{a}</option>)}
          </select>

          {activeTab === 'all' && (
            <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} style={selectStyle}>
              <option value="">🔖 Holat (Barchasi)</option>
              <option value="Aktiv">Aktiv</option>
              <option value="Kutmoqda">Kutmoqda</option>
              <option value="Chiqib ketgan">Chiqib ketgan</option>
            </select>
          )}
        </div>

        {/* Jadval */}
        <div className="table-responsive">
          <table className="admin-table" style={{width: '100%'}}>
            <thead>
              <tr>
                <th style={{width: '40px'}}>№</th>
                <th>Ism</th>
                <th>Telefon</th>
                <th>Sana</th>
                <th>Viloyat</th>
                <th>Yosh</th>
                <th>Holat</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.length > 0 ? (
                filteredUsers.map((u, i) => (
                  <tr key={u.user_id + '_' + i}>
                    <td style={{fontWeight: 600, color: 'var(--text-light)'}}>{i + 1}</td>
                    <td style={{fontWeight: 500}}>{u.name}</td>
                    <td style={{fontFamily: 'monospace', fontSize: '13px'}}>{u.phone}</td>
                    <td>{u.date}</td>
                    <td>{u.region}</td>
                    <td>{u.age_group || "—"}</td>
                    <td>
                      <span className={`badge ${u.status === 'Aktiv' ? 'success' : u.status === 'Chiqib ketgan' ? 'danger' : 'warning'}`}>
                        {u.status === 'Aktiv' ? '✅' : u.status === 'Chiqib ketgan' ? '🚫' : '⏳'} {u.status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-light)' }}>
                    Topilmadi
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {filteredUsers.length > 0 && (
          <p style={{textAlign: 'right', color: 'var(--text-light)', fontSize: '13px', marginTop: '12px'}}>
            Jami: {filteredUsers.length} kishi
          </p>
        )}
      </div>
    </div>
  );
};

/* ═══ Sub-components ═══ */

const StatCard = ({ icon, color, title, value }) => (
  <div className="stat-card">
    <div className="stat-icon" style={{background: `${color}15`, color}}>{icon}</div>
    <div className="stat-info">
      <h3>{title}</h3>
      <p className="stat-val">{typeof value === 'number' ? value.toLocaleString() : value}</p>
    </div>
  </div>
);

const ConversionRow = ({ icon, label, value, percent, color }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
    <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-light)', fontSize: '14px' }}>
      {icon} {label}:
    </span>
    <span style={{ fontWeight: 600, color, fontSize: '14px' }}>
      {value} kishi ({percent}%)
    </span>
  </div>
);

const TabBtn = ({ active, onClick, children, danger }) => (
  <button
    onClick={onClick}
    style={{
      padding: '8px 16px',
      borderRadius: '10px',
      border: active ? 'none' : '1px solid var(--border)',
      background: active ? (danger ? 'rgba(239,68,68,0.1)' : 'rgba(59,130,246,0.1)') : 'transparent',
      color: active ? (danger ? '#ef4444' : '#3b82f6') : 'var(--text-light)',
      fontWeight: active ? 600 : 400,
      cursor: 'pointer',
      fontSize: '13px',
      transition: 'all 0.2s ease'
    }}
  >
    {children}
  </button>
);

/* ═══ Styles ═══ */

const backBtnStyle = {
  display: 'flex', alignItems: 'center', gap: '8px',
  background: 'var(--card-bg)', padding: '10px 18px',
  borderRadius: '12px', border: '1px solid var(--border)',
  cursor: 'pointer', color: 'var(--text)', fontSize: '14px',
  fontWeight: 500, transition: 'all 0.2s ease'
};

const selectStyle = {
  padding: '8px 12px', borderRadius: '10px',
  border: '1px solid var(--border)', background: 'var(--card-bg)',
  color: 'var(--text)', fontSize: '13px', cursor: 'pointer'
};

export default AdminChannelDetail;
