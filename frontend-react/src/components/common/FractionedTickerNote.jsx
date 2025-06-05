import React from 'react';

const FractionedTickerNote = ({ className = '' }) => {
  return (
    <div 
      className={`${className}`}
      style={{
        backgroundColor: '#2e502f',
        color: 'white',
        borderLeft: '4px solid #4caf50',
        padding: '12px',
        margin: '15px 0',
        borderRadius: '4px',
        fontSize: '14px'
      }}
    >
      <strong>Nota:</strong> Ações fracionadas (ex: VALE3F) serão automaticamente convertidas para sua versão normal (VALE3).
    </div>
  );
};

export default FractionedTickerNote;
