import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, PieChart, CreditCard, User, Tags } from 'lucide-react';
import DashboardPage from './pages/Dashboard';
import BalancesPage from './pages/Balances';
import StatisticsPage from './pages/Statistics';
import ProfilePage from './pages/Profile';
import CategoriesPage from './pages/Categories';

const App = () => {
  const [initData, setInitData] = useState('');

  useEffect(() => {
    // Telegram Web App SDK init
    if (window.Telegram && window.Telegram.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.expand(); // Expand to full screen
      setInitData(tg.initData);
    }
  }, []);

  return (
    <BrowserRouter>
      <div className="app-container">
        <div style={{ padding: '20px' }}>
          <Routes>
            <Route path="/" element={<DashboardPage initData={initData} />} />
            <Route path="/balances" element={<BalancesPage initData={initData} />} />
            <Route path="/stats" element={<StatisticsPage initData={initData} />} />
            <Route path="/categories" element={<CategoriesPage initData={initData} />} />
            <Route path="/profile" element={<ProfilePage initData={initData} />} />
          </Routes>
        </div>
        <BottomNav />
      </div>
    </BrowserRouter>
  );
};

const BottomNav = () => {
  const location = useLocation();
  
  return (
    <div className="bottom-nav">
      <Link to="/" className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}>
        <Home size={24} />
        <span>Bosh sahifa</span>
      </Link>
      <Link to="/stats" className={`nav-item ${location.pathname === '/stats' ? 'active' : ''}`}>
        <PieChart size={24} />
        <span>Hisobot</span>
      </Link>
      <Link to="/balances" className={`nav-item ${location.pathname === '/balances' ? 'active' : ''}`}>
        <CreditCard size={24} />
        <span>Balans</span>
      </Link>
      <Link to="/categories" className={`nav-item ${location.pathname === '/categories' ? 'active' : ''}`}>
        <Tags size={24} />
        <span>Kategoriya</span>
      </Link>
      <Link to="/profile" className={`nav-item ${location.pathname === '/profile' ? 'active' : ''}`}>
        <User size={24} />
        <span>Profil</span>
      </Link>
    </div>
  );
};

export default App;
