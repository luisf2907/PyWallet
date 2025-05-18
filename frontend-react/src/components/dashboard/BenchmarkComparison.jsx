import React from 'react';
import {
  Box,
  Grid,
  Typography,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import './BenchmarkComparison.css';

/**
 * Component to display benchmark comparisons
 */
const BenchmarkComparison = ({ benchmarks = {} }) => {
  const {
    cdiReturn,
    cdiDiff,
    percentageOfCdi,
    ipcaReturn = null,
    ipcaDiff = null,
    ibovespaReturn = null,
    ibovespaDiff = null,
  } = benchmarks;
  
  // Format percentage for display
  const formatPercent = (value) => {
    if (value === null || value === undefined) return '0,00%';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2).replace('.', ',')}%`;
  };
  
  return (
    <Box sx={{ p: 2, borderRadius: 2, width: '100%', bgcolor: '#1E1E1E' }} className="benchmark-paper">
      <Box 
        display="flex" 
        alignItems="center" 
        mb={2}
        ml={1}
      >
        <TrendingUpIcon sx={{ mr: 1, color: '#ffc107' }} />
        <Typography variant="h6" fontWeight="500">
          Comparação com Benchmarks
        </Typography>
      </Box>
      
      <Box className="benchmark-container">
        <Grid container spacing={2} className="benchmark-grid">
          {/* CDI */}
          <Grid item xs={12} sm={6} md={3} className="benchmark-item">
            <Box sx={{
              p: 2, 
              backgroundColor: '#212121',
              borderRadius: 1,
              height: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <Typography variant="subtitle2" color="text.secondary" fontWeight="bold" gutterBottom>
                CDI
              </Typography>
              <Typography variant="body1" fontWeight="500">
                Retorno: {formatPercent(cdiReturn)}
              </Typography>
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  color: cdiDiff >= 0 ? 'success.main' : 'error.main',
                  mt: 0.5
                }}
              >
                {cdiDiff >= 0 ? 
                  <TrendingUpIcon fontSize="small" sx={{ mr: 0.5 }} /> : 
                  <TrendingDownIcon fontSize="small" sx={{ mr: 0.5 }} />
                }                  <Typography variant="body2">
                    Diferença: {formatPercent(Math.abs(cdiDiff))}
                  </Typography>
              </Box>
              <Typography variant="body2" fontWeight="medium" mt={0.5}>
                % do CDI: {formatPercent(percentageOfCdi)}
              </Typography>
            </Box>
          </Grid>
          
          {/* IPCA */}
          <Grid item xs={12} sm={6} md={3} className="benchmark-item">
            <Box sx={{
              p: 2, 
              backgroundColor: '#212121',
              borderRadius: 1,
              height: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <Typography variant="subtitle2" color="text.secondary" fontWeight="bold" gutterBottom>
                IPCA
              </Typography>
              <Typography variant="body1" fontWeight="500">
                {ipcaReturn !== null ? 
                  `Retorno: ${formatPercent(ipcaReturn)}` : 
                  'Implementação futura'
                }
              </Typography>
              {ipcaDiff !== null && (
                <Box 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    color: ipcaDiff >= 0 ? 'success.main' : 'error.main',
                    mt: 0.5
                  }}
                >
                  {ipcaDiff >= 0 ? 
                    <TrendingUpIcon fontSize="small" sx={{ mr: 0.5 }} /> : 
                    <TrendingDownIcon fontSize="small" sx={{ mr: 0.5 }} />
                  }
                  <Typography variant="body2">
                    Diferença: {formatPercent(Math.abs(ipcaDiff))}
                  </Typography>
                </Box>
              )}
            </Box>
          </Grid>
          
          {/* IPCA+6% */}
          <Grid item xs={12} sm={6} md={3} className="benchmark-item">
            <Box sx={{
              p: 2, 
              backgroundColor: '#212121',
              borderRadius: 1,
              height: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <Typography variant="subtitle2" color="text.secondary" fontWeight="bold" gutterBottom>
                IPCA+6%
              </Typography>
              <Typography variant="body1" fontWeight="500">
                Implementa��o futura
              </Typography>
            </Box>
          </Grid>
          
          {/* IBOVESPA */}
          <Grid item xs={12} sm={6} md={3} className="benchmark-item">
            <Box sx={{
              p: 2, 
              backgroundColor: '#212121',
              borderRadius: 1,
              height: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <Typography variant="subtitle2" color="text.secondary" fontWeight="bold" gutterBottom>
                IBOVESPA
              </Typography>
              <Typography variant="body1" fontWeight="500">
                {ibovespaReturn !== null ? 
                  `Retorno: ${formatPercent(ibovespaReturn)}` : 
                  'Implementação futura'
                }
              </Typography>
              {ibovespaDiff !== null && (
                <Box 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    color: ibovespaDiff >= 0 ? 'success.main' : 'error.main',
                    mt: 0.5
                  }}
                >
                  {ibovespaDiff >= 0 ? 
                    <TrendingUpIcon fontSize="small" sx={{ mr: 0.5 }} /> : 
                    <TrendingDownIcon fontSize="small" sx={{ mr: 0.5 }} />
                  }
                  <Typography variant="body2">
                    Diferença: {formatPercent(Math.abs(ibovespaDiff))}
                  </Typography>
                </Box>
              )}
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default BenchmarkComparison;
