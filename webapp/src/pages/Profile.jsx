import React from 'react';
import { User, Settings, CreditCard, Tag, Bell, Download, Trash2, BookOpen, MessageCircle, FileText, Shield, Globe, ChevronRight } from 'lucide-react';

const ProfilePage = ({ initData }) => {
  const menuGroups = [
    {
      title: "Asosiy",
      items: [
        { icon: <User size={20} />, label: "Profilni tahrirlash", color: "var(--primary)" },
        { icon: <CreditCard size={20} />, label: "Balanslar", color: "var(--success)" },
        { icon: <Tag size={20} />, label: "Kategoriyalar", color: "var(--warning)" },
        { icon: <Bell size={20} />, label: "Bildirishnomalar", color: "var(--danger)" },
      ]
    },
    {
      title: "Ma'lumotlar",
      items: [
        { icon: <Download size={20} />, label: "Hisobotni yuklab olish", color: "#AF52DE" },
        { icon: <Trash2 size={20} />, label: "Hisobotlarni tozalash", color: "var(--danger)" },
      ]
    },
    {
      title: "Yordam va Boshqa",
      items: [
        { icon: <BookOpen size={20} />, label: "Foydalanish yo'riqnomasi", color: "var(--text-secondary)" },
        { icon: <MessageCircle size={20} />, label: "Qo'llab-quvvatlash", color: "var(--primary)" },
        { icon: <FileText size={20} />, label: "Bizning shartlar", color: "var(--text-secondary)" },
        { icon: <Shield size={20} />, label: "Maxfiylik siyosati", color: "var(--text-secondary)" },
        { icon: <Globe size={20} />, label: "Tilni o'zgartirish", color: "var(--text-secondary)" },
      ]
    }
  ];

  return (
    <div className="animate-fade-in">
      <h1 className="title" style={{ marginBottom: '24px' }}>Profil</h1>

      {/* User Card */}
      <div className="card flex-between" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ 
            width: '60px', height: '60px', borderRadius: '30px', 
            background: 'linear-gradient(135deg, var(--primary) 0%, #AF52DE 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '24px', fontWeight: 'bold'
          }}>
            A
          </div>
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: '700' }}>Ali Valiyev</h2>
            <p style={{ color: 'var(--success)', fontSize: '14px', marginTop: '4px', fontWeight: '500' }}>Pro Obuna</p>
          </div>
        </div>
        <button style={{ padding: '8px 16px', borderRadius: '20px', background: 'rgba(10, 132, 255, 0.1)', color: 'var(--primary)', border: 'none', fontWeight: '600' }}>
          Tahrirlash
        </button>
      </div>

      {/* Menu Groups */}
      {menuGroups.map((group, gIdx) => (
        <div key={gIdx} style={{ marginBottom: '24px' }}>
          <p className="subtitle" style={{ marginLeft: '16px', marginBottom: '8px', fontSize: '13px', textTransform: 'uppercase' }}>
            {group.title}
          </p>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            {group.items.map((item, iIdx) => (
              <div key={item.label}>
                <div className="flex-between" style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{ 
                      width: '32px', height: '32px', borderRadius: '8px', 
                      backgroundColor: item.color, display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: 'white'
                    }}>
                      {React.cloneElement(item.icon, { size: 18, color: 'white' })}
                    </div>
                    <span style={{ fontSize: '16px', fontWeight: '500' }}>{item.label}</span>
                  </div>
                  <ChevronRight size={20} className="text-secondary" />
                </div>
                {iIdx < group.items.length - 1 && (
                  <div style={{ height: '1px', backgroundColor: 'var(--border)', marginLeft: '64px' }}></div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
      
      <div style={{ textAlign: 'center', marginTop: '32px', marginBottom: '20px' }}>
        <p className="text-secondary" style={{ fontSize: '13px' }}>Somly AI v1.0.0</p>
      </div>
    </div>
  );
};

export default ProfilePage;
