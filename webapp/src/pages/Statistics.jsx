import React, { useState, useEffect, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import { ChevronLeft, ChevronRight, Calendar, X, TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { fetchApi, getExchangeRates } from '../utils/api';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RTooltip } from 'recharts';
import { EmptyState, ErrorState, SkeletonPage } from '../components/StateViews';
import PageHeader from '../components/PageHeader';

const StatisticsPage = ({ initData }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(false);
  const [exchangeRates, setExchangeRates] = useState({});

  // Filters
  const [activeCurrency, setActiveCurrency] = useState('UZS');
  const [activeTab, setActiveTab] = useState('Hammasi');
  const [dateModal, setDateModal] = useState(false);

  // Date range
  const [dateRange, setDateRange] = useState(() => {
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth(), 1);
    return { start, end: now };
  });

  // Donut interaction
  const [activeSlice, setActiveSlice] = useState(null);

  const fmtDate = (d) => {
    const months = ['Yan','Fev','Mar','Apr','May','Iyn','Iyl','Avg','Sen','Okt','Noy','Dek'];
    return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
  };

  const fmtDateApi = (d) => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;

  const loadData = async (bg = false) => {
    if (!bg) setLoading(true);
    try {
      const s = fmtDateApi(dateRange.start);
      const e = fmtDateApi(dateRange.end);
      const res = await fetchApi(`/dashboard?start=${s}&end=${e}`);
      if (res && !res.error) { setData(res); setError(false); }
      
      const rates = await getExchangeRates();
      if (rates) setExchangeRates(rates);
    } catch (err) {
      if (err.message !== 'OFFLINE') setError(true);
    } finally {
      if (!bg) setLoading(false);
      setRefreshing(false);
    }
  };

  const handleWs = useCallback(() => loadData(true), [dateRange]);

  useEffect(() => { loadData(); }, [dateRange]);

  useEffect(() => {
    const evts = ['ws_transaction.created','ws_transaction.updated','ws_transaction.deleted','ws_balance.updated','ws_connected','ws_sync'];
    evts.forEach(e => window.addEventListener(e, handleWs));
    return () => evts.forEach(e => window.removeEventListener(e, handleWs));
  }, [handleWs]);

  const shiftDate = (dir) => {
    const diff = dateRange.end - dateRange.start;
    const days = Math.round(diff / 86400000) + 1;
    setDateRange(prev => {
      const ns = new Date(prev.start);
      const ne = new Date(prev.end);
      ns.setDate(ns.getDate() + (dir * days));
      ne.setDate(ne.getDate() + (dir * days));
      return { start: ns, end: ne };
    });
  };

  const setPreset = (type) => {
    const now = new Date();
    if (type === 'today') {
      setDateRange({ start: new Date(now), end: new Date(now) });
    } else if (type === 'week') {
      const s = new Date(now);
      s.setDate(s.getDate() - 6);
      setDateRange({ start: s, end: new Date(now) });
    } else if (type === 'lastMonth') {
      const s = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const e = new Date(now.getFullYear(), now.getMonth(), 0);
      setDateRange({ start: s, end: e });
    }
    setDateModal(false);
  };

  // Derived data
  const balances = data?.balances || [];
  const currencies = balances.map(b => b.currency);
  if (currencies.length === 0) currencies.push('UZS');

  const statsObj = data?.stats?.[activeCurrency] || {};
  const statData = statsObj[activeTab] || [];
  const dailyStats = data?.daily_stats?.[activeCurrency] || {};
  const comparison = data?.comparison?.[activeCurrency] || { kirim: { current: 0, prev: 0 }, chiqim: { current: 0, prev: 0 } };
  const debts = data?.debts || { berishimKerak: 0, olishimKerak: 0 };

  // Totals
  const hammasiData = statsObj['Hammasi'] || [];
  const totalKirim = hammasiData.find(s => s.name === 'Kirim')?.value || 0;
  const totalChiqim = hammasiData.find(s => s.name === 'Chiqim')?.value || 0;
  const totalQoldiq = totalKirim - totalChiqim;

  // Chart data
  const isEmpty = statData.reduce((a, c) => a + c.value, 0) === 0;
  const chartData = isEmpty ? [{ name: "Ma'lumot yo'q", value: 1, color: '#38383A' }] : statData;

  // Line chart
  const lineData = Object.entries(dailyStats).sort(([a],[b]) => a.localeCompare(b)).map(([date, vals]) => {
    const d = new Date(date);
    return { name: `${d.getDate()}`, fullDate: date, kirim: vals.kirim || 0, chiqim: vals.chiqim || 0 };
  });

  // Comparison percentages
  const kirimPct = comparison.kirim.prev > 0 ? Math.round(((comparison.kirim.current - comparison.kirim.prev) / comparison.kirim.prev) * 100) : (comparison.kirim.current > 0 ? 100 : 0);
  const chiqimPct = comparison.chiqim.prev > 0 ? Math.round(((comparison.chiqim.current - comparison.chiqim.prev) / comparison.chiqim.prev) * 100) : (comparison.chiqim.current > 0 ? 100 : 0);

  // Qarz tab data
  const qarzData = [
    { name: 'Berishim kerak', value: debts.berishimKerak || 0, color: '#FF453A', emoji: '💸' },
    { name: 'Olishim kerak', value: debts.olishimKerak || 0, color: '#30D158', emoji: '💰' }
  ];

  const displayData = activeTab === 'Qarz' ? qarzData : chartData;
  const displayEmpty = activeTab === 'Qarz' ? (qarzData[0].value + qarzData[1].value === 0) : isEmpty;
  const finalChartData = displayEmpty ? [{ name: "Ma'lumot yo'q", value: 1, color: '#38383A' }] : displayData;

  const centerLabel = activeTab === 'Hammasi' ? { label: 'Jami:', value: (totalKirim + totalChiqim) }
    : activeTab === 'Kirim' ? { label: 'Jami kirim:', value: totalKirim }
    : activeTab === 'Chiqim' ? { label: 'Jami chiqim:', value: totalChiqim }
    : { label: 'Jami qarz:', value: debts.berishimKerak + debts.olishimKerak };

  const legendTotal = displayData.reduce((a, c) => a + c.value, 0);

  // Custom line tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    const item = payload[0]?.payload;
    return (
      <div style={{ background: 'rgba(0,0,0,0.85)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', padding: '10px 14px', backdropFilter: 'blur(10px)' }}>
        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px' }}>{item?.fullDate}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ fontSize: '13px', fontWeight: '600', color: p.color, margin: '2px 0' }}>
            {p.name === 'kirim' ? 'Kirim' : 'Chiqim'}: {p.value?.toLocaleString()} {activeCurrency}
          </p>
        ))}
      </div>
    );
  };

  if (loading) {
    return <SkeletonPage cards={4} />;
  }

  if (error && !data) {
    return <ErrorState onRetry={() => loadData()} />;
  }

  return (
    <div className="animate-fade-in" style={{ padding: '0 16px 100px' }}>
      {refreshing && (
        <div style={{ textAlign: 'center', padding: '10px', color: 'var(--text-secondary)' }}>
          <RefreshCw className="animate-spin" size={24} style={{ margin: '0 auto' }} />
        </div>
      )}

      {/* Header */}
      <PageHeader title="Statistika" showLogo={true} />

      {/* Date Range Selector */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', background: 'var(--card)', borderRadius: '16px', padding: '12px 16px', border: '1px solid var(--border)' }}>
        <button onClick={() => shiftDate(-1)} style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '10px', width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-primary)', cursor: 'pointer' }}>
          <ChevronLeft size={18} />
        </button>
        <button onClick={() => setDateModal(true)} style={{ background: 'none', border: 'none', color: 'var(--text-primary)', fontSize: '15px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Calendar size={16} color="var(--primary)" />
          {fmtDate(dateRange.start)} – {fmtDate(dateRange.end)}
        </button>
        <button onClick={() => shiftDate(1)} style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '10px', width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-primary)', cursor: 'pointer' }}>
          <ChevronRight size={18} />
        </button>
      </div>

      {/* Currency Chips */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: (activeCurrency !== 'UZS' && exchangeRates[activeCurrency]) ? '8px' : '20px', overflowX: 'auto' }} className="no-scrollbar">
        {currencies.map(c => (
          <button key={c} onClick={() => setActiveCurrency(c)} style={{
            padding: '8px 20px', borderRadius: '20px', fontSize: '14px', fontWeight: '600', border: 'none', cursor: 'pointer', transition: 'all 0.2s', flexShrink: 0,
            background: activeCurrency === c ? 'var(--primary)' : 'var(--card)',
            color: activeCurrency === c ? '#fff' : 'var(--text-secondary)',
            boxShadow: activeCurrency === c ? '0 4px 12px var(--primary-glow)' : 'none'
          }}>
            {activeCurrency === c ? '● ' : '○ '}{balances.find(b => b.currency === c)?.title || c}
          </button>
        ))}
      </div>
      
      {/* Exchange Rate Badge */}
      {activeCurrency !== 'UZS' && exchangeRates[activeCurrency] && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '20px', padding: '0 4px' }}>
          <span style={{ fontSize: '12px', fontWeight: '500', color: 'var(--primary)' }}>💱 1 {activeCurrency} = {exchangeRates[activeCurrency].toLocaleString('uz-UZ', {maximumFractionDigits: 2})} UZS</span>
          <span style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>(Markaziy Bank)</span>
        </div>
      )}

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '24px' }}>
        {[
          { icon: '💰', label: 'Kirim', value: totalKirim, color: '#30D158', bg: 'rgba(48,209,88,0.08)', border: 'rgba(48,209,88,0.2)' },
          { icon: '💸', label: 'Chiqim', value: totalChiqim, color: '#FF453A', bg: 'rgba(255,69,58,0.08)', border: 'rgba(255,69,58,0.2)' },
          { icon: '✅', label: 'Qoldiq', value: totalQoldiq, color: totalQoldiq >= 0 ? '#30D158' : '#FF453A', bg: 'rgba(10,132,255,0.08)', border: 'rgba(10,132,255,0.2)' }
        ].map((c, i) => (
          <div key={i} style={{ background: c.bg, border: `1px solid ${c.border}`, borderRadius: '16px', padding: '14px 12px', textAlign: 'center' }}>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px', fontWeight: '500' }}>{c.icon} {c.label}</p>
            <p style={{ fontSize: '16px', fontWeight: '800', color: c.color }}>{c.value.toLocaleString()}</p>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>{activeCurrency}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', background: 'var(--card)', borderRadius: '12px', padding: '4px', marginBottom: '24px', gap: '4px' }}>
        {['Hammasi', 'Kirim', 'Chiqim', 'Qarz'].map(tab => (
          <button key={tab} onClick={() => { setActiveTab(tab); setActiveSlice(null); }} style={{
            flex: 1, textAlign: 'center', padding: '10px 0', fontSize: '13px', fontWeight: '600', borderRadius: '10px', border: 'none', cursor: 'pointer', transition: 'all 0.2s',
            background: activeTab === tab ? 'var(--bg)' : 'transparent',
            color: activeTab === tab ? '#fff' : 'var(--text-secondary)',
            boxShadow: activeTab === tab ? '0 2px 8px rgba(0,0,0,0.2)' : 'none'
          }}>
            {tab}
          </button>
        ))}
      </div>

      {/* Donut Chart */}
      <div className="card" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ height: '260px', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={finalChartData}
                innerRadius={70}
                outerRadius={110}
                paddingAngle={displayEmpty ? 0 : 3}
                dataKey="value"
                stroke="none"
                animationBegin={0}
                animationDuration={800}
                animationEasing="ease-out"
                onClick={(_, idx) => !displayEmpty && setActiveSlice(activeSlice === idx ? null : idx)}
              >
                {finalChartData.map((entry, idx) => (
                  <Cell
                    key={idx}
                    fill={entry.color || '#6366F1'}
                    opacity={activeSlice !== null && activeSlice !== idx ? 0.3 : 1}
                    style={{ cursor: displayEmpty ? 'default' : 'pointer', transition: 'all 0.3s ease' }}
                  />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>

          {/* Center label or tooltip */}
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', background: 'rgba(0,0,0,0.75)', padding: '12px 16px', borderRadius: '14px', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.08)', minWidth: '120px' }}>
            {activeSlice !== null && !displayEmpty ? (
              <>
                <p style={{ fontSize: '18px', marginBottom: '4px' }}>{finalChartData[activeSlice]?.emoji || '📊'}</p>
                <p style={{ fontSize: '13px', fontWeight: '700', color: '#fff', marginBottom: '4px' }}>{finalChartData[activeSlice]?.name}</p>
                <p style={{ fontSize: '14px', fontWeight: '800', color: finalChartData[activeSlice]?.color }}>{finalChartData[activeSlice]?.value?.toLocaleString()} {activeCurrency}</p>
                <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {legendTotal > 0 ? Math.round((finalChartData[activeSlice]?.value / legendTotal) * 100) : 0}% • {finalChartData[activeSlice]?.count || '–'} ta
                </p>
              </>
            ) : displayEmpty ? (
              <>
                <p style={{ fontSize: '28px', marginBottom: '8px', opacity: 0.5 }}>📊</p>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.4' }}>Tanlangan davrda<br/>ma'lumot yo'q</p>
              </>
            ) : (
              <>
                <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>{centerLabel.label}</p>
                <p style={{ fontSize: '16px', fontWeight: 'bold', color: '#fff' }}>{centerLabel.value.toLocaleString()} {activeCurrency}</p>
              </>
            )}
          </div>
        </div>

        {/* Legend */}
        {!displayEmpty && (
          <div style={{ marginTop: '16px' }}>
            {displayData.map((item, idx) => {
              const pct = legendTotal > 0 ? Math.round((item.value / legendTotal) * 100) : 0;
              return (
                <div key={idx} onClick={() => setActiveSlice(activeSlice === idx ? null : idx)} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 0', borderBottom: idx < displayData.length - 1 ? '1px solid var(--border)' : 'none', cursor: 'pointer', opacity: activeSlice !== null && activeSlice !== idx ? 0.4 : 1, transition: 'opacity 0.3s' }}>
                  <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: item.color, flexShrink: 0 }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '14px', fontWeight: '500' }}>{item.emoji || '●'} {item.name}</span>
                      <span style={{ fontSize: '14px', fontWeight: '700' }}>{item.value.toLocaleString()} <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{pct}%</span></span>
                    </div>
                    <div style={{ height: '4px', borderRadius: '2px', background: 'var(--bg)', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${pct}%`, background: item.color, borderRadius: '2px', transition: 'width 0.8s ease' }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Line Chart */}
      {lineData.length > 1 && (
        <div className="card" style={{ padding: '20px', marginBottom: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>Kunlik dinamika</h3>
          <div style={{ height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.3)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="rgba(255,255,255,0.3)" fontSize={11} tickLine={false} axisLine={false} tickFormatter={v => v >= 1000000 ? `${(v/1000000).toFixed(1)}M` : v >= 1000 ? `${(v/1000).toFixed(0)}K` : v} />
                <RTooltip content={<CustomTooltip />} />
                <Line type="monotone" dataKey="kirim" stroke="#30D158" strokeWidth={2.5} dot={false} activeDot={{ r: 5, fill: '#30D158', stroke: '#fff', strokeWidth: 2 }} />
                <Line type="monotone" dataKey="chiqim" stroke="#FF453A" strokeWidth={2.5} dot={false} activeDot={{ r: 5, fill: '#FF453A', stroke: '#fff', strokeWidth: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '24px', marginTop: '12px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--text-secondary)' }}>
              <span style={{ width: '12px', height: '3px', borderRadius: '2px', background: '#30D158' }} /> Kirim
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--text-secondary)' }}>
              <span style={{ width: '12px', height: '3px', borderRadius: '2px', background: '#FF453A' }} /> Chiqim
            </span>
          </div>
        </div>
      )}

      {/* Comparison */}
      <div className="card" style={{ padding: '20px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>O'tgan davr taqqoslash</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div style={{ background: 'rgba(48,209,88,0.08)', border: '1px solid rgba(48,209,88,0.15)', borderRadius: '14px', padding: '16px' }}>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>Kirim</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              {kirimPct >= 0 ? <TrendingUp size={18} color="#30D158" /> : <TrendingDown size={18} color="#FF453A" />}
              <span style={{ fontSize: '20px', fontWeight: '800', color: kirimPct >= 0 ? '#30D158' : '#FF453A' }}>
                {kirimPct >= 0 ? '+' : ''}{kirimPct}%
              </span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>{comparison.kirim.current.toLocaleString()} vs {comparison.kirim.prev.toLocaleString()}</p>
          </div>
          <div style={{ background: 'rgba(255,69,58,0.08)', border: '1px solid rgba(255,69,58,0.15)', borderRadius: '14px', padding: '16px' }}>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>Chiqim</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              {chiqimPct <= 0 ? <TrendingDown size={18} color="#30D158" /> : <TrendingUp size={18} color="#FF453A" />}
              <span style={{ fontSize: '20px', fontWeight: '800', color: chiqimPct <= 0 ? '#30D158' : '#FF453A' }}>
                {chiqimPct >= 0 ? '+' : ''}{chiqimPct}%
              </span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>{comparison.chiqim.current.toLocaleString()} vs {comparison.chiqim.prev.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Date Modal */}
      {dateModal && createPortal(
        <div className="modal-overlay" onClick={() => setDateModal(false)} style={{ zIndex: 9999 }}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="flex-between" style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '20px', fontWeight: 'bold' }}>Davrni tanlang</h3>
              <button onClick={() => setDateModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)' }}><X size={20} /></button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
              <div style={{ background: 'var(--bg)', padding: '12px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Boshlang'ich</p>
                <input type="date" value={fmtDateApi(dateRange.start)} onChange={e => setDateRange(p => ({...p, start: new Date(e.target.value)}))} style={{ width: '100%', background: 'transparent', border: 'none', color: '#fff', fontSize: '14px', fontWeight: '600', outline: 'none' }} />
              </div>
              <div style={{ background: 'var(--bg)', padding: '12px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Yakuniy</p>
                <input type="date" value={fmtDateApi(dateRange.end)} onChange={e => setDateRange(p => ({...p, end: new Date(e.target.value)}))} style={{ width: '100%', background: 'transparent', border: 'none', color: '#fff', fontSize: '14px', fontWeight: '600', outline: 'none' }} />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
              {[{l: 'Bugungi kun', k: 'today'}, {l: 'Hafta', k: 'week'}, {l: "O'tgan oy", k: 'lastMonth'}].map(p => (
                <button key={p.k} onClick={() => setPreset(p.k)} style={{ flex: 1, padding: '10px', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '10px', color: 'var(--text-primary)', fontSize: '13px', fontWeight: '500', cursor: 'pointer' }}>{p.l}</button>
              ))}
            </div>

            <button onClick={() => setDateModal(false)} style={{ width: '100%', padding: '14px', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer' }}>Qo'llash</button>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default StatisticsPage;
