import React from 'react';
import './FractionalTickerInfo.css';

/**
 * Componente para exibir informações sobre a conversão de tickers fracionados
 * 
 * @returns {JSX.Element} Componente React
 */
const FractionalTickerInfo = ({ className = '' }) => {
  return (
    <div className={`fractional-ticker-info ${className}`}>
      Ações fracionadas (ex: VALE3F) serão automaticamente convertidas para sua versão normal (VALE3).
    </div>
  );
};

export default FractionalTickerInfo;
