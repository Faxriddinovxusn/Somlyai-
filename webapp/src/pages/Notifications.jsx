import React from 'react';
import { Bell, ShieldAlert, Sparkles, AlertTriangle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import PageHeader from '../components/PageHeader';

const NotificationsPage = ({ initData }) => {
  const { t } = useTranslation();
  
  // Dummy data for premium look
  const notificationsList = [
    {
      id: 1,
      type: 'system',
      title: 'Xush kelibsiz! 🎉',
      message: 'Somly AI ga xush kelibsiz. Moliyangizni aqlli boshqarishni bugundan boshlang.',
      time: 'Yangi',
      icon: Sparkles,
      color: 'var(--primary)'
    },
    {
      id: 2,
      type: 'alert',
      title: 'Balans tavsiyasi',
      message: 'Ushbu haftada "Oziq-ovqat" uchun harajatingiz o\'tgan haftaga nisbatan 20% ga oshdi.',
      time: '2 soat oldin',
      icon: AlertTriangle,
      color: 'var(--warning)'
    },
    {
      id: 3,
      type: 'success',
      title: 'Ma\'lumotlar sinxronlandi',
      message: 'Barcha yangi tranzaksiyalar muvaffaqiyatli bulutli bazaga saqlandi.',
      time: 'Kecha',
      icon: CheckCircle2,
      color: 'var(--success)'
    }
  ];

  return (
    <div className="page-container" style={{ padding: '20px', paddingBottom: '100px' }}>
      <header style={{ marginBottom: '24px' }}>
        <PageHeader title="Bildirishnomalar" showLogo={true} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '15px' }}>
          Muhim xabarlar va tizim yangiliklari
        </p>
      </header>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {notificationsList.map(notif => {
          const Icon = notif.icon;
          return (
            <div key={notif.id} className="glass-card" style={{ 
              padding: '16px', 
              borderRadius: '20px',
              display: 'flex',
              gap: '16px',
              alignItems: 'flex-start',
              position: 'relative',
              overflow: 'hidden'
            }}>
              {/* Type Indicator */}
              <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: notif.color }}></div>
              
              <div style={{ 
                width: 44, height: 44, borderRadius: '12px', 
                background: `color-mix(in srgb, ${notif.color} 15%, transparent)`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
              }}>
                <Icon size={22} color={notif.color} />
              </div>
              
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff', margin: 0 }}>{notif.title}</h3>
                  <span style={{ fontSize: '12px', color: 'var(--text-secondary)', whiteSpace: 'nowrap', marginLeft: '10px' }}>{notif.time}</span>
                </div>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>
                  {notif.message}
                </p>
              </div>
            </div>
          );
        })}
      </div>
      
      <div style={{ marginTop: '24px', textAlign: 'center' }}>
        <button style={{
          background: 'transparent', border: 'none', color: 'var(--text-secondary)',
          fontSize: '14px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px', margin: '0 auto', cursor: 'pointer'
        }}>
          Barcha xabarlarni o'qilgan deb belgilash <ShieldAlert size={14} />
        </button>
      </div>
    </div>
  );
};

export default NotificationsPage;
