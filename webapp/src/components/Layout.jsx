import React, { useState } from 'react';
import Sidebar from './Sidebar';
import BottomBar from './BottomBar';
import TransactionModal from './TransactionModal';

const Layout = ({ children }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleAddClick = () => {
    setIsModalOpen(true);
  };

  return (
    <div className="app-wrapper">
      <Sidebar />
      <div className="app-container">
        <main className="main-content">
          {children}
        </main>
      </div>
      <BottomBar onAddClick={handleAddClick} />
      <TransactionModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
};

export default Layout;
