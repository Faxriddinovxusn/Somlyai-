import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const PageHeader = ({ title, showBack = true, showLogo = false, rightElement = null }) => {
  const navigate = useNavigate();

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      marginBottom: '24px', gap: '12px', minHeight: '40px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, minWidth: 0 }}>
        {showBack && (
          <button
            onClick={() => navigate(-1)}
            className="clickable"
            style={{
              background: 'var(--card)', border: '1px solid var(--border)', color: 'var(--text-primary)',
              width: '36px', height: '36px', borderRadius: '18px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', flexShrink: 0, transition: 'all 0.2s'
            }}
          >
            <ArrowLeft size={20} />
          </button>
        )}
        <h1 style={{
          fontSize: '20px', fontWeight: '700', margin: 0,
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'
        }}>
          {title}
        </h1>
      </div>
      {rightElement && <div style={{ flexShrink: 0 }}>{rightElement}</div>}
    </div>
  );
};

export default PageHeader;
