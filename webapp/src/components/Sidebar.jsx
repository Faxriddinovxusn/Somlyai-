import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  FileText, 
  Tag, 
  CreditCard, 
  Wallet, 
  Bell,
  Users,
  ChevronRight
} from 'lucide-react';
import { useTranslation } from 'react-i18next';

const Sidebar = () => {
  const location = useLocation();
  const { t } = useTranslation();

  const mainLinks = [
    { path: '/', icon: Home, label: t('nav.dashboard', 'Bosh sahifa') },
    { path: '/stats', icon: FileText, label: t('nav.reports', 'Hisobotlar') },
    { path: '/categories', icon: Tag, label: t('nav.categories', 'Kategoriyalar') },
    { path: '/balances', icon: CreditCard, label: t('nav.balances', 'Balanslar') },
  ];

  const financeLinks = [
    { path: '/debts', icon: Wallet, label: t('nav.debts', 'Qarzlar') },
    { path: '/analytics', icon: Bell, label: t('nav.channels', 'Obuna kanallar') },
  ];

  const socialLinks = [
    { path: '/community', icon: Users, label: t('nav.community', 'Telegram guruh'), external: true },
    { path: '/notifications', icon: Bell, label: t('nav.notifications', 'Bildirishnomalar') },
  ];

  const renderLink = (link) => {
    const Icon = link.icon;
    const isActive = location.pathname === link.path;
    const linkProps = {
      className: `sidebar-link ${isActive ? 'active' : ''}`,
      title: link.label
    };

    if (link.external) {
      return (
        <a 
          key={link.path}
          href={link.path}
          target="_blank"
          rel="noopener noreferrer"
          {...linkProps}
        >
          <Icon size={20} strokeWidth={2} />
          <span>{link.label}</span>
          <ChevronRight size={16} className="sidebar-link-chevron" />
        </a>
      );
    }

    return (
      <Link 
        key={link.path} 
        to={link.path}
        {...linkProps}
      >
        <Icon size={20} strokeWidth={2} />
        <span>{link.label}</span>
      </Link>
    );
  };

  // Get user info from Telegram
  const userName = window.Telegram?.WebApp?.initDataUnsafe?.user?.first_name || 'Foydalanuvchi';
  const userLastName = window.Telegram?.WebApp?.initDataUnsafe?.user?.last_name || '';
  const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 0;
  const initials = (userName[0] + (userLastName?.[0] || '')).toUpperCase().slice(0, 2);

  return (
    <div className="sidebar">
      {/* Logo Section */}
      <div className="sidebar-logo">
        <div className="logo-image">
          <span style={{ fontSize: '18px' }}>💰</span>
        </div>
        <h1>Somly AI</h1>
      </div>

      {/* Main Section */}
      <div className="sidebar-section">
        <div className="sidebar-section-title">━━━ ASOSIY ━━━</div>
        {mainLinks.map(renderLink)}
      </div>

      {/* Finance Section */}
      <div className="sidebar-section">
        <div className="sidebar-section-title">━━━ MOLIYA ━━━</div>
        {financeLinks.map(renderLink)}
      </div>

      {/* Social Section */}
      <div className="sidebar-section">
        <div className="sidebar-section-title">━━━ IJTIMOIY ━━━</div>
        {socialLinks.map(renderLink)}
      </div>

      <div className="sidebar-spacer"></div>

      {/* Profile Section */}
      <div className="sidebar-divider"></div>
      <Link to="/settings" style={{ textDecoration: 'none' }}>
        <div className="sidebar-profile">
          <div className="avatar">{initials}</div>
          <div className="profile-info">
            <div className="profile-name">{userName} {userLastName}</div>
            <div className="profile-status">Sozlamalar</div>
          </div>
        </div>
      </Link>
    </div>
  );
};

export default Sidebar;
