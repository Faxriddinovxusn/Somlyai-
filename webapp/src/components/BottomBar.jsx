import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, FileText, Plus, Wallet, Settings } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const BottomBar = ({ onAddClick }) => {
  const location = useLocation();
  const { t } = useTranslation();
  const [iconSize, setIconSize] = useState(22);
  const [plusSize, setPlusSize] = useState(28);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 480) {
        setIconSize(24);
        setPlusSize(32);
      } else {
        setIconSize(22);
        setPlusSize(28);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const navItems = [
    { path: '/', icon: Home, label: t('nav.dashboard', 'Bosh sahifa') },
    { path: '/stats', icon: FileText, label: t('nav.reports', 'Hisobotlar') },
    null, // Placeholder for center button
    { path: '/debts', icon: Wallet, label: t('nav.debts', 'Qarzlar') },
    { path: '/profile', icon: Settings, label: t('nav.settings', 'Sozlamalar') },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="bottom-nav">
      {/* Left items */}
      <Link to="/" className={`nav-item ${isActive('/') ? 'active' : ''}`} title={t('nav.dashboard', 'Bosh sahifa')}>
        <Home size={iconSize} strokeWidth={2} />
        <span>Bosh</span>
      </Link>

      <Link to="/stats" className={`nav-item ${isActive('/stats') ? 'active' : ''}`} title={t('nav.reports', 'Hisobotlar')}>
        <FileText size={iconSize} strokeWidth={2} />
        <span>Hisobot</span>
      </Link>

      {/* Center Add Button */}
      <div className="nav-item-add">
        <button 
          className="add-button" 
          onClick={onAddClick}
          title={t('nav.add', 'Yangi tranzaksiya')}
          aria-label={t('nav.add', 'Yangi tranzaksiya')}
        >
          <Plus size={plusSize} strokeWidth={2.5} />
        </button>
      </div>

      {/* Right items */}
      <Link to="/debts" className={`nav-item ${isActive('/debts') ? 'active' : ''}`} title={t('nav.debts', 'Qarzlar')}>
        <Wallet size={iconSize} strokeWidth={2} />
        <span>Qarz</span>
      </Link>

      <Link to="/profile" className={`nav-item ${isActive('/profile') ? 'active' : ''}`} title={t('nav.settings', 'Sozlamalar')}>
        <Settings size={iconSize} strokeWidth={2} />
        <span>Sozl</span>
      </Link>
    </div>
  );
};

export default BottomBar;
