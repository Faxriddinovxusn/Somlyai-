import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import './i18n/i18n'

// Initialize Telegram Web App immediately
if (window.Telegram && window.Telegram.WebApp) {
  const tg = window.Telegram.WebApp;
  
  // Expand to full screen immediately
  tg.expand();
  
  // Enable closing confirmation
  tg.enableClosingConfirmation();
  
  // Set theme to dark
  if (tg.setHeaderColor) {
    tg.setHeaderColor('#000000');
  }
  if (tg.setBottomBarColor) {
    tg.setBottomBarColor('#000000');
  }
  
  // Prevent viewport shrinking
  let expandInterval = setInterval(() => {
    if (!tg.isExpanded) {
      tg.expand();
    }
  }, 1000);
  
  // On viewport change
  tg.onEvent('viewportChanged', () => {
    if (!tg.isExpanded) {
      tg.expand();
    }
  });
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
