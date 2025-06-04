import React, { useState, useEffect, useRef } from 'react';
import './PortfolioImportTable.css';
import { portfolioAPI } from '../api/portfolioAPI';

// Gerar linhas iniciais
const initialRows = (n) => Array.from({ length: n }, (_, idx) => ({ 
  id: idx, 
  ticker: '', 
  preco: '', 
  quantidade: '' 
}));

export default function PortfolioImportTable({ onSave }) {  const [rows, setRows] = useState(initialRows(10));
  const [tickersValid, setTickersValid] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [showWarning, setShowWarning] = useState(false);
  const [error, setError] = useState('');
  
  // Validação do ticker em tempo real utilizando a API
  const validateTicker = async (ticker) => {
    if (!ticker || ticker.trim().length < 3) return false;
    try {
      const result = await portfolioAPI.validateTicker(ticker.trim().toUpperCase());
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
  }, [rows]);

  // Validação de preço e quantidade
  const validateRow = (row) => {
    if (!row.ticker || tickersValid[row.id] === false) return false;
    
    let preco = String(row.preco || '').replace(',', '.');
    if (!preco || isNaN(Number(preco)) || Number(preco) <= 0) return false;
    
    let quantidade = row.quantidade;
    if (!quantidade || isNaN(Number(quantidade)) || !Number.isInteger(Number(quantidade)) || Number(quantidade) <= 0) return false;
    
    return true;  };
  
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
            newRows[rowIdx] = {
              ...newRows[rowIdx],
              [field]: cellValue
            };
          }
        });
      });
      
      return newRows;
    });
  };

  // Salvar
  const handleSave = async () => {
    setError('');
    if (!rows.some(validateRow)) {
      setError('Preencha pelo menos um ativo válido.');
      return;
    }
    setShowWarning(true);
  };

  // Confirma sobrescrita
  const confirmSave = async () => {
    setIsSaving(true);
    try {
      const ativos = rows.filter(validateRow).map(row => ({
        ticker: row.ticker.trim().toUpperCase(),
        preco: Number(String(row.preco || '').replace(',', '.')),
        quantidade: Number(row.quantidade)
      }));
      await portfolioAPI.overwritePortfolio({ ativos });
      setIsSaving(false);
      setShowWarning(false);
      if (onSave) onSave();
    } catch (e) {
      setError('Erro ao salvar.');
      setIsSaving(false);
    }
  };

  return (
    <div className="portfolio-import-table-dark">
      <h2>Importar Ativos (Sobrescreve Carteira)</h2>
      <p className="warning">Esta ação irá sobrescrever completamente sua carteira atual. Todos os dados anteriores, incluindo históricos de compras/vendas, serão perdidos.</p>
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
                    onChange={(e) => handleCellChange(row.id, 'ticker', e.target.value.toUpperCase())}
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
          </tbody>
        </table>
      </div>
      
      {error && <div className="error-msg">{error}</div>}
      <button className="save-btn" onClick={handleSave} disabled={isSaving}>
        {isSaving ? 'Salvando...' : 'Salvar'}
      </button>
      
      {showWarning && (
        <div className="modal">
          <div className="modal-content">
            <h3>Atenção!</h3>
            <p>Tem certeza que deseja sobrescrever sua carteira? Esta ação não pode ser desfeita.</p>
            <div className="modal-buttons">
              <button className="confirm-btn" onClick={confirmSave} disabled={isSaving}>
                {isSaving ? 'Processando...' : 'Confirmar'}
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
