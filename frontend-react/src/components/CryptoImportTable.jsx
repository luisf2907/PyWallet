import React, { useState, useEffect, useRef } from 'react';
import './PortfolioImportTable.css';
import { portfolioAPI } from '../api/portfolioAPI';

// Lista das 10 maiores criptomoedas para reconhecimento automático
const TOP_10_CRYPTOS = {
  // Sigla -> Nome completo
  'BTC': 'Bitcoin',
  'ETH': 'Ethereum', 
  'USDT': 'Tether',
  'BNB': 'Binance Coin',
  'XRP': 'XRP',
  'SOL': 'Solana',
  'USDC': 'USD Coin',
  'ADA': 'Cardano',
  'DOGE': 'Dogecoin',
  'AVAX': 'Avalanche'
};

// Criar mapa reverso: Nome completo -> Sigla
const CRYPTO_NAME_TO_SYMBOL = {};
Object.entries(TOP_10_CRYPTOS).forEach(([symbol, name]) => {
  CRYPTO_NAME_TO_SYMBOL[name.toUpperCase()] = symbol;
});

// Função para normalizar input de criptomoedas
const normalizeCrypto = (input) => {
  if (!input) return '';
  
  // Remove espaços e converte para maiúsculas
  input = input.trim().toUpperCase();
  
  // Se é uma das siglas conhecidas, retorna a sigla
  if (TOP_10_CRYPTOS[input]) {
    return input;
  }
  
  // Se é um nome completo conhecido, converte para sigla
  if (CRYPTO_NAME_TO_SYMBOL[input]) {
    return CRYPTO_NAME_TO_SYMBOL[input];
  }
  
  // Se não é reconhecida automaticamente, retorna como está para validação via API
  return input;
};

// Gerar linhas iniciais vazias (sem exemplos fixos)
const initialRows = (n) => {
  return Array.from({ length: n }, (_, idx) => ({ 
    id: idx, 
    ticker: '', 
    preco: '', 
    quantidade: '' 
  }));
};

export default function CryptoImportTable({ onSave }) {  
  const [rows, setRows] = useState(initialRows(10));
  const [cryptosValid, setCryptosValid] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [showWarning, setShowWarning] = useState(false);
  const [error, setError] = useState('');
  const [overwriteMode, setOverwriteMode] = useState(false);
  
  // Validação da criptomoeda em tempo real utilizando a API
  const validateCrypto = async (crypto) => {
    if (!crypto || crypto.trim().length < 2) return false;
    
    try {
      // Primeiro, tenta normalizar (reconhecimento automático das top 10)
      const normalizedCrypto = normalizeCrypto(crypto);
      
      // Se foi reconhecida automaticamente, é válida
      if (TOP_10_CRYPTOS[normalizedCrypto]) {
        return true;
      }
      
      // Se não foi reconhecida, valida via API CoinGecko
      const result = await portfolioAPI.validateCrypto(normalizedCrypto);
      return result.isValid;
    } catch {
      return false;
    }
  };
  
  // Controle de quais criptos já foram validadas
  const [validatedCryptos, setValidatedCryptos] = useState({
    // Cache das top 10 para evitar validações desnecessárias
    'BTC': true,
    'BITCOIN': true,
    'ETH': true,
    'ETHEREUM': true,
    'USDT': true,
    'TETHER': true,
    'BNB': true,
    'BINANCE COIN': true,
    'XRP': true,
    'SOL': true,
    'SOLANA': true,
    'USDC': true,
    'USD COIN': true,
    'ADA': true,
    'CARDANO': true,
    'DOGE': true,
    'DOGECOIN': true,
    'AVAX': true,
    'AVALANCHE': true
  });
  const [lastModifiedId, setLastModifiedId] = useState(null);

  // Validação das criptomoedas - apenas o que foi modificado
  useEffect(() => {
    if (lastModifiedId === null) return;
    
    const validateModifiedCrypto = async () => {
      const row = rows.find(r => r.id === lastModifiedId);
      if (!row || !row.ticker || row.ticker.trim() === '') return;
      
      const crypto = row.ticker.trim().toUpperCase();
      
      // Verifica se esta cripto já foi validada antes
      if (validatedCryptos[crypto] !== undefined) {
        setCryptosValid(prev => ({
          ...prev,
          [lastModifiedId]: validatedCryptos[crypto]
        }));
        return;
      }
      
      // Marcar como "validando" temporariamente
      setCryptosValid(prev => ({
        ...prev, 
        [lastModifiedId]: 'validating'
      }));
      
      // Fazer a validação
      const isValid = await validateCrypto(crypto);
      
      // Atualizar os estados
      setValidatedCryptos(prev => ({
        ...prev,
        [crypto]: isValid
      }));
      
      setCryptosValid(prev => ({
        ...prev,
        [lastModifiedId]: isValid
      }));
    };
    
    // Debounce para não sobrecarregar a API
    const timeoutId = setTimeout(() => {
      validateModifiedCrypto();
    }, 400);
    
    return () => clearTimeout(timeoutId);
  }, [lastModifiedId, rows, validatedCryptos]);

  // Adiciona linhas extras conforme preenchimento
  useEffect(() => {
    const filled = rows.filter(r => r.ticker || r.preco || r.quantidade).length;
    if (rows.length < filled + 5) {
      setRows(prevRows => [
        ...prevRows,
        ...Array.from({ length: 5 }, (_, i) => ({ 
          id: prevRows.length + i,
          ticker: '', 
          preco: '', 
          quantidade: '' 
        }))
      ]);
    }
  }, [rows]);

  // Validação de preço e quantidade
  const validateRow = (row) => {
    // Validar cripto - deve existir e ser válida
    if (!row.ticker || cryptosValid[row.id] === false) return false;
    
    // Validar quantidade - deve ser um número positivo
    let quantidade = row.quantidade;
    if (!quantidade || isNaN(Number(quantidade)) || Number(quantidade) <= 0) return false;
    
    // Preço é opcional - se vazio, será estimado automaticamente
    if (row.preco && row.preco.trim() !== '') {
      let preco = String(row.preco).replace(',', '.');
      if (isNaN(Number(preco)) || Number(preco) <= 0) return false;
    }
    
    // Regras específicas de cada modo:
    if (overwriteMode) {
      // No modo Sobrescrever: quantidade deve ser positiva
      if (Number(quantidade) <= 0) return false;
    } else {
      // No modo Aporte/Retirada: quantidade não pode ser zero, mas pode ser negativa (venda)
      if (Number(quantidade) === 0) return false;
    }
    
    return true;
  };
  
  // Atualizar valor de célula
  const handleCellChange = (id, field, value) => {
    setRows(prevRows => 
      prevRows.map(row => 
        row.id === id ? { ...row, [field]: value } : row
      )
    );
    
    // Se o campo modificado for o ticker, marca para validação
    if (field === 'ticker') {
      setLastModifiedId(id);
    }
  };
  
  // Handler para seleção de texto quando um input recebe foco
  const handleFocus = (e) => {
    // Seleciona todo o texto quando o input recebe foco
    if (e.target.value) {
      e.target.select();
    }
  };

  // Navegar células com Tab, Enter e setas do teclado (como no Excel)
  const handleKeyDown = (e, rowId, field, rowIndex, colIndex) => {
    const columns = ['ticker', 'preco', 'quantidade'];
    
    // Tab e Enter para navegação
    if (e.key === 'Tab' || e.key === 'Enter') {
      e.preventDefault();
      
      // Próxima coluna ou próxima linha
      let nextCol = colIndex;
      let nextRow = rowIndex;
      
      if (e.key === 'Enter' || colIndex === columns.length - 1) {
        nextRow = rowIndex + 1;
        nextCol = 0;
      } else {
        nextCol = colIndex + 1;
      }
      
      // Encontrar o próximo elemento para focar
      const nextRowElement = document.querySelector(`#crypto-row-${nextRow}-col-${nextCol}`);
      if (nextRowElement) {
        nextRowElement.focus();
      }
    }
    // Navegação com teclas de seta
    else if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
      // Comportamento especial para setas esquerda/direita 
      // quando o cursor está no início ou fim do texto
      const input = e.target;
      const cursorPos = input.selectionStart;
      const textLength = input.value.length;
      
      // Permitir navegação natural dentro do texto
      if (e.key === 'ArrowLeft' && cursorPos > 0) return;
      if (e.key === 'ArrowRight' && cursorPos < textLength) return;
      
      e.preventDefault();
      
      let nextCol = colIndex;
      let nextRow = rowIndex;
      
      // Calcular a próxima célula baseado na tecla pressionada
      switch(e.key) {
        case 'ArrowUp':
          nextRow = Math.max(0, rowIndex - 1);
          break;
        case 'ArrowDown':
          nextRow = Math.min(rows.length - 1, rowIndex + 1);
          break;
        case 'ArrowLeft':
          if (colIndex > 0) {
            nextCol = colIndex - 1;
          } else if (rowIndex > 0) {
            nextRow = rowIndex - 1;
            nextCol = columns.length - 1;
          }
          break;
        case 'ArrowRight':
          if (colIndex < columns.length - 1) {
            nextCol = colIndex + 1;
          } else if (rowIndex < rows.length - 1) {
            nextRow = rowIndex + 1;
            nextCol = 0;
          }
          break;
      }
      
      // Encontrar o próximo elemento para focar
      const nextRowElement = document.querySelector(`#crypto-row-${nextRow}-col-${nextCol}`);
      if (nextRowElement) {
        nextRowElement.focus();
        
        // Posiciona o cursor adequadamente baseado na direção
        if (e.key === 'ArrowLeft') {
          const length = nextRowElement.value.length;
          nextRowElement.setSelectionRange(length, length);
        } else if (e.key === 'ArrowRight') {
          nextRowElement.setSelectionRange(0, 0);
        } else {
          nextRowElement.select();
        }
      }
    }
  };
  
  // Handler para colar dados do Excel
  const handlePaste = (e, startRowIdx, startColIdx) => {
    e.preventDefault();
    
    // Obter dados da área de transferência
    const clipboardData = e.clipboardData;
    const pastedData = clipboardData.getData('text');
    const rows = pastedData.split(/\r\n|\n|\r/).filter(row => row.trim() !== '');
    
    if (!rows.length) return;
    
    // Colunas disponíveis para preencher
    const columns = ['ticker', 'preco', 'quantidade'];
    
    // Copiar o estado atual das linhas
    setRows(prevRows => {
      const newRows = [...prevRows];
      let lastCryptoRowId = null;
      
      // Preencher com os dados colados
      rows.forEach((rowStr, rowOffset) => {
        const rowIdx = startRowIdx + rowOffset;
        const rowData = rowStr.split(/\t|,/).map(cell => cell.trim());
        
        // Preencher células na linha
        rowData.forEach((cellValue, colOffset) => {
          const colIdx = startColIdx + colOffset;
          if (colIdx < columns.length && rowIdx < newRows.length) {
            const field = columns[colIdx];
            
            // Se for o campo ticker, normaliza as criptomoedas
            if (field === 'ticker' && cellValue) {
              cellValue = normalizeCrypto(cellValue);
              lastCryptoRowId = newRows[rowIdx].id;
            }
            
            newRows[rowIdx] = {
              ...newRows[rowIdx],
              [field]: cellValue
            };
          }
        });
      });
      
      // Marca a última cripto modificada para validação
      if (lastCryptoRowId !== null) {
        setTimeout(() => {
          setLastModifiedId(lastCryptoRowId);
        }, 0);
      }
      
      return newRows;
    });
  };

  // Salvar
  const handleSave = async () => {
    setError('');
    if (!rows.some(validateRow)) {
      setError('Preencha pelo menos uma criptomoeda válida.');
      return;
    }
    
    // Verificar a conexão com o backend antes de continuar
    try {
      await portfolioAPI.testConnection();
      console.log('Conexão com o backend está funcionando');
    } catch (e) {
      console.error('Erro ao verificar conexão com backend:', e);
      setError('Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.');
      return;
    }
    
    setShowWarning(true);
  };
  
  // Confirma a operação (sobrescrita ou aporte/retirada)
  const confirmSave = async () => {
    setIsSaving(true);
    setError('');
    try {
      // Filtrar apenas as linhas válidas e normalizar dados
      const criptos = rows.filter(validateRow).map(row => {
        // Normalizar criptomoeda
        const crypto = normalizeCrypto(row.ticker);
        
        // Converter preço para número (pode ser null se vazio - será estimado)
        let preco = null;
        if (row.preco && row.preco.trim() !== '') {
          const precoStr = String(row.preco).replace(',', '.').trim();
          preco = Number(precoStr);
        }
        
        // Converter quantidade para número
        const quantidade = Number(row.quantidade);
        
        return { crypto, preco, quantidade };
      });
      
      // Log para depuração
      console.log(`Enviando ${criptos.length} criptomoedas no modo ${overwriteMode ? 'Sobrescrever' : 'Aporte/Retirada'}`);
      console.log('Dados enviados:', criptos);
      
      // Chama a API diferente dependendo do modo
      let response;
      try {
        if (overwriteMode) {
          response = await portfolioAPI.overwriteCryptoPortfolio({ criptos });
        } else {
          response = await portfolioAPI.batchUpdateCryptoPortfolio({ criptos });
        }
        
        console.log('Resposta da API:', response);
        setIsSaving(false);
        setShowWarning(false);
        if (onSave) onSave();
      } catch (e) {
        throw e;
      }
    } catch (e) {
      console.error('Erro ao salvar:', e);
      
      // Fornecer mensagem de erro mais amigável para o usuário
      if (e.toString().includes('404')) {
        setError(`Erro de comunicação com o servidor (404). O endpoint necessário não foi encontrado.`);
      } else if (e.toString().includes('401')) {
        setError(`Erro de autenticação (401). Por favor, faça login novamente.`);
      } else if (e.toString().includes('TypeError')) {
        setError(`Erro de comunicação com a API. Por favor, tente novamente ou atualize a página.`);
        console.error('Detalhes do erro de tipo:', e);
      } else {
        setError(`Erro ao salvar: ${e.toString()}`);
      }
      
      setIsSaving(false);
    }
  };

  // Componente de nota explicativa para criptomoedas
  const CryptoNote = () => (
    <div 
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
      <strong>Nota:</strong> Criptomoedas podem ser inseridas por nome completo (ex: Bitcoin) ou sigla (ex: BTC). 
      Sistema reconhece automaticamente as principais moedas.
    </div>
  );

  return (
    <div className="portfolio-import-table-dark">
      <div className="header-with-toggle">
        <h2>{overwriteMode ? 'Importar Criptomoedas (Sobrescreve Carteira)' : 'Alterar Posições de Criptomoedas (Compra/Venda)'}</h2>
        <div className="toggle-container">
          <span className={!overwriteMode ? 'active-mode' : ''}>Aporte/Retirada</span>
          <label className="toggle-switch">
            <input 
              type="checkbox" 
              checked={overwriteMode} 
              onChange={() => setOverwriteMode(!overwriteMode)}
            />
            <span className="toggle-slider"></span>
          </label>
          <span className={overwriteMode ? 'active-mode' : ''}>Sobrescrever</span>
        </div>
      </div>

      {overwriteMode ? (
        <p className="warning">
          <strong>Modo Sobrescrever:</strong> Esta ação irá substituir completamente sua carteira de criptomoedas atual. 
          Todos os dados anteriores, incluindo históricos de compras/vendas, serão perdidos.
          Neste modo, todas as quantidades devem ser positivas. Se não souber o preço médio, deixe em branco.
        </p>
      ) : (
        <p className="info">
          <strong>Modo Aporte/Retirada:</strong> Neste modo você pode adicionar ou remover posições de criptomoedas.
          Valores positivos serão registrados como compras e valores negativos como vendas.
          Preços devem ser informados em USD. Se não souber o preço médio, deixe em branco.
          Seus dados históricos serão mantidos, apenas as posições serão atualizadas.
        </p>
      )}
      
      <div className="excel-table-container">
        <table className="excel-table">
          <thead>
            <tr>
              <th>Criptomoeda</th>
              <th>Preço Médio (USD)</th>
              <th>Quantidade</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={row.id}>
                <td className={`excel-cell ${
                    row.ticker ? (
                      cryptosValid[row.id] === true ? 'cell-valid' : 
                      cryptosValid[row.id] === false ? 'cell-invalid' :
                      cryptosValid[row.id] === 'validating' ? 'cell-validating' : ''
                    ) : ''
                  }`}>
                  <input 
                    id={`crypto-row-${rowIndex}-col-0`}
                    type="text"
                    value={row.ticker || ''}
                    onChange={(e) => {
                      // Normalizar criptomoeda durante a digitação
                      const inputValue = e.target.value;
                      const normalizedCrypto = normalizeCrypto(inputValue);
                      
                      // Se foi detectada normalização automática, mostra feedback visual
                      if (inputValue.toUpperCase() !== normalizedCrypto && TOP_10_CRYPTOS[normalizedCrypto]) {
                        const element = document.getElementById(`crypto-row-${rowIndex}-col-0`);
                        if (element) {
                          element.classList.add('ticker-normalized');
                          setTimeout(() => {
                            element.classList.remove('ticker-normalized');
                          }, 1000);
                        }
                      }
                      
                      handleCellChange(row.id, 'ticker', normalizedCrypto);
                    }}
                    onKeyDown={(e) => handleKeyDown(e, row.id, 'ticker', rowIndex, 0)}
                    onFocus={handleFocus}
                    onPaste={(e) => handlePaste(e, rowIndex, 0)}
                    placeholder="BTC"
                    className="excel-input"
                    spellCheck="false"
                    autoComplete="off"
                    autoCapitalize="characters"
                  />
                  {row.ticker && cryptosValid[row.id] === 'validating' && (
                    <div className="validating-indicator"></div>
                  )}
                  {row.ticker && cryptosValid[row.id] === false && (
                    <div className="error-tooltip">Criptomoeda inválida</div>
                  )}
                </td>
                <td className="excel-cell">
                  <input
                    id={`crypto-row-${rowIndex}-col-1`}
                    type="text"
                    value={row.preco || ''}
                    onChange={(e) => handleCellChange(row.id, 'preco', e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, row.id, 'preco', rowIndex, 1)}
                    onFocus={handleFocus}
                    placeholder="57000"
                    className="excel-input"
                    spellCheck="false"
                    autoComplete="off"
                    inputMode="decimal"
                  />
                </td>
                <td className="excel-cell">
                  <input
                    id={`crypto-row-${rowIndex}-col-2`}
                    type="text"
                    value={row.quantidade || ''}
                    onChange={(e) => handleCellChange(row.id, 'quantidade', e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, row.id, 'quantidade', rowIndex, 2)}
                    onFocus={handleFocus}
                    placeholder="0.063628"
                    className="excel-input"
                    spellCheck="false"
                    autoComplete="off"
                    inputMode="decimal"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {error && <div className="error-msg">{error}</div>}
      
      <CryptoNote />
      
      <button className="save-btn" onClick={handleSave} disabled={isSaving}>
        {isSaving ? 'Salvando...' : overwriteMode ? 'Sobrescrever Carteira' : 'Aplicar Alterações'}
      </button>

      {showWarning && (
        <div className="modal">
          <div className="modal-content">
            <h3>{overwriteMode ? '⚠️ ATENÇÃO: SOBRESCREVER CARTEIRA DE CRIPTOMOEDAS' : 'Confirmar Alterações'}</h3>
            {overwriteMode ? (
              <div>
                <p className="warning modal-warning">
                  <strong>Você está prestes a sobrescrever toda a sua carteira de criptomoedas!</strong>
                </p>
                <p>Esta ação não pode ser desfeita e substituirá completamente seus dados atuais.</p>
                <p>Todos os históricos de transações anteriores serão perdidos.</p>
              </div>
            ) : (
              <div>
                <p>Confirma a aplicação das alterações abaixo na sua carteira de criptomoedas?</p>
                <p className="info modal-info">
                  Quantidades positivas serão registradas como compras.<br />
                  Quantidades negativas serão registradas como vendas.<br />
                  Preços vazios serão estimados automaticamente.
                </p>
              </div>
            )}
            <div className="modal-buttons">
              <button 
                className={overwriteMode ? "confirm-btn warning-btn" : "confirm-btn"} 
                onClick={confirmSave} 
                disabled={isSaving}
              >
                {isSaving ? 'Processando...' : overwriteMode ? 'Sim, Sobrescrever Carteira' : 'Confirmar Alterações'}
              </button>
              <button className="cancel-btn" onClick={() => setShowWarning(false)} disabled={isSaving}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
