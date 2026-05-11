import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, ChevronRight, User } from 'lucide-react';
import AdminUserDetail from './AdminUserDetail';

const AdminUsers = ({ token }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [selectedUser, setSelectedUser] = useState(null);

  // Filters
  const [search, setSearch] = useState('');
  const [filterAge, setFilterAge] = useState('');
  const [filterRegion, setFilterRegion] = useState('');
  const [filterGender, setFilterGender] = useState('');
  const [filterLang, setFilterLang] = useState('');
  const [filterActive, setFilterActive] = useState('');
  const [sortBy, setSortBy] = useState('date_desc');

  // Pagination
  const [page, setPage] = useState(1);
  const ITEMS_PER_PAGE = 20;

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await fetch('/api/admin/users', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUsers(data);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const filteredUsers = useMemo(() => {
    let result = users;

    if (search) {
      const q = search.toLowerCase();
      result = result.filter(u => 
        (u.full_name || '').toLowerCase().includes(q) || 
        (u.phone_number || '').includes(q) ||
        (u.username || '').toLowerCase().includes(q)
      );
    }
    if (filterAge) result = result.filter(u => u.age_group === filterAge);
    if (filterRegion) result = result.filter(u => u.region === filterRegion);
    if (filterGender) result = result.filter(u => u.gender === filterGender);
    if (filterLang) result = result.filter(u => u.language === filterLang);
    if (filterActive !== '') {
      const isActive = filterActive === 'true';
      result = result.filter(u => u.is_active === isActive);
    }

    if (sortBy === 'date_desc') {
      result.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
    } else if (sortBy === 'date_asc') {
      result.sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0));
    } else if (sortBy === 'active_desc') {
      result.sort((a, b) => new Date(b.last_active || 0) - new Date(a.last_active || 0));
    }

    return result;
  }, [users, search, filterAge, filterRegion, filterGender, filterLang, filterActive, sortBy]);

  const displayedUsers = filteredUsers.slice(0, page * ITEMS_PER_PAGE);
  const hasMore = displayedUsers.length < filteredUsers.length;

  // Extract unique regions for filter
  const regions = [...new Set(users.map(u => u.region).filter(Boolean))].sort();

  if (selectedUser) {
    return <AdminUserDetail token={token} userId={selectedUser} onBack={() => setSelectedUser(null)} />;
  }

  const handleExport = () => {
    // CSV Header
    const headers = ['Ism', 'Telefon', 'Yosh', 'Viloyat', 'Jins', 'Daromad (avg)', "Ro'yxat sanasi"];
    const rows = filteredUsers.map(u => [
      `"${u.full_name || ''}"`,
      `"${u.phone_number || ''}"`,
      `"${u.age_group || ''}"`,
      `"${u.region || ''}"`,
      `"${u.gender === 'male' ? 'Erkak' : u.gender === 'female' ? 'Ayol' : ''}"`,
      `"${u.avg_income || ''}"`,
      `"${(u.created_at || '').substring(0, 10)}"`
    ]);

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `SomlyAI_Foydalanuvchilar_${new Date().toISOString().substring(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="admin-page fade-in">
      <div className="flex-row" style={{ justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1 className="page-title" style={{ margin: 0 }}>👥 Foydalanuvchilar</h1>
        <button className="btn-primary" onClick={handleExport} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          Yuklab olish (CSV)
        </button>
      </div>

      <div className="filters-card card mb20">
        <div className="search-bar" style={{ marginBottom: '1rem' }}>
          <Search size={18} />
          <input 
            type="text" 
            placeholder="Ism, username yoki telefon orqali qidirish..." 
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        
        <div className="filters-grid">
          <select value={filterAge} onChange={e => { setFilterAge(e.target.value); setPage(1); }}>
            <option value="">Yosh (Barchasi)</option>
            <option value="18-24">18-24</option>
            <option value="25-34">25-34</option>
            <option value="35-44">35-44</option>
            <option value="45+">45+</option>
          </select>
          
          <select value={filterRegion} onChange={e => { setFilterRegion(e.target.value); setPage(1); }}>
            <option value="">Viloyat (Barchasi)</option>
            {regions.map(r => <option key={r} value={r}>{r}</option>)}
          </select>

          <select value={filterGender} onChange={e => { setFilterGender(e.target.value); setPage(1); }}>
            <option value="">Jins (Barchasi)</option>
            <option value="male">Erkak</option>
            <option value="female">Ayol</option>
          </select>

          <select value={filterLang} onChange={e => { setFilterLang(e.target.value); setPage(1); }}>
            <option value="">Til (Barchasi)</option>
            <option value="uz">O'zbek</option>
            <option value="ru">Rus</option>
            <option value="en">Ingliz</option>
          </select>

          <select value={filterActive} onChange={e => { setFilterActive(e.target.value); setPage(1); }}>
            <option value="">Holat (Barchasi)</option>
            <option value="true">Aktiv</option>
            <option value="false">Nofaol</option>
          </select>

          <select value={sortBy} onChange={e => { setSortBy(e.target.value); setPage(1); }}>
            <option value="date_desc">Eng yangilari</option>
            <option value="date_asc">Eng eskilar</option>
            <option value="active_desc">So'nggi faollar</option>
          </select>
        </div>
      </div>

      <div className="users-list-wrapper">
        <p className="results-count">Jami: {filteredUsers.length} ta foydalanuvchi topildi</p>
        
        {loading ? (
          <div>{[1,2,3].map(i => <div key={i} className="skeleton-row mt10"></div>)}</div>
        ) : displayedUsers.length === 0 ? (
          <div className="empty-state">Topilmadi.</div>
        ) : (
          <div className="users-list">
            {displayedUsers.map(u => (
              <div key={u.telegram_id} className="user-list-item card" onClick={() => setSelectedUser(u.telegram_id)}>
                <div className="user-item-main">
                  <div className="user-avatar">
                    {u.full_name ? u.full_name.charAt(0).toUpperCase() : <User size={16}/>}
                  </div>
                  <div className="user-item-info">
                    <div className="ui-row">
                      <span className="ui-name">{u.full_name || "Noma'lum"}</span>
                      <span className="ui-badge">{u.age_group || '?'}</span>
                      <span className="ui-badge">{u.region || '?'}</span>
                    </div>
                    <div className="ui-row secondary">
                      <span>{u.phone_number || "Raqam yo'q"}</span>
                      <span>•</span>
                      <span>{u.gender === 'male' ? 'Erkak' : u.gender === 'female' ? 'Ayol' : 'Noma\'lum'}</span>
                      <span>•</span>
                      <span>{u.language === 'uz' ? "O'zbek" : u.language}</span>
                    </div>
                  </div>
                </div>
                <div className="user-item-right">
                  <div className="ui-activity">
                    <span>Oxirgi faollik</span>
                    <strong>{u.last_active?.substring(0, 10) || 'Noma\'lum'}</strong>
                  </div>
                  <ChevronRight size={20} color="var(--text-muted)" />
                </div>
              </div>
            ))}
          </div>
        )}

        {hasMore && (
          <button className="btn-load-more" onClick={() => setPage(p => p + 1)}>
            Ko'proq yuklash
          </button>
        )}
      </div>
    </div>
  );
};

export default AdminUsers;
