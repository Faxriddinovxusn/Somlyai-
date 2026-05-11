import React, { useState, useEffect } from 'react';
import { Plus, Trash2, ExternalLink, ShieldAlert, ShieldCheck, Users, Activity, X } from 'lucide-react';

const AdminChannels = ({ token, navigateTo }) => {
  const [channels, setChannels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => { fetchChannels(); }, []);

  const fetchChannels = async () => {
    try {
      const res = await fetch('/api/admin/channels/extended', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setChannels(await res.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const addChannel = async () => {
    if (!newUsername.trim()) {
      setErrorMsg("Kanal username kiritilishi shart!");
      return;
    }
    setSaving(true);
    setErrorMsg('');
    try {
      const res = await fetch('/api/admin/channels/verify_add', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: newUsername.trim() }),
      });
      const data = await res.json();
      if (data.success) {
        setNewUsername(''); 
        setShowAddModal(false);
        setLoading(true);
        await fetchChannels();
      } else {
        setErrorMsg(data.error || "Noma'lum xatolik");
      }
    } catch (e) { 
      setErrorMsg(e.message);
    }
    setSaving(false);
  };

  const deleteChannel = async (id) => {
    if (!confirm('Bu kanalni o\'chirishga ishonchingiz komilmi?')) return;
    try {
      await fetch(`/api/admin/channels/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      await fetchChannels();
    } catch (e) { console.error(e); }
  };

  if (loading) {
    return (
      <div className="admin-page">
        <h1 className="page-title">📢 Kanallar</h1>
        <div className="skeleton-table">{[1,2,3].map(i => <div key={i} className="skeleton-row" style={{height: '100px'}} />)}</div>
      </div>
    );
  }

  return (
    <div className="admin-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">📢 Obuna kerakli kanallar</h1>
          <p className="page-subtitle">Jami: {channels.length} ta kanal ulangan</p>
        </div>
        <button className="btn-primary" onClick={() => {setShowAddModal(true); setErrorMsg('');}}>
          <Plus size={18} /> Yangi kanal qo'shish
        </button>
      </div>

      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-content add-channel-modal">
            <div className="modal-header">
              <h3>Kanal qo'shish</h3>
              <button className="btn-icon" onClick={() => setShowAddModal(false)}><X size={20}/></button>
            </div>
            <div className="modal-body">
              <p className="mb10">Kanal username'sini kiriting (faqat ommaviy kanallar):</p>
              <input
                className="w-full input-field"
                placeholder="@kanal_username"
                value={newUsername}
                onChange={e => setNewUsername(e.target.value)}
                disabled={saving}
              />
              
              {errorMsg && (
                <div className="alert-box error mt10">
                  <strong>⚠️ Xatolik</strong>
                  <p>{errorMsg}</p>
                  {errorMsg.includes("admin emas") && (
                    <ol className="mt10 pl20">
                      <li>Kanalga kiring</li>
                      <li>Adminlar → Botni qo'shish</li>
                      <li>Keyin qayta urinib ko'ring</li>
                    </ol>
                  )}
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowAddModal(false)} disabled={saving}>Bekor qilish</button>
              <button className="btn-primary" onClick={addChannel} disabled={saving}>
                {saving ? <span className="spinner"></span> : '✅ Qo\'shish'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="channels-grid mt20">
        {channels.length === 0 ? (
          <div className="card empty-state" style={{gridColumn: '1 / -1'}}>
            <p>Hozircha kanallar yo'q</p>
            <button className="btn-primary" onClick={() => setShowAddModal(true)}>
              <Plus size={18} /> Birinchi kanalni qo'shing
            </button>
          </div>
        ) : (
          channels.map((ch, i) => (
            <div className="card channel-ext-card" key={ch.id}>
              <div className="channel-ext-header">
                <div className="channel-ext-title">
                  <span className="channel-num">{i + 1}</span>
                  <div>
                    <h3>{ch.name}</h3>
                    <a href={ch.link} target="_blank" rel="noopener noreferrer" className="channel-link">
                      {ch.username} <ExternalLink size={12} />
                    </a>
                  </div>
                </div>
                <button className="btn-danger-sm" onClick={() => deleteChannel(ch.id)} title="O'chirish">
                  <Trash2 size={16} />
                </button>
              </div>
              
              <div className="channel-ext-stats mt15">
                <div className="stat-row">
                  <span className="stat-label"><Users size={14}/> Obunachilar:</span>
                  <span className="stat-value">{ch.member_count.toLocaleString()}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label"><ShieldAlert size={14}/> Bot admin:</span>
                  <span className="stat-value">
                    {ch.is_admin ? <span className="badge success"><ShieldCheck size={12}/> Ha</span> : <span className="badge danger">Yo'q</span>}
                  </span>
                </div>
                <div className="stat-row">
                  <span className="stat-label"><Activity size={14}/> Bot orqali (tahminiy):</span>
                  <span className="stat-value">{ch.conversion}% ({ch.joined_via_bot})</span>
                </div>
              </div>
              
              <button 
                className="btn-secondary w-full mt15" 
                onClick={() => navigateTo('channel-stats', { channelLink: ch.link, channelName: ch.name })}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              >
                <Activity size={16} /> Batafsil Statistika
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AdminChannels;
