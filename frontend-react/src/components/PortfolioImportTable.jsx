import React, { useState, useEffect, useRef } from 'react';
import './PortfolioImportTable.css';
import { portfolioAPI } from '../api/portfolioAPI';
import { FractionedTickerNote } from '../components/common';

// Função para normalizar tickers fracionados (ex: VALE3F -> VALE3)
const normalizeTicker = (ticker) => {
  if (!ticker) return '';
  
  // Remove espaços e converte para maiúsculas
  ticker = ticker.trim().toUpperCase();
  
  // Detecta se é um ticker fracionado (termina com F)
  if (ticker.match(/^[A-Z0-9]{4,6}F$/)) {
    // Remove o F final para converter para a versão normal do ticker
    return ticker.slice(0, -1);
  }
  
  return ticker;
};

// Gerar linhas iniciais
const initialRows = (n) => Array.from({ length: n }, (_, idx) => ({ 
  id: idx, 
  ticker: '', 
  preco: '', 
  quantidade: '' 
}));

export default function PortfolioImportTable({ onSave }) {  
  const [rows, setRows] = useState(initialRows(10));
  const [tickersValid, setTickersValid] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [showWarning, setShowWarning] = useState(false);
  const [error, setError] = useState('');
  const [overwriteMode, setOverwriteMode] = useState(false);
  
  
  // Validação do ticker em tempo real utilizando a API
  const validateTicker = async (ticker) => {
    if (!ticker || ticker.trim().length < 3) return false;
    try {
      // Normaliza o ticker antes de validar
      const normalizedTicker = normalizeTicker(ticker);
      const result = await portfolioAPI.validateTicker(normalizedTicker);
      return result.isValid;
    } catch {
      return false;
    }
  };
  
  // Validação de todos os tickers preenchidos
  useEffect(() => {
    // Não queremos fazer validações à toa - apenas para tickers modificados
    const validateAll = async () => {
      const newValid = { ...tickersValid };
      const pendingValidations = rows.filter(
        row => row.ticker && 
        row.ticker.trim() !== '' && 
        (tickersValid[row.id] === undefined || 
         !('_lastValidated' in newValid) || 
         newValid._lastValidated !== row.ticker.trim().toUpperCase())
      );
      
      if (pendingValidations.length === 0) return;
      
      // Para cada ticker que precisa ser validado
      const promises = pendingValidations.map(async (row) => {
        const upperTicker = row.ticker.trim().toUpperCase();
        // Marcar com "validando" temporariamente
        newValid[row.id] = 'validating';
        setTickersValid({...newValid});
        
        // Fazer a validação real
        const isValid = await validateTicker(upperTicker);
        newValid[row.id] = isValid;
        newValid._lastValidated = upperTicker;
      });
      
      await Promise.all(promises);
      setTickersValid({...newValid});
    };
    
    // Debounce para não sobrecarregar a API
    const timeoutId = setTimeout(() => {
      validateAll();
    }, 400);
    
    return () => clearTimeout(timeoutId);
    // eslint-disable-next-line
  }, [rows]);

  // Adiciona linhas extras conforme preenchimento
  useEffect(() => {
    const filled = rows.filter(r => r.ticker || r.preco || r.quantidade).length;
    if (rows.length < filled + 5) {
      setRows(prevRows => [
        ...prevRows,
        ...initialRows(5).map((row, i) => ({ ...row, id: prevRows.length + i }))
      ]);
    }
  }, [rows]);  // Validação de preço e quantidade
  const validateRow = (row) => {
    // Validar ticker - deve existir e ser válido
    if (!row.ticker || tickersValid[row.id] === false) return false;
    
    // Validar preço - deve ser um número positivo
    let preco = String(row.preco || '').replace(',', '.');
    if (!preco || isNaN(Number(preco)) || Number(preco) <= 0) return false;
    
    // Validar quantidade
    let quantidade = row.quantidade;
    if (!quantidade || isNaN(Number(quantidade)) || !Number.isInteger(Number(quantidade))) return false;
    
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
      const nextRowElement = document.querySelector(`#row-${nextRow}-col-${nextCol}`);
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
            // Ir para a última coluna da linha anterior
            nextRow = rowIndex - 1;
            nextCol = columns.length - 1;
          }
          break;
        case 'ArrowRight':
          if (colIndex < columns.length - 1) {
            nextCol = colIndex + 1;
          } else if (rowIndex < rows.length - 1) {
            // Ir para a primeira coluna da próxima linha
            nextRow = rowIndex + 1;
            nextCol = 0;
          }
          break;
      }
      
      // Encontrar o próximo elemento para focar
      const nextRowElement = document.querySelector(`#row-${nextRow}-col-${nextCol}`);
      if (nextRowElement) {
        nextRowElement.focus();
        
        // Posiciona o cursor adequadamente baseado na direção
        if (e.key === 'ArrowLeft') {
          // Cursor no final quando vem da esquerda
          const length = nextRowElement.value.length;
          nextRowElement.setSelectionRange(length, length);
        } else if (e.key === 'ArrowRight') {
          // Cursor no início quando vem da direita
          nextRowElement.setSelectionRange(0, 0);
        } else {
          // Para navegação vertical, seleciona todo o texto
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
      
      // Preencher com os dados colados
      rows.forEach((rowStr, rowOffset) => {
        const rowIdx = startRowIdx + rowOffset;
        const rowData = rowStr.split(/\t|,/).map(cell => cell.trim());
        
        // Preencher células na linha
        rowData.forEach((cellValue, colOffset) => {
          const colIdx = startColIdx + colOffset;
          if (colIdx < columns.length && rowIdx < newRows.length) {
            const field = columns[colIdx];
            
            // Se for o campo ticker, normaliza os tickers fracionados
            if (field === 'ticker' && cellValue) {
              cellValue = normalizeTicker(cellValue);
            }
            
            newRows[rowIdx] = {
              ...newRows[rowIdx],
              [field]: cellValue
            };
          }
        });
      });
      
      return newRows;
    });
  };  // Salvar
  const handleSave = async () => {
    setError('');
    if (!rows.some(validateRow)) {
      setError('Preencha pelo menos um ativo válido.');
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
      // Filtrar apenas as linhas válidas e limpar possíveis dados problemáticos
      const ativos = rows.filter(validateRow).map(row => {
        // Garantir que ticker não tenha espaços ou caracteres especiais
        // Converter versões fracionadas (ex: VALE3F) para versão normal (VALE3)
        const ticker = normalizeTicker(row.ticker);
        
        // Converter preço para número garantindo formato correto
        const precoStr = String(row.preco || '').replace(',', '.').trim();
        const preco = Number(precoStr);
        
        // Converter quantidade para número inteiro
        const quantidade = parseInt(row.quantidade, 10);
        
        return { ticker, preco, quantidade };
      });
      
      // Log para depuração
      console.log(`Enviando ${ativos.length} ativos no modo ${overwriteMode ? 'Sobrescrever' : 'Aporte/Retirada'}`);
      console.log('Dados enviados:', ativos);
      console.log('API utilizada:', overwriteMode ? 'overwritePortfolio' : 'batchUpdatePortfolio');
      
      // Chama a API diferente dependendo do modo
      let response;
      try {
        if (overwriteMode) {
          response = await portfolioAPI.overwritePortfolio({ ativos });
        } else {
          // No modo Aporte/Retirada, processar um por um para maior segurança
          const promises = ativos.map(async (ativo) => {
            const tipo = ativo.quantidade > 0 ? 'compra' : 'venda';
            const quantidade_abs = Math.abs(ativo.quantidade);
            
            return portfolioAPI.updateEmpresa({
              codigo: ativo.ticker, // ticker já está normalizado no mapeamento acima
              preco: ativo.preco,
              quantidade: quantidade_abs,
              tipo_operacao: tipo
            });
          });
            await Promise.all(promises);
          response = { message: `${ativos.length} operações processadas com sucesso` };
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
        // Mensagem específica para o erro de tipo
        setError(`Erro de comunicação com a API. Por favor, tente novamente ou atualize a página.`);
        console.error('Detalhes do erro de tipo:', e);
      } else {
        setError(`Erro ao salvar: ${e.toString()}`);
      }
      
      setIsSaving(false);
    }
  };
  return (
    <div className="portfolio-import-table-dark">
      <div className="header-with-toggle">
        <h2>{overwriteMode ? 'Importar Ativos (Sobrescreve Carteira)' : 'Alterar Posições (Compra/Venda)'}</h2>
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
          <strong>Modo Sobrescrever:</strong> Esta ação irá substituir completamente sua carteira atual. 
          Todos os dados anteriores, incluindo históricos de compras/vendas, serão perdidos.
          Neste modo, todas as quantidades devem ser positivas.
        </p>
      ) : (
        <p className="info">
          <strong>Modo Aporte/Retirada:</strong> Neste modo você pode adicionar ou remover posições individuais.
          Valores positivos serão registrados como compras e valores negativos como vendas.
          Seus dados históricos serão mantidos, apenas as posições serão atualizadas.
        </p>      )}
      
      <div className="excel-table-container">
        <table className="excel-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Preço Médio</th>
              <th>Quantidade</th>
            </tr>
          </thead>
          <tbody>            {rows.map((row, rowIndex) => (
              <tr key={row.id}>                <td className={`excel-cell ${
                    row.ticker ? (
                      tickersValid[row.id] === true ? 'cell-valid' : 
                      tickersValid[row.id] === false ? 'cell-invalid' :
                      tickersValid[row.id] === 'validating' ? 'cell-validating' : ''
                    ) : ''
                  }`}>                  <input 
                    id={`row-${rowIndex}-col-0`}
                    type="text"
                    value={row.ticker || ''}
                    onChange={(e) => {
                      // Converter para maiúsculo e normalizar ticker fracionado
                      const inputValue = e.target.value.toUpperCase();
                      const normalizedTicker = normalizeTicker(inputValue);
                      
                      // Se for detectado um ticker fracionado, substitui automaticamente
                      // pela versão normal e mostra um indicador visual
                      if (inputValue !== normalizedTicker && inputValue.endsWith('F')) {
                        // Fornece feedback visual temporário que o ticker foi normalizado
                        const element = document.getElementById(`row-${rowIndex}-col-0`);
                        if (element) {
                          element.classList.add('ticker-normalized');
                          setTimeout(() => {
                            element.classList.remove('ticker-normalized');
                          }, 1000);
                        }
                      }
                      
                      handleCellChange(row.id, 'ticker', normalizedTicker);
                    }}
                    onKeyDown={(e) => handleKeyDown(e, row.id, 'ticker', rowIndex, 0)}
                    onFocus={handleFocus}
                    onPaste={(e) => handlePaste(e, rowIndex, 0)}
                    placeholder="PETR4"
                    className="excel-input"
                    spellCheck="false"
                    autoComplete="off"
                    autoCapitalize="characters"
                  />
                  {row.ticker && tickersValid[row.id] === 'validating' && (
                    <div className="validating-indicator"></div>
                  )}
                  {row.ticker && tickersValid[row.id] === false && (
                    <div className="error-tooltip">Ticker inválido</div>
                  )}
                </td>
                <td className="excel-cell">                  <input
                    id={`row-${rowIndex}-col-1`}
                    type="text"
                    value={row.preco || ''}
                    onChange={(e) => handleCellChange(row.id, 'preco', e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, row.id, 'preco', rowIndex, 1)}
                    onFocus={handleFocus}
                    placeholder="29,90"
                    className="excel-input"
                    spellCheck="false"
                    autoComplete="off"
                    inputMode="decimal"
                  />
                </td>
                <td className="excel-cell">                  <input
                    id={`row-${rowIndex}-col-2`}
                    type="text"
                    value={row.quantidade || ''}
                    onChange={(e) => handleCellChange(row.id, 'quantidade', e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, row.id, 'quantidade', rowIndex, 2)}
                    onFocus={handleFocus}
                    placeholder="100"
                    className="excel-input"
                    spellCheck="false"
                    autoComplete="off"
                    inputMode="numeric"
                  />
                </td>
              </tr>
            ))}
          </tbody>        </table>      </div>
        {error && <div className="error-msg">{error}</div>}
      
      <FractionedTickerNote />
      
      <button className="save-btn" onClick={handleSave} disabled={isSaving}>
        {isSaving ? 'Salvando...' : overwriteMode ? 'Sobrescrever Carteira' : 'Aplicar Alterações'}
      </button>
        {showWarning && (
        <div className="modal">
          <div className="modal-content">
            <h3>{overwriteMode ? '⚠️ ATENÇÃO: SOBRESCREVER CARTEIRA' : 'Confirmar Alterações'}</h3>
            {overwriteMode ? (
              <div>
                <p className="warning modal-warning">
                  <strong>Você está prestes a sobrescrever toda a sua carteira!</strong>
                </p>
                <p>Esta ação não pode ser desfeita e substituirá completamente seus dados atuais.</p>
                <p>Todos os históricos de transações anteriores serão perdidos.</p>
              </div>
            ) : (
              <div>
                <p>Confirma a aplicação das alterações abaixo na sua carteira?</p>
                <p className="info modal-info">
                  Quantidades positivas serão registradas como compras.<br />
                  Quantidades negativas serão registradas como vendas.
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
