import React, { useState, useEffect } from 'react';
import { Filter, Users, MapPin, Clock, Activity, Target, Trash2, ChevronRight, MessageSquare } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import AdminUserDetail from './AdminUserDetail';

// We reuse the heatmap component from AdminDashboard, so let's define a generic one
const Heatmap = ({ data }) => {
  const days = ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya'];
  const hours = Array.from({ length: 24 }, (_, i) => i);
  
  const maxCount = Math.max(...(data || []).map(d => d.count), 1);
  const grid = Array(7).fill(0).map(() => Array(24).fill(0));
  (data || []).forEach(d => {
    if (d.day >= 0 && d.day <= 6 && d.hour >= 0 && d.hour <= 23) {
      grid[d.day][d.hour] = d.count;
    }
  });

  const getColor = (count) => {
    if (count === 0) return 'var(--bg)';
    const intensity = Math.max(0.1, count / maxCount);
    return `rgba(59, 130, 246, ${intensity})`; // Blue for segments
  };

  return (
    <div className="heatmap-container">
      <div className="heatmap-grid">
        <div className="heatmap-empty-corner"></div>
        {hours.map(h => <div key={h} className="heatmap-header-x">{h}</div>)}
        {days.map((day, dIdx) => (
          <React.Fragment key={day}>
            <div className="heatmap-header-y">{day}</div>
            {hours.map(hIdx => {
              const count = grid[dIdx][hIdx];
              return (
                <div 
                  key={`${dIdx}-${hIdx}`} 
                  className="heatmap-cell"
                  style={{ backgroundColor: getColor(count) }}
                  title={`${day} ${hIdx}:00 - ${count} xabar`}
                />
              );
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <p className="label">{`${label}`}</p>
        <p className="intro" style={{ color: payload[0].color || 'var(--admin-primary)' }}>
          {`${payload[0].value} ta`}
        </p>
      </div>
    );
  }
  return null;
};

const FilterCheckbox = ({ label, value, state, setState }) => {
  const isChecked = state.includes(value);
  const toggle = () => {
    if (isChecked) setState(state.filter(v => v !== value));
    else setState([...state, value]);
  };
  return (
    <label className="checkbox-label">
      <input type="checkbox" checked={isChecked} onChange={toggle} />
      <span>{label}</span>
    </label>
  );
};

const AdminSegments = ({ token, navigateTo }) => {
  // Filter States
  const [ageGroups, setAgeGroups] = useState([]);
  const [genders, setGenders] = useState([]);
  const [countries, setCountries] = useState([]);
  const [regions, setRegions] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [interests, setInterests] = useState([]);
  const [incomeLevels, setIncomeLevels] = useState([]);

  // Available options (could be fetched dynamically, but hardcoded for UI speed)
  const OPT_AGES = ['18-24', '25-34', '35-44', '45-54', '55+'];
  const OPT_GENDERS = ['Erkak', 'Ayol'];
  const OPT_COUNTRIES = ["O'zbekiston", "Rossiya", "Qozog'iston", "Boshqa"];
  const OPT_REGIONS = ["Toshkent", "Samarqand", "Farg'ona", "Andijon", "Namangan", "Buxoro", "Xorazm", "Qashqadaryo", "Surxondaryo", "Jizzax", "Sirdaryo", "Navoiy"];
  const OPT_LANGS = [{l: 'uz', n: "O'zbek"}, {l: 'ru', n: "Rus"}, {l: 'en', n: "Ingliz"}];
  const OPT_INTERESTS = ["Sport", "Oziq-ovqat", "Sayohat", "Kiyim-kechak", "Ta'lim", "Texnologiya", "Sog'liqni saqlash", "Avtomobil"];
  const OPT_INCOMES = ["Past", "O'rta", "Yuqori"];

  // Results State
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const [selectedUser, setSelectedUser] = useState(null);

  // Initial fetch for generic stats or default view
  useEffect(() => {
    applyFilters();
  }, []);

  const applyFilters = async () => {
    setLoading(true);
    try {
      const payload = {
        age_groups: ageGroups,
        genders: genders,
        countries: countries,
        regions: regions,
        languages: languages,
        interests: interests,
        income_levels: incomeLevels
      };
      
      const res = await fetch('/api/admin/segments/filter', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        setResults(await res.json());
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const clearFilters = () => {
    setAgeGroups([]); setGenders([]); setCountries([]); setRegions([]);
    setLanguages([]); setInterests([]); setIncomeLevels([]);
  };

  const handleBroadcast = () => {
    const payload = {
      age_groups: ageGroups,
      genders: genders,
      countries: countries,
      regions: regions,
      languages: languages,
      interests: interests,
      income_levels: incomeLevels
    };
    navigateTo('broadcast', { initialFilters: payload });
  };

  if (selectedUser) {
    return <AdminUserDetail token={token} userId={selectedUser} onBack={() => setSelectedUser(null)} />;
  }

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  return (
    <div className="admin-page fade-in">
      <div className="page-header">
        <h1 className="page-title">🎯 Segmentatsiya (Ads Manager)</h1>
        {results && results.count > 0 && (
          <button className="btn-primary" onClick={handleBroadcast}>
            <MessageSquare size={16} /> Shu segmentga xabar yuborish
          </button>
        )}
      </div>

      <div className="segment-layout">
        {/* LEFT: FILTERS */}
        <div className="segment-sidebar card">
          <div className="sidebar-top">
            <h3>Filtrlar</h3>
            <button className="btn-clear" onClick={clearFilters}><Trash2 size={14}/> Tozalash</button>
          </div>

          <div className="filter-group">
            <h4>Yosh</h4>
            {OPT_AGES.map(a => <FilterCheckbox key={a} label={a} value={a} state={ageGroups} setState={setAgeGroups} />)}
          </div>

          <div className="filter-group">
            <h4>Jins</h4>
            {OPT_GENDERS.map(g => <FilterCheckbox key={g} label={g} value={g} state={genders} setState={setGenders} />)}
          </div>

          <div className="filter-group">
            <h4>Davlat</h4>
            {OPT_COUNTRIES.map(c => <FilterCheckbox key={c} label={c} value={c} state={countries} setState={setCountries} />)}
          </div>

          {countries.includes("O'zbekiston") && (
            <div className="filter-group">
              <h4>Viloyat</h4>
              {OPT_REGIONS.map(r => <FilterCheckbox key={r} label={r} value={r} state={regions} setState={setRegions} />)}
            </div>
          )}

          <div className="filter-group">
            <h4>Til</h4>
            {OPT_LANGS.map(l => <FilterCheckbox key={l.l} label={l.n} value={l.l} state={languages} setState={setLanguages} />)}
          </div>

          <div className="filter-group">
            <h4>Qiziqishlar</h4>
            {OPT_INTERESTS.map(i => <FilterCheckbox key={i} label={i} value={i} state={interests} setState={setInterests} />)}
          </div>

          <div className="filter-group">
            <h4>Daromad darajasi</h4>
            {OPT_INCOMES.map(i => <FilterCheckbox key={i} label={i} value={i} state={incomeLevels} setState={setIncomeLevels} />)}
          </div>

          <button className="btn-primary w-full mt10" onClick={applyFilters} disabled={loading}>
            <Filter size={16} /> {loading ? "Qidirilmoqda..." : "Filtrni qo'llash"}
          </button>
        </div>

        {/* RIGHT: RESULTS */}
        <div className="segment-results">
          {loading ? (
            <div className="skeleton-row" style={{height: '300px'}}></div>
          ) : results ? (
            <>
              {/* SUMMARY CARD */}
              <div className="card segment-summary">
                <div className="summary-header">
                  <Target size={24} color="var(--admin-primary)" />
                  <h2>Topildi: {results.count.toLocaleString()} ta foydalanuvchi</h2>
                </div>
                
                {results.count > 0 ? (
                  <div className="summary-details">
                    <p>Bu segmentning xususiyatlari:</p>
                    <div className="sd-grid">
                      <div className="sd-item">
                        <MapPin size={16} color="var(--text-muted)"/>
                        <span>Asosan: <strong>{results.top_regions.join(', ') || "Noma'lum"}</strong></span>
                      </div>
                      <div className="sd-item">
                        <Clock size={16} color="var(--text-muted)"/>
                        <span>Eng aktiv: <strong>Heatmap ga qarang</strong></span>
                      </div>
                      <div className="sd-item">
                        <Activity size={16} color="var(--text-muted)"/>
                        <span>O'rtacha oylik: <strong>~{results.avg_income.toLocaleString()} UZS</strong></span>
                      </div>
                      <div className="sd-item">
                        <Target size={16} color="var(--text-muted)"/>
                        <span>Ko'p sarflagan: <strong>{results.top_expense_cat}</strong></span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="cell-muted mt10">Bu filtrlarga mos foydalanuvchilar topilmadi.</p>
                )}
              </div>

              {results.count > 0 && (
                <>
                  {/* CHARTS ROW */}
                  <div className="segment-charts">
                    <div className="card chart-card pie">
                      <h3>Til taqsimoti</h3>
                      <div className="chart-wrapper pie-wrapper">
                        <ResponsiveContainer width="100%" height={160}>
                          <PieChart>
                            <Pie data={results.lang_chart} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={5} dataKey="value">
                              {results.lang_chart.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip content={<CustomTooltip />} />
                          </PieChart>
                        </ResponsiveContainer>
                        <div className="pie-legend">
                          {results.lang_chart.map((d, i) => (
                            <div className="legend-item" key={i}>
                              <span className="dot" style={{ background: COLORS[i % COLORS.length] }}></span>
                              <span>{d.name.toUpperCase()}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="card chart-card">
                      <h3>Yosh taqsimoti</h3>
                      <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={160}>
                          <BarChart data={results.age_chart} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                            <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
                            <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>

                  {/* HEATMAP */}
                  <div className="card mt20 heatmap-card">
                    <h3>🔥 Bu segmentning aktiv vaqtlari</h3>
                    <Heatmap data={results.heatmap} />
                  </div>

                  {/* USERS LIST */}
                  <div className="card mt20">
                    <h3>Foydalanuvchilar ro'yxati (Max 500)</h3>
                    <div className="users-list mt10">
                      {results.users.map(u => (
                        <div key={u.telegram_id} className="user-list-item mini" onClick={() => setSelectedUser(u.telegram_id)}>
                          <div className="user-item-main">
                            <div className="user-avatar small">
                              {u.full_name ? u.full_name.charAt(0).toUpperCase() : <User size={14}/>}
                            </div>
                            <div className="user-item-info">
                              <span className="ui-name">{u.full_name}</span>
                              <div className="ui-row secondary">
                                <span>{u.age_group}</span> • <span>{u.region}</span> • <span>{u.gender}</span>
                              </div>
                            </div>
                          </div>
                          <ChevronRight size={16} color="var(--text-muted)" />
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default AdminSegments;
