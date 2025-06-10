import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import './animation.css'; // Importando o arquivo de animação

/**
 * Compact table component to display holdings/stocks in portfolio sidebar
 * Showing only Ticker, Quantity, Average Price and Current Value
 */
const CompactHoldingsTable = ({ holdings = [] }) => {
  // Estado para controlar a animação
  const [animateIn, setAnimateIn] = useState(false);
  
  // Ativar animação após o componente montar
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimateIn(true);
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Log para debug
  console.log('CompactHoldingsTable recebeu holdings:', holdings);
  
  // Define custom styles for alignment consistency
  const cellStyles = {
    monetary: {
      textAlign: 'right', // Right alignment for monetary values
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    },
    numeric: {
      textAlign: 'center', // Center alignment for numeric values
      whiteSpace: 'nowrap'
    }
  };
  
  // Early return if no holdings
  if (!holdings || holdings.length === 0) {
    console.log('Sem holdings para exibir, retornando null');
    return null;
  }
  
  // Format currency in BRL style with exactly 2 decimal places
  const formatBRL = (value) => {
    // Ensure value is a number and properly formatted
    const numValue = typeof value === 'number' ? value : parseFloat(value || 0);
    return `R$ ${numValue.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };
  
  // Format currency for USD values with exactly 2 decimal places
  const formatUSD = (value) => {
    // Ensure value is a number and properly formatted
    const numValue = typeof value === 'number' ? value : parseFloat(value || 0);
    return `US$ ${numValue.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };  // Função para verificar se um ticker é brasileiro
  const isBrazilianTicker = (ticker) => {
    if (!ticker) return false;
    
    // Remove espaços e converte para maiúsculas
    const normalizedTicker = ticker.trim().toUpperCase();
    
    // Casos conhecidos de ações americanas (ignorar)
    const knownUSTickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'TSLA'];
    if (knownUSTickers.includes(normalizedTicker)) {
      return false;
    }
    
    // Verificar se é BDR (termina com números após um ponto)
    if (normalizedTicker.match(/\.[0-9]+$/)) {
      return false;
    }
    
    // Padrões de tickers brasileiros
    // 1. Padrão comum: 4 letras + 1 número (ex: PETR4, VALE3)
    // 2. Padrão ON/PN: letras + 11 (ordinárias) ou letras + números (ex: TAEE11, SAPR11)
    // 3. Units: letras + números (ex: BPAC11)
    const brazilianPatterns = [
      /^[A-Z]{4}\d{1}$/,       // Padrão comum (PETR4)
      /^[A-Z]{3,4}11$/,        // Ordinárias/Units (TAEE11, SAPR11)
      /^[A-Z]{2,4}\d{2}$/      // Outros padrões (BPAC11, BBDC4)
    ];
    
    // Se corresponder a qualquer um dos padrões, é um ticker brasileiro
    return brazilianPatterns.some(pattern => pattern.test(normalizedTicker));
  };
  
  // Verifica a estrutura dos dados e adapta se necessário
  const processHoldings = (rawHoldings) => {
    // Log para debug
    console.log('Processando holdings:', rawHoldings);
    
    if (!Array.isArray(rawHoldings) || rawHoldings.length === 0) {
      console.log('Dados de holdings inválidos ou vazios');
      return [];
    }
    
    // Verifica o formato dos dados baseado na primeira entrada
    const firstItem = rawHoldings[0];
    
    // Se já estiver no formato esperado
    if (firstItem.ticker && 
        (firstItem.current_value !== undefined || 
         firstItem.valor_atual !== undefined)) {      return rawHoldings.map(item => {
        const ticker = item.ticker || item.symbol || '';
        const isUS = item.is_us_ticker || item.is_us || item.isUS || ticker.startsWith('US:');
        const isBDR = item.is_bdr || item.isBDR || ticker.includes('.SA');
        const isBrazilian = item.is_brazilian || item.isBrazilian || 
                          (!isUS && !isBDR && isBrazilianTicker(ticker));
        
        return {
          ...item,
          is_us_ticker: isUS,
          is_bdr: isBDR,
          is_brazilian: isBrazilian
        };
      });
    }
    
    // Se for outro formato conhecido, tenta adaptar
    if (firstItem.symbol || firstItem.codigo) {
      return rawHoldings.map(item => {
        const ticker = item.symbol || item.codigo || item.ticker || 'N/A';        const isUS = item.is_us_ticker || item.is_us || item.isUS || ticker.startsWith('US:');
        const isBDR = item.is_bdr || item.isBDR || ticker.includes('.SA');
        const isBrazilian = item.is_brazilian || item.isBrazilian || 
                          (!isUS && !isBDR && isBrazilianTicker(ticker));
        
        return {
          ticker: ticker,
          quantity: item.quantity || item.quantidade || item.qtd || 0,
          avg_price: item.avg_price || item.preco_medio || item.precoMedio || 0,
          current_value: item.current_value || item.valor_atual || item.valorAtual || 0,
          is_us_ticker: isUS,
          is_bdr: isBDR,
          is_brazilian: isBrazilian
        };
      });
    }
    
    console.log('Formato desconhecido de holdings:', firstItem);
    return [];
  };
  // Sort assets by current value
  const processedHoldings = processHoldings(holdings);
  
  // Log para verificar se a detecção de ações brasileiras está funcionando
  console.log('Holdings processados com detecção de ações brasileiras:', 
    processedHoldings.map(h => ({
      ticker: h.ticker,
      is_brazilian: h.is_brazilian,
      is_us_ticker: h.is_us_ticker,
      is_bdr: h.is_bdr
    }))
  );
  
  const sortedHoldings = processedHoldings.sort((a, b) => 
    ((b.current_value || b.valor_atual || 0) - (a.current_value || a.valor_atual || 0))
  );  return (
    <Box
      className={animateIn ? 'fade-in-animation' : ''}
      sx={{
        position: 'fixed',
        right: 65, // 15 pixels do fim da página (5px extra para garantir o espaçamento)
        top: '50%', // Centralizar verticalmente
        transform: 'translateY(-50%)', // Ajuste para centralização perfeita
        width: '400px', // Aumentado para acomodar os valores completos
        boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
        borderRadius: '4px',
        backgroundColor: 'rgba(30, 30, 30, 0.6)',
        zIndex: 10,
        maxHeight: '70vh',
        display: 'flex',
        flexDirection: 'column',
        opacity: animateIn ? 1 : 0, // Inicia invisível e torna-se visível com a animação
      }}
    >
      <Typography
        variant="subtitle1"
        sx={{
          color: '#ffc107',
          fontWeight: 700,
          padding: '6px 10px',
          borderBottom: '1px solid rgba(255, 193, 7, 0.3)',
          fontSize: '0.85rem',
          backgroundColor: 'rgba(0, 0, 0, 0.2)'
        }}
      >
        Seus Ativos
      </Typography>
      <TableContainer sx={{ maxHeight: 'none', overflow: 'visible' }}>
        <Table size="small" stickyHeader={false}>
          <TableHead>
            <TableRow sx={{ 
              '& th': { 
                fontSize: '0.7rem',
                padding: '2px 4px',
                backgroundColor: 'rgba(0, 0, 0, 0.3)',
                color: '#ffc107',
                height: '22px'
              }
            }}>
              <TableCell sx={{ width: '25%', fontWeight: 700, fontSize: '0.7rem' }}>Ativo</TableCell>
              <TableCell sx={{ ...cellStyles.numeric, width: '15%', fontWeight: 700, fontSize: '0.7rem' }}>Quantidade</TableCell>
              <TableCell sx={{ ...cellStyles.monetary, width: '25%', fontWeight: 700, fontSize: '0.7rem' }}>Preço Médio</TableCell>
              <TableCell sx={{ ...cellStyles.monetary, width: '35%', fontWeight: 700, fontSize: '0.7rem' }}>Valor Atual</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedHoldings.map((asset) => {
              // Extract data with fallbacks for different property names
              const ticker = asset.ticker || asset.symbol || asset.codigo || 'N/A';
              const quantity = asset.quantity || asset.quantidade || asset.qtd || 0;
              const avgPrice = asset.avg_price || asset.preco_medio || asset.precoMedio || 0;
              const currentValue = asset.current_value || asset.valor_atual || asset.valorAtual || 0;
              const isUS = asset.is_us_ticker || asset.is_us || asset.isUS || false;
              const isBDR = asset.is_bdr || asset.isBDR || false;
              const isBrazilian = asset.is_brazilian || asset.isBrazilian || false;
              return (
                <TableRow 
                  key={ticker} 
                  hover
                  sx={{
                    '& td': { 
                      padding: '3px 6px',
                      borderBottom: '1px solid rgba(81, 81, 81, 0.2)',
                      height: '26px',
                    },
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.05)'
                    }
                  }}
                >
                  <TableCell sx={{ p: '3px 6px' }}>
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center',
                    }}>
                      {isUS && (
                        <Box 
                          component="span" 
                          sx={{ 
                            display: 'inline-block',
                            width: '4px',
                            height: '4px',
                            borderRadius: '50%',
                            backgroundColor: '#29b6f6',
                            mr: 0.5
                          }}
                        />
                      )}
                      {isBDR && (
                        <Box 
                          component="span" 
                          sx={{ 
                            display: 'inline-block',
                            width: '4px',
                            height: '4px',
                            borderRadius: '50%',
                            backgroundColor: '#ab47bc',
                            mr: 0.5
                          }}
                        />
                      )}
                      {isBrazilian && (
                        <Box 
                          component="span" 
                          sx={{ 
                            display: 'inline-block',
                            width: '4px',
                            height: '4px',
                            borderRadius: '50%',
                            backgroundColor: '#4caf50', // Verde para empresas brasileiras
                            mr: 0.5
                          }}
                        />
                      )}
                      <Typography
                        variant="body2" 
                        fontWeight="500" 
                        sx={{ 
                          fontSize: '0.8rem',
                          lineHeight: 1.0,
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          maxWidth: '65px'
                        }}
                      >
                        {ticker}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell sx={{ ...cellStyles.numeric, fontSize: '0.75rem' }}>
                    {Math.round(quantity).toLocaleString('pt-BR')}
                  </TableCell>
                  <TableCell sx={{ ...cellStyles.monetary, fontSize: '0.75rem', pr: '4px' }}>
                    {isUS ? formatUSD(avgPrice) : formatBRL(avgPrice)}
                  </TableCell>
                  <TableCell sx={{ ...cellStyles.monetary, fontSize: '0.75rem', pr: '8px' }}>
                    {formatBRL(currentValue)}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default CompactHoldingsTable;