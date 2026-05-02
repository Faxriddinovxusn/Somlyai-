# Mini App Excel Export Integration Guide

## 📱 Current State

The Export modal is already in `webapp/src/pages/Profile.jsx` but it's currently showing a placeholder alert. We need to connect it to the Telegram bot.

## 🔗 Integration Steps

### 1. Update the Export Modal (Profile.jsx)

Replace the existing export modal code (around line 195) with:

```jsx
{/* Export */}
{activeModal === 'export' && (
  <div className="modal-overlay" onClick={() => setActiveModal(null)}>
    <div className="modal-content" onClick={e => e.stopPropagation()}>
      <div className="flex-between" style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '20px', fontWeight: 'bold' }}>Hisobotni yuklash</h3>
        <button onClick={() => setActiveModal(null)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)' }}><X size={20}/></button>
      </div>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', fontSize: '14px' }}>Qaysi davr uchun hisobotni Excel shaklida Telegramga yuboraylik?</p>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        {[
          { label: 'Bu oy', value: 'export_this_month' },
          { label: "O'tgan oy", value: 'export_last_month' },
          { label: 'Oxirgi 3 oy', value: 'export_last_3_months' },
          { label: 'Hammasi', value: 'export_all_time' }
        ].map(period => (
          <button 
            key={period.value} 
            onClick={() => handleExportPeriod(period.value)}
            style={{ 
              padding: '16px', 
              background: 'var(--bg)', 
              border: '1px solid var(--border)', 
              borderRadius: '12px', 
              color: 'var(--text-primary)', 
              fontWeight: '600', 
              fontSize: '15px' 
            }}>
            {period.label}
          </button>
        ))}
      </div>
    </div>
  </div>
)}
```

### 2. Add Export Handler Function

Add this function to ProfilePage component:

```jsx
const handleExportPeriod = (period) => {
  try {
    if (window.Telegram?.WebApp) {
      const botWebAppUrl = window.Telegram.WebApp.initDataUnsafe?.start_param;
      
      // Send command to bot via WebApp.sendData or close and reopen
      window.Telegram.WebApp.sendData(`export_${period}`);
      
      // Show feedback
      setActiveModal(null);
      triggerAlert("✅ Buyruq botga yuborildi, kuting...");
    } else {
      triggerAlert("❌ Telegram WebApp mavjud emas");
    }
  } catch (error) {
    triggerAlert("❌ Xato: " + error.message);
  }
};
```

### 3. Alternative: Use Inline Button Approach

Instead of WebApp.sendData, use inline buttons:

```jsx
const handleExportPeriod = (period) => {
  try {
    if (window.Telegram?.WebApp) {
      // Close Mini App and show the bot's export menu
      // The bot should handle this via /excel command
      window.Telegram.WebApp.close();
      
      // Or send a deep link
      const botUsername = 'somly_ai_bot'; // Replace with actual bot username
      const deepLink = `https://t.me/${botUsername}?start=export_${period}`;
      window.open(deepLink, '_blank');
    }
  } catch (error) {
    triggerAlert("❌ Xato: " + error.message);
  }
};
```

### 4. Update Bot Handler (Optional Enhancement)

Add this to `src/handlers/export_handler.py` to handle start parameters:

```python
@router.message(Command("start"))
async def handle_start_with_export(message: Message, state: FSMContext):
    """Handle /start with export parameter."""
    args = message.text.split()
    
    if len(args) > 1 and args[1].startswith('export_'):
        # User came from Mini App export button
        period = args[1].replace('export_', '')
        await state.clear()
        
        # Map period to actual dates
        # ... then generate report
    else:
        # Regular start command
        await show_export_menu(message, state)
```

---

## 🎯 Recommended Approach

**Use the /excel command approach:**

1. User clicks "Hisobotni yuklab olish" in Mini App
2. Mini App shows period selection modal
3. User selects period
4. Mini App calls: `window.Telegram.WebApp.switchInline('/excel')`
5. Bot shows export period keyboard in chat
6. User completes export normally

---

## 🔧 JavaScript Implementation

Add this utility function to `webapp/src/utils/telegram.js` or similar:

```javascript
export const sendBotCommand = (command) => {
  if (!window.Telegram?.WebApp) {
    console.error('Telegram WebApp not available');
    return false;
  }
  
  const botUsername = 'somly_ai_bot'; // Replace with actual bot
  
  // Method 1: Switch to inline mode
  window.Telegram.WebApp.switchInline(command, true);
  
  // Method 2: Send via WebApp
  // window.Telegram.WebApp.sendData(command);
  
  return true;
};
```

Then use it in Profile.jsx:

```jsx
import { sendBotCommand } from '../utils/telegram';

const handleExportPeriod = (period) => {
  if (sendBotCommand('/excel')) {
    setActiveModal(null);
    triggerAlert("✅ Bot bilan bog'lanmoqda...");
  }
};
```

---

## 📱 Telegram WebApp API Methods

### Available Methods:
- **WebApp.switchInline(query)** - Show inline query
- **WebApp.sendData(data)** - Send data to bot
- **WebApp.close()** - Close Mini App
- **WebApp.openLink(url)** - Open external link
- **WebApp.openTelegramLink(url)** - Open Telegram link

### Data Flow:
```
Mini App (User selects period)
    ↓
JavaScript handler
    ↓
Telegram WebApp API
    ↓
Bot receives callback/command
    ↓
Bot generates Excel
    ↓
Bot sends file to user
```

---

## ✅ Testing Checklist

- [ ] Mini App loads without errors
- [ ] Export button opens modal
- [ ] Period selection buttons work
- [ ] Command reaches bot successfully
- [ ] Excel file is generated
- [ ] File is received in chat
- [ ] File is properly formatted

---

## 🚀 Future Enhancements

- Real-time progress indicator
- File preview before download
- Email export option
- Scheduled report generation
- Multiple format support (PDF, CSV)

---

**Note**: Replace `somly_ai_bot` with actual bot username/token.
