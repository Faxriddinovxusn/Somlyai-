import React, { useState, useEffect, useMemo } from 'react';
import { Calendar, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

const StatisticsPage = ({ initData }) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  
  const [period, setPeriod] = useState('month');
  const [currency, setCurrency] = useState('UZS');
  const [tab, setTab] = useState('all');

  useEffect(() => {
    // Simulated fetching
    setLoading(true);
    setTimeout(() => {
      setData({
        metrics: {
          income: 4310000,
          expense: 1200000,
          net: 3110000,
          debtGive: 150000,
          debtTake: 450000,
        },
        comparison: {
          incomeDiff: 12, // +12%
          expenseDiff: -3 // -3%
        },
        pieData: [
          { name: '🍔 Ovqat', value: 450000, color: '#FF9F0A' },
          { name: '🚕 Transport', value: 150000, color: '#0A84FF' },
          { name: '🛒 Xaridlar', value: 300000, color: '#30D158' },
          { name: '🏠 Uy-joy', value: 200000, color: '#FF453A' },
          { name: '🎮 Ko\'ngilochar', value: 80000, color: '#BF5AF2' },
          { name: 'Kichik xarajat', value: 20000, color: '#64D2FF' }
        ],
        lineData: [
          { name: '1', kirim: 0, chiqim: 45000 },
          { name: '5', kirim: 4000000, chiqim: 120000 },
          { name: '10', kirim: 0, chiqim: 200000 },
          { name: '15', kirim: 500000, chiqim: 300000 },
          { name: '20', kirim: 0, chiqim: 150000 },
          { name: '25', kirim: 0, chiqim: 80000 },
          { name: '30', kirim: 0, chiqim: 100000 },
        ]
      });
      setLoading(false);
    }, 800);
  }, [period, currency]);

  // Data processing for Donut Chart (< 2% logic)
  const processedPieData = useMemo(() => {
    if (!data?.pieData) return [];
    const total = data.pieData.reduce((acc, curr) => acc + curr.value, 0);
    const threshold = total * 0.02; // 2%
    let othersValue = 0;
    const result = [];
    
    data.pieData.forEach(item => {
      if (item.value < threshold) {
        othersValue += item.value;
      } else {
        result.push(item);
      }
    });
    
    if (othersValue > 0) {
      result.push({ name: '🌐 Boshqalar', value: othersValue, color: '#8E8E93' });
    }
    
    return result.sort((a, b) => b.value - a.value);
  }, [data]);

  const totalPieValue = useMemo(() => {
    return processedPieData.reduce((acc, curr) => acc + curr.value, 0);
  }, [processedPieData]);

  const formatMoney = (amount) => {
    if (amount >= 1000000) return (amount / 1000000).toFixed(1) + 'M';
    if (amount >= 1000) return (amount / 1000).toFixed(0) + 'K';
    return amount.toString();
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ backgroundColor: 'rgba(28, 28, 30, 0.95)', padding: '12px', borderRadius: '12px', border: '1px solid var(--border)', boxShadow: '0 4px 12px rgba(0,0,0,0.5)', backdropFilter: 'blur(10px)' }}>
          <p style={{ fontWeight: '600', marginBottom: '4px', fontSize: '14px', color: 'white' }}>{payload[0].name}</p>
          <p style={{ color: payload[0].payload.color || 'var(--primary)', fontWeight: 'bold', fontSize: '16px' }}>
            {payload[0].value.toLocaleString()} {currency}
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="animate-fade-in" style={{ padding: '0 16px' }}>
        <div className="skeleton" style={{ height: '40px', borderRadius: '20px', marginBottom: '16px', marginTop: '16px' }}></div>
        <div className="skeleton" style={{ height: '180px', borderRadius: '16px', marginBottom: '16px' }}></div>
        <div className="skeleton" style={{ height: '300px', borderRadius: '16px' }}></div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ padding: '0 16px', paddingBottom: '24px' }}>
      {/* Header */}
      <div className="flex-between" style={{ marginBottom: '16px', paddingTop: '16px' }}>
        <h1 className="title" style={{ margin: 0 }}>Statistika</h1>
      </div>

      {/* Period Selector */}
      <div className="no-scrollbar" style={{ display: 'flex', gap: '8px', overflowX: 'auto', marginBottom: '16px', paddingBottom: '4px' }}>
        {['Bugun', 'Hafta', 'Oy', 'O\'tgan oy'].map(p => (
          <button 
            key={p} 
            className={`chip ${period === (p === 'Oy' ? 'month' : p) ? 'active' : ''}`}
            onClick={() => setPeriod(p === 'Oy' ? 'month' : p)}
          >
            {p}
          </button>
        ))}
        <button className="chip" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Calendar size={14} /> Sana
        </button>
      </div>

      {/* Currency Filter */}
      <div className="no-scrollbar" style={{ display: 'flex', gap: '8px', overflowX: 'auto', marginBottom: '24px', paddingBottom: '4px' }}>
        {['UZS', 'USD', 'RUB', 'KZT'].map(c => (
          <button 
            key={c} 
            className={`chip ${currency === c ? 'active' : ''}`}
            onClick={() => setCurrency(c)}
            style={{ padding: '6px 12px', fontSize: '13px', borderRadius: '8px' }}
          >
            {c}
          </button>
        ))}
      </div>

      {/* Top Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '24px' }}>
        <div className="stat-card success" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--success)', marginBottom: '8px' }}>
            <ArrowDownRight size={16} />
            <span style={{ fontSize: '13px', fontWeight: 600 }}>Jami Kirim</span>
          </div>
          <p style={{ fontSize: '20px', fontWeight: 800 }}>{data.metrics.income.toLocaleString()}</p>
        </div>
        
        <div className="stat-card danger" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--danger)', marginBottom: '8px' }}>
            <ArrowUpRight size={16} />
            <span style={{ fontSize: '13px', fontWeight: 600 }}>Jami Chiqim</span>
          </div>
          <p style={{ fontSize: '20px', fontWeight: 800 }}>{data.metrics.expense.toLocaleString()}</p>
        </div>

        <div className="stat-card" style={{ padding: '16px', gridColumn: 'span 2' }}>
          <p className="subtitle" style={{ fontSize: '14px', marginBottom: '4px' }}>Sof qoldiq</p>
          <div className="flex-between">
            <h2 style={{ fontSize: '28px', fontWeight: 800, color: data.metrics.net >= 0 ? 'var(--success)' : 'var(--danger)' }}>
              {data.metrics.net > 0 ? '+' : ''}{data.metrics.net.toLocaleString()} <span style={{ fontSize: '16px' }}>{currency}</span>
            </h2>
          </div>
        </div>
      </div>

      {/* Comparison with Last Month */}
      <div className="card" style={{ padding: '16px', marginBottom: '24px' }}>
        <p className="subtitle" style={{ fontSize: '14px', marginBottom: '12px' }}>O'tgan oyga nisbatan</p>
        <div className="flex-between" style={{ gap: '12px' }}>
          <div style={{ flex: 1 }}>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Kirim</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
              {data.comparison.incomeDiff > 0 ? <TrendingUp size={16} color="var(--success)" /> : <TrendingDown size={16} color="var(--danger)" />}
              <span style={{ color: data.comparison.incomeDiff > 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>
                {Math.abs(data.comparison.incomeDiff)}% {data.comparison.incomeDiff > 0 ? 'oshdi' : 'kamaydi'}
              </span>
            </div>
          </div>
          <div style={{ width: '1px', backgroundColor: 'var(--border)', height: '30px' }}></div>
          <div style={{ flex: 1 }}>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Chiqim</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
              {data.comparison.expenseDiff > 0 ? <TrendingUp size={16} color="var(--danger)" /> : <TrendingDown size={16} color="var(--success)" />}
              <span style={{ color: data.comparison.expenseDiff < 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>
                {Math.abs(data.comparison.expenseDiff)}% {data.comparison.expenseDiff > 0 ? 'oshdi' : 'kamaydi'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tab-container">
        {['Hammasi', 'Kirim', 'Chiqim', 'Qarz'].map(t => (
          <div 
            key={t} 
            className={`tab ${tab === t.toLowerCase() ? 'active' : ''}`}
            onClick={() => setTab(t.toLowerCase())}
          >
            {t}
          </div>
        ))}
      </div>

      {/* Interactive Donut Chart */}
      <div className="card" style={{ padding: '24px 16px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '24px' }}>Kategoriyalar ulushi</h2>
        
        <div style={{ height: '240px', position: 'relative' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={processedPieData}
                innerRadius={70}
                outerRadius={95}
                paddingAngle={4}
                dataKey="value"
                stroke="none"
                cornerRadius={4}
              >
                {processedPieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', width: '120px' }}>
            <p className="subtitle" style={{ fontSize: '12px' }}>Jami</p>
            <p style={{ fontWeight: '800', fontSize: '18px', marginTop: '2px' }}>{formatMoney(totalPieValue)}</p>
          </div>
        </div>

        {/* Legend / Breakdown List */}
        <div style={{ marginTop: '32px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {processedPieData.map(item => {
            const percent = ((item.value / totalPieValue) * 100).toFixed(1);
            return (
              <div key={item.name}>
                <div className="flex-between" style={{ marginBottom: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '12px', height: '12px', borderRadius: '4px', backgroundColor: item.color }}></div>
                    <span style={{ fontWeight: 500, fontSize: '14px' }}>{item.name}</span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontWeight: 700, fontSize: '14px' }}>{formatMoney(item.value)}</span>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '13px', marginLeft: '8px' }}>{percent}%</span>
                  </div>
                </div>
                <div className="progress-bg">
                  <div className="progress-fill" style={{ width: `${percent}%`, backgroundColor: item.color }}></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Dynamic Line Chart */}
      <div className="card" style={{ padding: '24px 16px', marginBottom: '0' }}>
        <div className="flex-between" style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '700' }}>Dinamika</h2>
          <Activity size={20} color="var(--primary)" />
        </div>
        
        <div style={{ height: '220px', marginLeft: '-15px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.lineData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis 
                dataKey="name" 
                stroke="var(--text-secondary)" 
                tick={{fontSize: 12}} 
                axisLine={false} 
                tickLine={false} 
                dy={10}
              />
              <YAxis 
                stroke="var(--text-secondary)" 
                tick={{fontSize: 12}} 
                axisLine={false} 
                tickLine={false}
                tickFormatter={(value) => formatMoney(value)}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: 'rgba(28, 28, 30, 0.9)', borderRadius: '12px', border: '1px solid var(--border)' }}
                itemStyle={{ fontWeight: 'bold' }}
              />
              <Line 
                type="monotone" 
                dataKey="kirim" 
                name="Kirim"
                stroke="var(--success)" 
                strokeWidth={3} 
                dot={{ r: 0 }} 
                activeDot={{ r: 6, strokeWidth: 0 }}
              />
              <Line 
                type="monotone" 
                dataKey="chiqim" 
                name="Chiqim"
                stroke="var(--danger)" 
                strokeWidth={3} 
                dot={{ r: 0 }} 
                activeDot={{ r: 6, strokeWidth: 0 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Debt summary - only show if all or debt tab is active */}
      {(tab === 'all' || tab === 'qarz') && (
        <div className="card" style={{ marginTop: '16px', padding: '20px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '16px' }}>Qarzlar hisoboti</h2>
          <div className="flex-between" style={{ gap: '16px' }}>
            <div style={{ flex: 1, background: 'rgba(239, 68, 58, 0.1)', padding: '16px', borderRadius: '12px' }}>
              <p style={{ fontSize: '13px', color: 'var(--danger)', fontWeight: 600 }}>Berishim kerak</p>
              <p style={{ fontWeight: '800', fontSize: '18px', marginTop: '6px' }}>{formatMoney(data.metrics.debtGive)}</p>
            </div>
            <div style={{ flex: 1, background: 'rgba(48, 209, 88, 0.1)', padding: '16px', borderRadius: '12px' }}>
              <p style={{ fontSize: '13px', color: 'var(--success)', fontWeight: 600 }}>Olishim kerak</p>
              <p style={{ fontWeight: '800', fontSize: '18px', marginTop: '6px' }}>{formatMoney(data.metrics.debtTake)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatisticsPage;
