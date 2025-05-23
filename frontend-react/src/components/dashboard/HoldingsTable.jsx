import React from 'react';
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
  TableFooter,
  Chip,
} from '@mui/material';

/**
 * Table component to display holdings/stocks in portfolio
 */
const HoldingsTable = ({ holdings = [] }) => {
  // Define custom styles for alignment consistency
  const cellStyles = {
    monetary: {
      textAlign: 'left' // Consistent right alignment for monetary values
    },
    percentage: {
      textAlign: 'center' // Consistent center alignment for percentage values
    }
  };
  
  if (!holdings || holdings.length === 0) {
    return (
      <Box textAlign="center" py={3}>
        <Typography variant="body2" color="text.secondary">
          Nenhuma posição encontrada no portfólio
        </Typography>
      </Box>
    );
  }
  
  // Calculate totals for footer
  const totals = {
    investedValue: 0,
    currentValue: 0,
    return: 0
  };
  
  holdings.forEach(asset => {
    totals.investedValue += asset.invested_value || 0;
    totals.currentValue += asset.current_value || 0;
    totals.return += (asset.current_value || 0) - (asset.invested_value || 0);
  });
  
  const totalReturnPct = totals.investedValue > 0 
    ? ((totals.currentValue / totals.investedValue) - 1) * 100 
    : 0;  // Format currency in BRL style with exactly 2 decimal places
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
  };
  
  // Format percentage values consistently with 2 decimal places
  const formatPercentage = (value) => {
    const numValue = typeof value === 'number' ? value : parseFloat(value || 0);
    return `${numValue.toFixed(2)}%`;
  };

  // Sort assets by current value
  const sortedHoldings = [...holdings].sort((a, b) => 
    (b.current_value || 0) - (a.current_value || 0)
  );

  return (
    <TableContainer component={Paper} 
      sx={{
        boxShadow: 'none',
        backgroundColor: 'transparent',
        minWidth: 900, // Ensures the table content has a minimum width to trigger scroll
      }}
    >
      <Table size="small">        <TableHead>          <TableRow sx={{ 
            borderBottom: '2px solid #ffc107',
            '& th': { 
              fontSize: '0.85rem',
              paddingBottom: '8px'
            }
          }}>
            <TableCell sx={{ color: '#ffc107', fontWeight: 700 }}>Ativo</TableCell>
            <TableCell align="left" sx={{ color: '#ffc107', fontWeight: 700 }}>Tipo</TableCell>
            <TableCell align="center" sx={{ color: '#ffc107', fontWeight: 700 }}>Quantidade</TableCell>            
            <TableCell sx={{ ...cellStyles.monetary, color: '#ffc107', fontWeight: 700 }}>Preço Médio</TableCell>
            <TableCell sx={{ ...cellStyles.monetary, color: '#ffc107', fontWeight: 700 }}>Preço Atual</TableCell>
            <TableCell sx={{ ...cellStyles.monetary, color: '#ffc107', fontWeight: 700 }}>Valor Investido</TableCell>
            <TableCell sx={{ ...cellStyles.monetary, color: '#ffc107', fontWeight: 700 }}>Valor Atual</TableCell>
            <TableCell sx={{ ...cellStyles.monetary, color: '#ffc107', fontWeight: 700 }}>Retorno</TableCell>
            <TableCell sx={{ ...cellStyles.percentage, color: '#ffc107', fontWeight: 700 }}>Retorno (%)</TableCell>
            <TableCell sx={{ ...cellStyles.percentage, color: '#ffc107', fontWeight: 700 }}>Peso (%)</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sortedHoldings.map((asset) => {
            const returnValue = (asset.current_value || 0) - (asset.invested_value || 0);
            const returnPct = asset.return_pct || 0;
            const weightPct = totals.currentValue > 0 
              ? ((asset.current_value || 0) / totals.currentValue) * 100 
              : 0;
            
            // Determine asset type for badge
            const isBDR = asset.is_bdr;
            const isUS = asset.is_us_ticker;
            let assetType = "BR";
            let badgeColor = "success";
            
            if (isUS) {
              assetType = "US";
              badgeColor = "info";            } else if (isBDR) {
              assetType = "BDR";
              badgeColor = "purple"; // Changed to purple color for BDR badges
            }
            
            return (
              <TableRow key={asset.ticker} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="500">
                    {asset.ticker}
                  </Typography>
                </TableCell>
                <TableCell align="center">                  <Chip
                    label={assetType}
                    color={badgeColor}
                    size="small"
                    variant="filled"
                    className={assetType === 'BDR' ? 'asset-tag-bdr' : ''}
                    sx={{ 
                      minWidth: 45, 
                      fontWeight: 500
                    }}
                  />
                </TableCell>                <TableCell align="center">
                  {Math.round(asset.quantity).toLocaleString('pt-BR')}                </TableCell>                
                <TableCell sx={cellStyles.monetary}>
                  {isUS ? formatUSD(asset.avg_price) : formatBRL(asset.avg_price)}
                </TableCell>
                <TableCell sx={cellStyles.monetary}>
                  {isUS ? formatUSD(asset.current_price) : formatBRL(asset.current_price)}
                </TableCell>
                <TableCell sx={cellStyles.monetary}>
                  {formatBRL(asset.invested_value)}
                </TableCell>
                <TableCell sx={cellStyles.monetary}>
                  {formatBRL(asset.current_value)}
                </TableCell>
                <TableCell
                  sx={{ 
                    ...cellStyles.monetary,
                    color: returnValue > 0 ? 'success.main' : returnValue < 0 ? 'error.main' : 'text.primary' 
                  }}
                >
                  {formatBRL(returnValue)}                </TableCell>                
                <TableCell
                  sx={{ 
                    ...cellStyles.percentage,
                    color: returnPct > 0 ? 'success.main' : returnPct < 0 ? 'error.main' : 'text.primary',
                    fontWeight: 500
                  }}
                >
                  {returnPct > 0 ? '+' : ''}{formatPercentage(returnPct)}
                </TableCell>
                <TableCell sx={{ ...cellStyles.percentage, fontWeight: 500 }}>
                  {formatPercentage(weightPct)}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>        <TableFooter>          <TableRow sx={{ 
            '& td': { 
              fontWeight: 700, 
              borderTop: '2px solid', 
              borderTopColor: '#ffc107', 
              fontSize: '0.875rem',
              py: 1.5
            } 
          }}>
            <TableCell colSpan={5}>Total</TableCell>
            <TableCell>
              <div style={{ width: '100%', textAlign: 'left' }}>{formatBRL(totals.investedValue)}</div>
            </TableCell>
            <TableCell>
              <div style={{ width: '100%', textAlign: 'left' }}>{formatBRL(totals.currentValue)}</div>
            </TableCell>
            <TableCell>
              <div 
                style={{ 
                  width: '100%', 
                  textAlign: 'left',
                  color: totals.return > 0 ? '#2e7d32' : totals.return < 0 ? '#d32f2f' : 'inherit'
                }}
              >                {formatBRL(totals.return)}
              </div>
            </TableCell>
            <TableCell>
              <div 
                style={{ 
                  width: '100%', 
                  textAlign: 'center',
                  color: totalReturnPct > 0 ? '#2e7d32' : totalReturnPct < 0 ? '#d32f2f' : 'inherit',
                  fontWeight: 700
                }}
              >
                {totalReturnPct > 0 ? '+' : ''}{formatPercentage(totalReturnPct)}
              </div>
            </TableCell>
            <TableCell>
              <div style={{ width: '100%', textAlign: 'center', fontWeight: 700 }}>
                100.00%
              </div>
            </TableCell>
          </TableRow>
        </TableFooter>
      </Table>
    </TableContainer>
  );
};

export default HoldingsTable;
