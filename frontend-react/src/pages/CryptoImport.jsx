import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CryptoImportTable from '../components/CryptoImportTable';
import './FileUpload.css';

export default function CryptoImport() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const handleCryptoSave = () => {
    setIsLoading(true);
    
    // Simular delay para feedback visual
    setTimeout(() => {
      setIsLoading(false);
      // Redirecionar para o dashboard após salvar
      navigate('/dashboard');
    }, 1000);
  };

  return (
    <div className="file-upload-container">
      <div className="upload-header">
        <h1>💰 Importar Carteira de Criptomoedas</h1>
        <p className="upload-subtitle">
          Adicione suas criptomoedas de forma simples e inteligente
        </p>
      </div>

      {isLoading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Processando criptomoedas...</p>
        </div>
      ) : (
        <div className="upload-content">
          <div className="info-card crypto-info">
            <h3>🪙 Como funciona a importação de criptomoedas</h3>
            <ul>
              <li><strong>Reconhecimento automático:</strong> Digite BTC, Bitcoin, ETH, Ethereum - o sistema reconhece automaticamente as principais moedas</li>
              <li><strong>Preços em USD:</strong> Informe preços em dólares ou deixe vazio para estimativa automática baseada no mercado</li>
              <li><strong>Validação inteligente:</strong> Criptomoedas desconhecidas são validadas automaticamente via CoinGecko</li>
              <li><strong>Flexibilidade total:</strong> Funciona tanto para compras quanto vendas (quantidades negativas)</li>
            </ul>
            
            <div className="crypto-examples">
              <h4>💡 Exemplos práticos:</h4>
              <div className="example-row">
                <span className="example-input">BTC</span> + <span className="example-price">57000</span> + <span className="example-qty">0.063628</span>
                <span className="example-desc">→ Compra de Bitcoin com preço conhecido</span>
              </div>
              <div className="example-row">
                <span className="example-input">Bitcoin</span> + <span className="example-price">(vazio)</span> + <span className="example-qty">0.5</span>
                <span className="example-desc">→ Sistema estima o preço médio automaticamente</span>
              </div>
            </div>
          </div>

          <div className="upload-section">
            <CryptoImportTable onSave={handleCryptoSave} />
          </div>
        </div>
      )}
    </div>
  );
}
