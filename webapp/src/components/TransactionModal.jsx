import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';

const TransactionModal = ({ isOpen, onClose }) => {
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [amountError, setAmountError] = useState('');

  useEffect(() => {
    if (!isOpen) {
      setAmount('');
      setCategory('');
      setAmountError('');
    }
  }, [isOpen]);

  const handleAmountChange = (e) => {
    const val = e.target.value;
    setAmount(val);
    
    if (val === '') {
      setAmountError('');
      return;
    }
    
    const num = parseFloat(val);
    if (num < 0) {
      setAmountError("Manfiy son bo'lishi mumkin emas");
    } else if (num === 0) {
      setAmountError("0 dan katta bo'lishi kerak");
    } else {
      setAmountError('');
    }
  };

  const handleSave = () => {
    if (!amount) {
      setAmountError('Summani kiriting');
      return;
    }
    
    const num = parseFloat(amount);
    if (num <= 0) return;
    
    const finalCategory = category.trim() === '' ? 'Boshqa xarajatlar' : category;
    
    // Placeholder action
    alert(`Tranzaksiya qo'shildi: ${amount} - ${finalCategory}`);
    onClose();
  };

  if (!isOpen) return null;

  return createPortal(
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 9999 }}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="flex-between" style={{ marginBottom: '20px' }}>
          <h2 className="title" style={{ fontSize: '20px', margin: 0 }}>Yangi tranzaksiya</h2>
          <X size={24} onClick={onClose} style={{ cursor: 'pointer', color: 'var(--text-secondary)' }} />
        </div>
        
        <div>
          <label className="subtitle" style={{ fontSize: '14px' }}>Summa</label>
          <input 
            type="number" 
            className="input-field" 
            placeholder="0" 
            value={amount}
            onChange={handleAmountChange}
            style={amountError ? { borderColor: 'var(--danger)' } : {}}
          />
          {amountError && (
            <p style={{ color: 'var(--danger)', fontSize: '12px', marginTop: '4px' }}>
              {amountError}
            </p>
          )}
        </div>

        <div style={{ marginTop: '16px' }}>
          <label className="subtitle" style={{ fontSize: '14px' }}>Kategoriya</label>
          <input 
            type="text" 
            className="input-field" 
            placeholder="Kategoriyani kiriting (ixtiyoriy)" 
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          />
        </div>

        <button 
          className="btn-primary" 
          onClick={handleSave}
          disabled={!!amountError || !amount}
          style={{ 
            opacity: (!!amountError || !amount) ? 0.5 : 1, 
            cursor: (!!amountError || !amount) ? 'not-allowed' : 'pointer' 
          }}
        >
          Saqlash
        </button>
      </div>
    </div>,
    document.body
  );
};

export default TransactionModal;

