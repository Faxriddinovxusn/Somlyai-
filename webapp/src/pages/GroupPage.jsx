import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Plus, Search, X, ChevronRight, Trash2, Check, ArrowRight } from 'lucide-react';
import { fetchApi } from '../utils/api';
import PageHeader from '../components/PageHeader';

const GroupPage = ({ initData }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [groups, setGroups] = useState([]);
  
  // Wizard state
  const [setupMode, setSetupMode] = useState(false);
  const [step, setStep] = useState(1);
  const [userBalances, setUserBalances] = useState([]);
  const [selectedBalances, setSelectedBalances] = useState([]);
  const [members, setMembers] = useState([]);
  const [showToast, setShowToast] = useState(false);

  // Modal state
  const [showAddMemberModal, setShowAddMemberModal] = useState(false);
  const [phoneQuery, setPhoneQuery] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState('');

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      try {
        const [groupsRes, dashRes] = await Promise.all([
          fetchApi('/groups'),
          fetchApi('/dashboard')
        ]);
        
        const grps = Array.isArray(groupsRes) && !groupsRes.error ? groupsRes : [];
        setGroups(grps);
        
        if (dashRes && dashRes.balances) {
          setUserBalances(dashRes.balances);
          // Default to all selected
          setSelectedBalances(dashRes.balances.map(b => b.currency));
        }

        if (grps.length === 0) {
          setSetupMode(true);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const toggleBalance = (currency) => {
    if (selectedBalances.includes(currency)) {
      setSelectedBalances(selectedBalances.filter(c => c !== currency));
    } else {
      setSelectedBalances([...selectedBalances, currency]);
    }
  };

  const searchUser = async () => {
    if (phoneQuery.length < 5) return;
    setSearching(true);
    setSearchError('');
    setSearchResult(null);
    try {
      const res = await fetchApi(`/groups/search-user?phone=${encodeURIComponent(phoneQuery)}`);
      if (res && !res.error) {
        setSearchResult(res);
      } else {
        setSearchError('Bu raqamda foydalanuvchi topilmadi');
      }
    } catch (e) {
      setSearchError('Bu raqamda foydalanuvchi topilmadi');
    } finally {
      setSearching(false);
    }
  };

  const handleSaveMember = () => {
    if (searchResult) {
      if (!members.find(m => m.telegram_id === searchResult.telegram_id)) {
        setMembers([...members, searchResult]);
      }
      setShowAddMemberModal(false);
      setPhoneQuery('');
      setSearchResult(null);
    }
  };

  const removeMember = (id) => {
    setMembers(members.filter(m => m.telegram_id !== id));
  };

  const finishSetup = async () => {
    // Show toast for 2 seconds
    setShowToast(true);
    setTimeout(() => {
      setShowToast(false);
    }, 2000);

    setStep(3);

    // Call backend to create group in the background
    try {
      const res = await fetchApi('/groups', {
        method: 'POST',
        body: JSON.stringify({ name: "Mening Guruhim" })
      });
      if (res && res.success && members.length > 0) {
        // Add members to the created group
        for (const m of members) {
          await fetchApi(`/groups/${res.group_id || res.id}/members`, {
            method: 'POST',
            body: JSON.stringify({ telegram_id: m.telegram_id, name: m.full_name })
          });
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="animate-fade-in" style={{ padding: '16px' }}>
        <div className="skeleton" style={{ height: '40px', marginBottom: '16px' }}></div>
        <div className="skeleton" style={{ height: '120px', borderRadius: '16px', marginBottom: '16px' }}></div>
      </div>
    );
  }

  // View Mode (If they already have a group and didn't click "Create Setup")
  if (!setupMode) {
    return (
      <div className="animate-fade-in" style={{ padding: '0 16px 100px' }}>
        <div className="flex-between" style={{ marginBottom: '20px' }}>
          <div style={{ width: '100%' }}>
            <PageHeader 
              title="Telegram guruh" 
              showLogo={true} 
              rightElement={
                <button onClick={() => setSetupMode(true)} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '50%', width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-primary)' }}>
                  <Plus size={20} />
                </button>
              }
            />
          </div>
        </div>
        {groups.map(g => (
          <div key={g.id} style={{ background: 'var(--card)', padding: '16px', borderRadius: '16px', marginBottom: '12px', border: '1px solid var(--border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '20px', background: 'rgba(10,132,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>👥</div>
              <div>
                <p style={{ fontWeight: '600', fontSize: '16px' }}>{g.name}</p>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{g.members?.length || 1} a'zo</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // WIZARD MODE
  return (
    <div className="animate-fade-in" style={{ padding: '0 16px 100px' }}>
      
      {/* Toast Notification */}
      <div style={{
        position: 'fixed', bottom: showToast ? '100px' : '-100px', left: '50%', transform: 'translateX(-50%)',
        background: 'rgba(28, 28, 30, 0.95)', border: '1px solid rgba(255,255,255,0.08)',
        backdropFilter: 'blur(10px)', padding: '12px 24px', borderRadius: '30px',
        color: '#fff', fontSize: '14px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px',
        transition: 'bottom 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)', zIndex: 1000,
        boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
      }}>
        ✅ Guruh sozlamalari saqlandi
      </div>

      {/* Header */}
      <div style={{ padding: '16px 0 8px', position: 'sticky', top: 0, background: 'var(--bg)', zIndex: 10 }}>
        <PageHeader title="Telegram guruh" showLogo={true} />
        
        {/* Progress Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
          <span style={{ fontSize: '12px', fontWeight: step >= 1 ? '600' : '400', color: step >= 1 ? '#0A84FF' : 'var(--text-secondary)' }}>1-bosqich</span>
          <div style={{ width: '6px', height: '6px', borderRadius: '3px', background: step >= 1 ? '#0A84FF' : 'var(--border)', margin: '0 4px' }} />
          <div style={{ flex: 1, height: '2px', background: step >= 2 ? '#0A84FF' : 'var(--border)', maxWidth: '40px' }} />
          <div style={{ width: '6px', height: '6px', borderRadius: '3px', background: step >= 2 ? '#0A84FF' : 'var(--border)', margin: '0 4px' }} />
          <span style={{ fontSize: '12px', fontWeight: step >= 2 ? '600' : '400', color: step >= 2 ? '#0A84FF' : 'var(--text-secondary)' }}>2-bosqich</span>
          <div style={{ flex: 1, height: '2px', background: step >= 3 ? '#0A84FF' : 'var(--border)', maxWidth: '40px' }} />
          <div style={{ width: '6px', height: '6px', borderRadius: '3px', background: step >= 3 ? '#0A84FF' : 'var(--border)', margin: '0 4px' }} />
          <span style={{ fontSize: '12px', fontWeight: step >= 3 ? '600' : '400', color: step >= 3 ? '#0A84FF' : 'var(--text-secondary)' }}>3-bosqich</span>
        </div>
      </div>

      {/* STEP 1 */}
      {step === 1 && (
        <div className="animate-fade-in" style={{ marginTop: '24px' }}>
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '8px' }}>Balanslar biriktirish</h2>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0, padding: '0 16px' }}>
              Telegram guruhida foydalanmoqchi bo'lgan balanslaringizni tanlang
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '32px' }}>
            {userBalances.map(b => {
              const isSelected = selectedBalances.includes(b.currency);
              return (
                <div 
                  key={b.currency}
                  onClick={() => toggleBalance(b.currency)}
                  style={{
                    background: isSelected ? 'rgba(10, 132, 255, 0.08)' : 'var(--card)',
                    border: `1px solid ${isSelected ? 'rgba(10, 132, 255, 0.3)' : 'var(--border)'}`,
                    borderRadius: '16px', padding: '16px', display: 'flex', alignItems: 'center', gap: '12px',
                    cursor: 'pointer', transition: 'all 0.2s'
                  }}
                >
                  <div style={{ 
                    width: '24px', height: '24px', borderRadius: '6px', 
                    background: isSelected ? '#0A84FF' : 'transparent',
                    border: isSelected ? 'none' : '2px solid var(--border)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    {isSelected && <Check size={16} color="#fff" strokeWidth={3} />}
                  </div>
                  <span style={{ fontSize: '20px' }}>{b.emoji || (b.currency === 'UZS' ? '🇺🇿' : '🇺🇸')}</span>
                  <span style={{ fontSize: '16px', fontWeight: '600', flex: 1 }}>{b.title || b.currency}</span>
                  <div style={{ width: '12px', height: '12px', borderRadius: '6px', background: b.color || '#0A84FF' }} />
                </div>
              );
            })}
          </div>

          <button 
            onClick={() => setStep(2)}
            disabled={selectedBalances.length === 0}
            style={{ 
              width: '100%', padding: '16px', background: '#0A84FF', color: '#fff', border: 'none', 
              borderRadius: '16px', fontSize: '16px', fontWeight: '600', cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
              opacity: selectedBalances.length === 0 ? 0.5 : 1
            }}
          >
            Balanslarni o'zgartirish <ArrowRight size={18} />
          </button>
        </div>
      )}

      {/* STEP 2 */}
      {step === 2 && (
        <div className="animate-fade-in" style={{ marginTop: '24px' }}>
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '8px' }}>A'zolarni biriktirish</h2>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0, padding: '0 16px' }}>
              Telegram guruhida balanslaringizga hisobot qo'shadigan guruh a'zolarini tanlang
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '24px' }}>
            {members.map(m => (
              <div key={m.telegram_id} style={{
                background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '16px', 
                padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '18px', background: 'rgba(10,132,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' }}>👤</div>
                  <span style={{ fontSize: '15px', fontWeight: '600' }}>{m.full_name}</span>
                </div>
                <button onClick={() => removeMember(m.telegram_id)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '32px', height: '32px' }}>
                  <X size={18} />
                </button>
              </div>
            ))}
          </div>

          <button 
            onClick={() => setShowAddMemberModal(true)}
            style={{ 
              width: '100%', padding: '16px', background: 'transparent', color: '#0A84FF', 
              border: '1px dashed rgba(10, 132, 255, 0.5)', borderRadius: '16px', fontSize: '15px', 
              fontWeight: '600', cursor: 'pointer', marginBottom: '32px'
            }}
          >
            + Guruhga a'zolarni qo'shish
          </button>

          <button 
            onClick={finishSetup}
            style={{ 
              width: '100%', padding: '16px', background: '#0A84FF', color: '#fff', border: 'none', 
              borderRadius: '16px', fontSize: '16px', fontWeight: '600', cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'
            }}
          >
            Bosqichni yakunlash <ArrowRight size={18} />
          </button>
        </div>
      )}

      {/* STEP 3 */}
      {step === 3 && (
        <div className="animate-fade-in" style={{ marginTop: '40px', textAlign: 'center' }}>
          <div style={{ 
            width: '80px', height: '80px', borderRadius: '40px', background: 'rgba(48, 209, 88, 0.1)', 
            display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px',
            color: '#30D158'
          }}>
            <Check size={40} strokeWidth={3} />
          </div>
          
          <h2 style={{ fontSize: '18px', color: '#30D158', fontWeight: '600', marginBottom: '16px' }}>
            Guruh muvaffaqiyatli yaratildi!
          </h2>
          
          <h1 style={{ fontSize: '24px', fontWeight: '800', marginBottom: '12px', lineHeight: '1.2' }}>
            Telegram guruh yarating,<br/>Somly AI bot'ni qo'shing
          </h1>
          
          <p style={{ fontSize: '15px', color: 'var(--text-secondary)', lineHeight: '1.6', marginBottom: '40px', padding: '0 16px' }}>
            Yaratilgan telegram guruhiga Somly AI bot'ni admin qilib tayinlang. So'ng Somly AI bot guruhida barcha hisobotlarni o'sha yig'ib boradi
          </p>

          <button 
            onClick={() => navigate('/')}
            style={{ 
              width: '100%', padding: '16px', background: '#0A84FF', color: '#fff', border: 'none', 
              borderRadius: '16px', fontSize: '16px', fontWeight: '600', cursor: 'pointer'
            }}
          >
            Bosh sahifaga qaytish
          </button>
        </div>
      )}

      {/* ODAM QO'SHISH MODAL */}
      {showAddMemberModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'flex-end', zIndex: 2000
        }} onClick={() => setShowAddMemberModal(false)}>
          <div style={{
            background: 'var(--card)', width: '100%', borderRadius: '24px 24px 0 0', padding: '24px',
          }} onClick={e => e.stopPropagation()}>
            <div className="flex-between" style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '20px', fontWeight: '700' }}>ODAM QO'SHISH</h3>
              <button onClick={() => setShowAddMemberModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)' }}><X size={24} /></button>
            </div>

            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '20px', lineHeight: '1.5' }}>
              Guruh a'zosi qo'shish uchun telefon raqami bo'yicha qidiring
            </p>

            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
              <div style={{ flex: 1, position: 'relative' }}>
                <Search size={18} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                <input 
                  type="tel" 
                  placeholder="Foydalanuvchini qidiring..." 
                  value={phoneQuery} 
                  onChange={e => setPhoneQuery(e.target.value)}
                  style={{ 
                    width: '100%', padding: '14px 14px 14px 40px', background: 'var(--bg)', 
                    border: '1px solid var(--border)', borderRadius: '14px', color: '#fff', fontSize: '15px', outline: 'none' 
                  }} 
                />
              </div>
              <button 
                onClick={searchUser} 
                disabled={phoneQuery.length < 5 || searching} 
                style={{ 
                  padding: '0 20px', background: '#0A84FF', color: '#fff', border: 'none', 
                  borderRadius: '14px', fontWeight: '600', cursor: 'pointer', opacity: phoneQuery.length < 5 ? 0.5 : 1 
                }}
              >
                {searching ? '...' : 'Qidirish'}
              </button>
            </div>

            {searchError && (
              <div style={{ textAlign: 'center', padding: '16px', color: '#FF453A', fontSize: '14px', fontWeight: '500', marginBottom: '24px' }}>
                {searchError}
              </div>
            )}

            {searchResult && (
              <div style={{ 
                padding: '16px', background: 'rgba(10, 132, 255, 0.08)', border: '1px solid rgba(10, 132, 255, 0.2)', 
                borderRadius: '16px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' 
              }}>
                <div style={{ width: '40px', height: '40px', borderRadius: '20px', background: '#0A84FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '18px' }}>
                  👤
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ fontSize: '16px', fontWeight: '600', color: '#fff' }}>{searchResult.full_name}</p>
                </div>
                <Check size={24} color="#0A84FF" />
              </div>
            )}

            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setShowAddMemberModal(false)} style={{ flex: 1, padding: '16px', background: 'var(--bg)', border: 'none', borderRadius: '16px', color: '#fff', fontWeight: '600', fontSize: '15px' }}>
                Bekor qilish
              </button>
              <button onClick={handleSaveMember} disabled={!searchResult} style={{ flex: 1, padding: '16px', background: searchResult ? '#0A84FF' : 'var(--border)', color: '#fff', border: 'none', borderRadius: '16px', fontWeight: '600', fontSize: '15px', opacity: searchResult ? 1 : 0.5 }}>
                Saqlash
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GroupPage;
