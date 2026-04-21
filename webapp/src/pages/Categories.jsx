import React, { useState, useEffect } from 'react';
import { Tags, Plus, Trash2, ChevronDown, ChevronRight, X } from 'lucide-react';

const CategoriesPage = ({ initData }) => {
  const [systemCategories, setSystemCategories] = useState([]);
  const [customCategories, setCustomCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Accordion state
  const [showCustom, setShowCustom] = useState(true);
  const [showSystem, setShowSystem] = useState(false);
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCatName, setNewCatName] = useState('');
  const [newCatEmoji, setNewCatEmoji] = useState('💰');
  const [newCatType, setNewCatType] = useState('chiqim');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 8732138574; // Fallback for dev

  const fetchCategories = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/categories?user_id=${userId}`);
      if (response.ok) {
        const data = await response.json();
        setSystemCategories(data.system || []);
        setCustomCategories(data.custom || []);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleCreateCategory = async (e) => {
    e.preventDefault();
    if (!newCatName || !newCatEmoji) return;
    
    setIsSubmitting(true);
    try {
      const response = await fetch('http://localhost:8000/api/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          name: newCatName,
          emoji: newCatEmoji,
          type: newCatType
        })
      });
      
      if (response.ok) {
        await fetchCategories();
        setIsModalOpen(false);
        setNewCatName('');
        setNewCatEmoji('💰');
      }
    } catch (error) {
      console.error('Error creating category:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteCategory = async (catId) => {
    if (!window.confirm("Bu kategoriyani o'chirmoqchimisiz?")) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/categories/${catId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        await fetchCategories();
      }
    } catch (error) {
      console.error('Error deleting category:', error);
    }
  };

  const renderTypeLabel = (type) => {
    switch(type) {
      case 'kirim': return <span style={{color: 'var(--success)', fontSize: '12px'}}>Kirim</span>;
      case 'chiqim': return <span style={{color: 'var(--danger)', fontSize: '12px'}}>Chiqim</span>;
      default: return <span style={{color: 'var(--warning)', fontSize: '12px'}}>Har ikkalasi</span>;
    }
  };

  if (loading) {
    return (
      <div className="animate-fade-in">
        <div className="skeleton" style={{ height: '60px', marginBottom: '16px' }}></div>
        <div className="skeleton" style={{ height: '200px', marginBottom: '16px' }}></div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ paddingBottom: '80px' }}>
      <div className="flex-between" style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '800', margin: 0 }}>Kategoriyalar</h1>
        <button 
          onClick={() => setIsModalOpen(true)}
          style={{
            background: 'var(--primary)',
            color: 'white',
            border: 'none',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer'
          }}
        >
          <Plus size={24} />
        </button>
      </div>

      {/* Custom Categories Accordion */}
      <div className="card" style={{ marginBottom: '16px', padding: 0, overflow: 'hidden' }}>
        <div 
          onClick={() => setShowCustom(!showCustom)}
          className="flex-between" 
          style={{ padding: '16px', cursor: 'pointer', background: 'rgba(255,255,255,0.02)' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(10, 132, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Tags size={18} color="var(--primary)" />
            </div>
            <h2 style={{ fontSize: '16px', margin: 0, fontWeight: '600' }}>
              Shaxsiy kategoriyalar ({customCategories.length} ta)
            </h2>
          </div>
          {showCustom ? <ChevronDown size={20} className="text-secondary" /> : <ChevronRight size={20} className="text-secondary" />}
        </div>
        
        {showCustom && (
          <div style={{ padding: '0 16px 16px 16px' }}>
            {customCategories.length === 0 ? (
              <p className="subtitle" style={{ textAlign: 'center', padding: '20px 0', fontSize: '14px' }}>
                Hali shaxsiy kategoriyalar yo'q. Yangi qo'shing!
              </p>
            ) : (
              customCategories.map(cat => (
                <div key={cat.id} className="flex-between" style={{ padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontSize: '24px' }}>{cat.emoji}</span>
                    <div>
                      <p style={{ margin: 0, fontWeight: '500' }}>{cat.name}</p>
                      {renderTypeLabel(cat.type)}
                    </div>
                  </div>
                  <button 
                    onClick={() => handleDeleteCategory(cat.id)}
                    style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', padding: '8px' }}
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* System Categories Accordion */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div 
          onClick={() => setShowSystem(!showSystem)}
          className="flex-between" 
          style={{ padding: '16px', cursor: 'pointer', background: 'rgba(255,255,255,0.02)' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(48, 209, 88, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Tags size={18} color="var(--success)" />
            </div>
            <h2 style={{ fontSize: '16px', margin: 0, fontWeight: '600' }}>
              Qo'shimcha kategoriyalar ({systemCategories.length} ta)
            </h2>
          </div>
          {showSystem ? <ChevronDown size={20} className="text-secondary" /> : <ChevronRight size={20} className="text-secondary" />}
        </div>
        
        {showSystem && (
          <div style={{ padding: '0 16px 16px 16px', maxHeight: '400px', overflowY: 'auto' }}>
            {systemCategories.map((cat, idx) => (
              <div key={idx} className="flex-between" style={{ padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '24px' }}>{cat.emoji}</span>
                  <div>
                    <p style={{ margin: 0, fontWeight: '500' }}>{cat.name}</p>
                    {renderTypeLabel(cat.type)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {isModalOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)', zIndex: 1000,
          display: 'flex', alignItems: 'flex-end', justifyContent: 'center'
        }}>
          <div className="animate-slide-up" style={{
            background: 'var(--bg-secondary)', width: '100%', maxWidth: '500px',
            borderTopLeftRadius: '24px', borderTopRightRadius: '24px',
            padding: '24px', paddingBottom: '40px'
          }}>
            <div className="flex-between" style={{ marginBottom: '20px' }}>
              <h2 style={{ margin: 0, fontSize: '20px' }}>Yangi kategoriya</h2>
              <button onClick={() => setIsModalOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)' }}>
                <X size={24} />
              </button>
            </div>
            
            <form onSubmit={handleCreateCategory}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--text-secondary)' }}>Emoji</label>
                <input 
                  type="text" 
                  value={newCatEmoji}
                  onChange={e => setNewCatEmoji(e.target.value)}
                  maxLength={2}
                  style={{ width: '60px', padding: '12px', fontSize: '24px', textAlign: 'center', background: 'var(--bg-primary)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: 'white' }}
                  required
                />
              </div>
              
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--text-secondary)' }}>Nom</label>
                <input 
                  type="text" 
                  value={newCatName}
                  onChange={e => setNewCatName(e.target.value)}
                  placeholder="Kategoriya nomi"
                  style={{ width: '100%', padding: '16px', background: 'var(--bg-primary)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: 'white', fontSize: '16px' }}
                  required
                />
              </div>
              
              <div style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--text-secondary)' }}>Tur</label>
                <select 
                  value={newCatType}
                  onChange={e => setNewCatType(e.target.value)}
                  style={{ width: '100%', padding: '16px', background: 'var(--bg-primary)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: 'white', fontSize: '16px', appearance: 'none' }}
                >
                  <option value="chiqim">Chiqim</option>
                  <option value="kirim">Kirim</option>
                  <option value="both">Har ikkalasi</option>
                </select>
              </div>
              
              <button 
                type="submit" 
                disabled={isSubmitting}
                style={{
                  width: '100%', padding: '16px', background: 'var(--primary)', color: 'white',
                  border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: 'bold',
                  opacity: isSubmitting ? 0.7 : 1
                }}
              >
                {isSubmitting ? 'Qo\'shilmoqda...' : 'Qo\'shish'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CategoriesPage;
