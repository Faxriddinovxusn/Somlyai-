import React from 'react';

export const SkeletonCard = () => (
  <div className="card animate-fade-in" style={{ padding: '24px' }}>
    <div className="flex-between" style={{ marginBottom: '16px' }}>
      <div className="skeleton" style={{ width: '120px', height: '20px' }}></div>
      <div className="skeleton" style={{ width: '40px', height: '40px', borderRadius: '50%' }}></div>
    </div>
    <div className="skeleton" style={{ width: '200px', height: '36px', marginBottom: '8px' }}></div>
    <div className="skeleton" style={{ width: '150px', height: '16px' }}></div>
  </div>
);

export const SkeletonList = ({ count = 3 }) => {
  return (
    <div className="animate-fade-in">
      {[...Array(count)].map((_, i) => (
        <div key={i} className="flex-between" style={{ padding: '16px 0', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="skeleton" style={{ width: '48px', height: '48px', borderRadius: '12px' }}></div>
            <div>
              <div className="skeleton" style={{ width: '120px', height: '16px', marginBottom: '8px' }}></div>
              <div className="skeleton" style={{ width: '80px', height: '14px' }}></div>
            </div>
          </div>
          <div className="skeleton" style={{ width: '60px', height: '20px' }}></div>
        </div>
      ))}
    </div>
  );
};
