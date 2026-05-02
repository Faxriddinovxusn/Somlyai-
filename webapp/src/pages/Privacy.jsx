import React from 'react';
import { Shield, ArrowLeft, Lock, Eye, Server, MessageCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';

const PrivacyPage = () => {
  const navigate = useNavigate();

  return (
    <div className="animate-fade-in" style={{ padding: '0 16px 100px', paddingTop: '16px', maxWidth: '800px', margin: '0 auto' }}>
      
      {/* Header */}
      <PageHeader title="Maxfiylik siyosati" showLogo={true} showBack={true} />

      {/* Shield Icon */}
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <div style={{ 
          width: '80px', height: '80px', borderRadius: '40px', 
          background: 'linear-gradient(135deg, rgba(10,132,255,0.2) 0%, rgba(48,209,88,0.2) 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', 
          margin: '0 auto 16px', border: '1px solid rgba(48,209,88,0.3)'
        }}>
          <Shield size={40} color="#30D158" />
        </div>
        <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#fff', margin: '0 0 8px' }}>Somly AI Maxfiylik Siyosati</h2>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', margin: 0 }}>Sizning xavfsizligingiz — bizning ustuvorligimiz</p>
      </div>

      {/* Main Content */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

        {/* Section 1 */}
        <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '20px', padding: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <div style={{ background: 'rgba(48,209,88,0.15)', padding: '10px', borderRadius: '12px' }}>
              <Lock size={20} color="#30D158" />
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#fff', margin: 0 }}>Moliyaviy ma'lumotlar</h3>
          </div>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.7', margin: 0 }}>
            Somly AI siz ishonib topshirgan moliyaviy ma'lumotlaringizni — kirim, chiqim va qarz 
            ma'lumotlarini — <strong style={{ color: '#fff' }}>hech qachon kuzatmaydi</strong>, tahlil qilmaydi 
            yoki uchinchi shaxslarga taqdim etmaydi.
          </p>
        </div>

        {/* Section 2 */}
        <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '20px', padding: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <div style={{ background: 'rgba(10,132,255,0.15)', padding: '10px', borderRadius: '12px' }}>
              <Eye size={20} color="#0A84FF" />
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#fff', margin: 0 }}>Saqlanadigan ma'lumotlar</h3>
          </div>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.7', marginBottom: '12px' }}>
            Biz faqatgina quyidagi umumiy ma'lumotlarni saqlaymiz:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {['Yoshingiz', 'Joylashuvingiz (viloyat/davlat)', 'Telegram ism va raqamingiz'].map((item, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                <div style={{ width: '6px', height: '6px', borderRadius: '3px', background: '#0A84FF', flexShrink: 0 }} />
                <span style={{ fontSize: '14px', color: '#fff' }}>{item}</span>
              </div>
            ))}
          </div>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', marginTop: '12px', marginBottom: 0 }}>
            Ushbu ma'lumotlar faqatgina sizga samarali va maqsadli reklama ko'rsatish maqsadida ishlatiladi.
          </p>
        </div>

        {/* Section 3 */}
        <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '20px', padding: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <div style={{ background: 'rgba(191,90,242,0.15)', padding: '10px', borderRadius: '12px' }}>
              <Server size={20} color="#BF5AF2" />
            </div>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#fff', margin: 0 }}>Xavfsizlik</h3>
          </div>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.7', margin: 0 }}>
            Ma'lumotlaringiz <strong style={{ color: '#fff' }}>hech qachon, hech qayerga sotilmaydi</strong>. 
            Barcha ma'lumotlar xavfsiz serverlarimizda muhofaza ostida saqlanadi.
          </p>
        </div>

        {/* Contact */}
        <div style={{ 
          background: 'linear-gradient(135deg, rgba(10,132,255,0.1) 0%, rgba(90,200,250,0.1) 100%)', 
          borderRadius: '20px', padding: '20px', 
          border: '1px solid rgba(10,132,255,0.2)',
          textAlign: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginBottom: '12px' }}>
            <MessageCircle size={20} color="#0A84FF" />
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#fff', margin: 0 }}>Shikoyat va takliflar</h3>
          </div>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.6', margin: '0 0 16px' }}>
            Har qanday savol, shikoyat yoki takliflar uchun biz bilan bog'laning:
          </p>
          <button 
            onClick={() => window.Telegram?.WebApp?.openTelegramLink('https://t.me/XusniddinWR') || window.open('https://t.me/XusniddinWR', '_blank')}
            style={{ 
              background: '#0A84FF', color: '#fff', border: 'none', 
              padding: '12px 24px', borderRadius: '14px', 
              fontSize: '15px', fontWeight: '600', cursor: 'pointer'
            }}
          >
            @XusniddinWR ga yozish
          </button>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPage;
