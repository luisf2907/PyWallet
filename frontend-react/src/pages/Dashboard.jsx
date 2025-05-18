import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  CircularProgress,
  Button,
  Link as MuiLink,
  TextField,
  InputAdornment,
  Chip,
  Container
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import RefreshIcon from '@mui/icons-material/Refresh';
import DateRangeIcon from '@mui/icons-material/DateRange';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import DonutLargeIcon from '@mui/icons-material/DonutLarge';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import { Layout, Alert } from '../components/common';
import { 
  DistributionChart, 
  EvolutionChart, 
  HoldingsTable,
  ExchangeRate
} from '../components/dashboard';
import { portfolioAPI } from '../api/portfolioAPI';
import { useAlert } from '../hooks/useAlert';
import './Dashboard.css';

const Dashboard = () => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [exchangeRate, setExchangeRate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState(() => {
    const today = new Date();
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(today.getFullYear() - 1);
    
    return {
      startDate: formatDateForInput(oneYearAgo),
      endDate: formatDateForInput(today)
    };
  });
  
  const { showAlert } = useAlert();
  
  // Format date for input fields
  function formatDateForInput(date) {
    return date.toISOString().split('T')[0];
  }
  // Function to load portfolio data
  const loadPortfolioData = async (showLoadingIndicator = true) => {
    try {
      if (showLoadingIndicator) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }
      setError('');
      
      // Load all data in parallel for better performance
      const [summaryResponse, distributionResponse, exchangeRateData] = await Promise.all([
        portfolioAPI.getSummary(dateRange.startDate, dateRange.endDate),
        portfolioAPI.getDistribution(),
        portfolioAPI.getExchangeRate()
      ]);
      
      // Get the actual summary data from the response
      const summary = summaryResponse?.summary || {};
      const assets = summaryResponse?.assets || [];
      const evolution = summaryResponse?.evolution || [];

      console.log('Portfolio Summary:', summary);
      console.log('Assets:', assets);
      console.log('Evolution:', evolution);
      console.log('Distribution Data:', distributionResponse);
      
      // Ensure we have valid data with defaults for missing values
      const processedSummary = {
        total_current_value: summary?.total_current_value || 0,
        total_invested: summary?.total_invested || 0,
        total_return: summary?.total_return || 0,
        total_return_pct: summary?.total_return_pct || 0,
        best_asset: summary?.best_asset || '--',
        best_asset_return_pct: summary?.best_asset_return_pct || 0,
        worst_asset: summary?.worst_asset || '--',
        worst_asset_return_pct: summary?.worst_asset_return_pct || 0,
        assets: assets,
        evolution: evolution,
        cdi_return_pct: summary?.cdi_return_pct || 0,
        percentage_of_cdi: summary?.percentage_of_cdi || 0
      };
        setPortfolioData({
        summary: processedSummary,
        distribution: distributionResponse
      });
      
      if (exchangeRateData && exchangeRateData.rate) {
        setExchangeRate(exchangeRateData.rate);
      }
    } catch (err) {
      console.error('Error loading portfolio data:', err);
      setError(err.message || 'Erro ao carregar dados do portfólio');
      showAlert('Erro ao carregar dados do portfólio', 'error');
    } finally {
      if (showLoadingIndicator) {
        setLoading(false);
      } else {
        setRefreshing(false);
      }
    }
  };
  
  // Load data on component mount
  useEffect(() => {
    loadPortfolioData();
  }, []);
  
  return (
    <Layout>
      <Container maxWidth={false} disableGutters className="dashboard-wrapper" sx={{ px: 2 }}>
        <Box mb={3} display="flex" justifyContent="space-between" alignItems="center" width="100%">
          <Box>
            <Typography variant="h4" component="h1" fontWeight="600" sx={{
              background: 'linear-gradient(45deg, #ffc107, #ffd54f)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Visão Geral
            </Typography>
          </Box>
          
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => loadPortfolioData(false)}
            disabled={loading || refreshing}
          >
            {refreshing ? <CircularProgress size={20} /> : 'Atualizar'}
          </Button>
        </Box>
        
        {/* Exchange Rate Display */}
        {exchangeRate && <ExchangeRate rate={exchangeRate} />}
        
        {error && <Alert type="error" message={error} />}          {loading ? (
          <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="60vh" gap={2}>
            <CircularProgress size={60} sx={{ color: '#ffc107' }} />
            <Typography variant="h6" color="#ffc107" sx={{ mt: 2 }}>
              Carregando seu portfólio...
            </Typography>
          </Box>
        ) : !portfolioData || !portfolioData.summary ? (
          <EmptyPortfolioState />
        ) : (<Box sx={{ width: '100%', px: 0 }}>            {/* Row 1: All KPIs in a single row */}            <Box className="kpi-container">              <Box className="kpi-row">
                {/* Value KPIs */}                <Box className="kpi-item">
                  <Paper className="kpi-card" elevation={2} sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    height: '100%',
                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                      transform: 'translateY(-2px)'
                    }
                  }}>
                    <Typography variant="subtitle2" color="#ffc107" fontWeight="600" gutterBottom>
                      VALOR TOTAL
                    </Typography>
                    <Typography variant="h5" fontWeight="600" sx={{ mb: 1 }}>
                      R$ {parseFloat(portfolioData.summary.total_current_value || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </Typography>
                  </Paper>
                </Box>
                  <Box className="kpi-item">
                  <Paper className="kpi-card" elevation={2} sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    height: '100%',
                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                      transform: 'translateY(-2px)'
                    }
                  }}>
                    <Typography variant="subtitle2" color="#ffc107" fontWeight="600" gutterBottom>
                      INVESTIMENTO
                    </Typography>
                    <Typography variant="h5" fontWeight="600" sx={{ mb: 1 }}>
                      R$ {parseFloat(portfolioData.summary.total_invested || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </Typography>
                  </Paper>
                </Box>                <Box className="kpi-item">
                  <Paper className="kpi-card" elevation={2} sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    height: '100%',
                    backgroundColor: (theme) => (portfolioData.summary.total_return || 0) >= 0 
                      ? 'rgba(76, 175, 80, 0.08)' 
                      : 'rgba(244, 67, 54, 0.08)',
                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                      transform: 'translateY(-2px)'
                    }
                  }}>
                    <Typography 
                      variant="subtitle2" 
                      sx={{ 
                        fontWeight: '600',
                        color: (portfolioData.summary.total_return || 0) >= 0 ? 'success.main' : 'error.main'
                      }}
                      gutterBottom
                    >
                      RETORNO (R$)
                    </Typography>
                    <Typography 
                      variant="h5" 
                      fontWeight="600" 
                      sx={{ 
                        mb: 1, 
                        color: (portfolioData.summary.total_return || 0) >= 0 ? 'success.main' : 'error.main'  
                      }}
                    >
                      {(portfolioData.summary.total_return || 0) >= 0 ? '+' : ''}
                      R$ {parseFloat(portfolioData.summary.total_return || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}                    </Typography>
                  </Paper>
                </Box>
                
                <Box className="kpi-item">
                  <Paper className="kpi-card" elevation={2} sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    height: '100%',
                    backgroundColor: (theme) => (portfolioData.summary.total_return_pct || 0) >= 0 
                      ? 'rgba(76, 175, 80, 0.08)' 
                      : 'rgba(244, 67, 54, 0.08)',
                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                      transform: 'translateY(-2px)'
                    }
                  }}>
                    <Typography 
                      variant="subtitle2" 
                      sx={{ 
                        fontWeight: '600',
                        color: (portfolioData.summary.total_return_pct || 0) >= 0 ? 'success.main' : 'error.main'
                      }}
                      gutterBottom
                    >
                      RETORNO (%)
                    </Typography>
                    <Typography 
                      variant="h5" 
                      fontWeight="600" 
                      sx={{ 
                        mb: 1, 
                        color: (portfolioData.summary.total_return_pct || 0) >= 0 ? 'success.main' : 'error.main' 
                      }}
                    >
                      {(portfolioData.summary.total_return_pct || 0) >= 0 ? '+' : ''}
                      {parseFloat(portfolioData.summary.total_return_pct || 0).toFixed(2)}%
                    </Typography>
                  </Paper>
                </Box>
                  {/* Best Asset */}                <Box className="kpi-item">
                  <Paper className="kpi-card" elevation={2} sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    height: '100%',
                    border: (theme) => `1px solid ${(portfolioData.summary.best_asset_return_pct || 0) >= 0 ? theme.palette.success.main : theme.palette.error.main}`,
                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: (theme) => `0 5px 15px ${(portfolioData.summary.best_asset_return_pct || 0) >= 0 ? 'rgba(76, 175, 80, 0.3)' : 'rgba(244, 67, 54, 0.3)'}`,
                      transform: 'translateY(-2px)'
                    }
                  }}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <Chip 
                        label="MELHOR ATIVO" 
                        size="small" 
                        sx={{ 
                          backgroundColor: 'success.main', 
                          color: 'white',
                          fontWeight: 'bold'
                        }} 
                      />
                    </Box>
                    <Typography variant="body1" fontWeight="bold" sx={{ mt: 0.5 }}>
                      {portfolioData.summary.best_asset || '--'}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color="success.main" 
                      fontWeight="medium"
                      sx={{ display: 'flex', alignItems: 'center' }}
                    >
                      <TrendingUpIcon fontSize="small" sx={{ mr: 0.5 }} />
                      {portfolioData.summary.best_asset_return_pct ? 
                        portfolioData.summary.best_asset_return_pct.toFixed(2) : '0,00'}%
                    </Typography>
                  </Paper>
                </Box>
                  {/* Worst Asset */}                <Box className="kpi-item">
                  <Paper className="kpi-card" elevation={2} sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    height: '100%',
                    border: (theme) => `1px solid ${(portfolioData.summary.worst_asset_return_pct || 0) >= 0 ? theme.palette.success.main : theme.palette.error.main}`,
                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: (theme) => `0 5px 15px ${(portfolioData.summary.worst_asset_return_pct || 0) >= 0 ? 'rgba(76, 175, 80, 0.3)' : 'rgba(244, 67, 54, 0.3)'}`,
                      transform: 'translateY(-2px)'
                    }
                  }}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <Chip 
                        label="PIOR ATIVO" 
                        size="small" 
                        sx={{ 
                          backgroundColor: 'error.main', 
                          color: 'white',
                          fontWeight: 'bold'
                        }} 
                      />
                    </Box>
                    <Typography variant="body1" fontWeight="bold" sx={{ mt: 0.5 }}>
                      {portfolioData.summary.worst_asset || '--'}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color="error.main" 
                      fontWeight="medium"
                      sx={{ display: 'flex', alignItems: 'center' }}
                    >
                      <TrendingUpIcon fontSize="small" sx={{ mr: 0.5 }} />                      {portfolioData.summary.worst_asset_return_pct ? 
                        portfolioData.summary.worst_asset_return_pct.toFixed(2) : '0,00'}%
                    </Typography>
                  </Paper>
                </Box>
              </Box>
              <Box className="section-divider" sx={{ 
                borderBottom: '1px solid rgba(255,255,255,0.12)', 
                width: '100%', 
                my: 3 
              }} />            </Box>
            
            {/* Row 2: Charts in one row with 40/60 split (swapped positions) */}
            <Box className="charts-row" mt={4} mb={3}>
              {/* Distribution Chart (40%) - Now on the left */}
              <Box sx={{ width: { xs: '100%', md: '40%' }, mb: { xs: 2, md: 0 } }}>
                <Paper className="chart-paper" sx={{ 
                  p: 3, 
                  borderRadius: 2, 
                  height: '100%',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                }}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <DonutLargeIcon sx={{ mr: 1, color: '#ffc107' }} />
                    <Typography variant="h6" sx={{ fontWeight: '600', color: '#ffc107' }}>
                      Distribuição por Ativo
                    </Typography>
                  </Box>
                  
                  <Box className="chart-container" height="320px">
                    <DistributionChart 
                      distribution={portfolioData?.distribution?.distribution || []} 
                    />
                  </Box>
                </Paper>
              </Box>
              
              {/* Portfolio Evolution (60%) - Now on the right */}              <Box sx={{ width: { xs: '100%', md: '60%' } }}>
                <Paper className="chart-paper" sx={{ 
                  p: 3, 
                  borderRadius: 2, 
                  height: '100%',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                }}>                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2} flexWrap="wrap">
                    <Box display="flex" alignItems="center">
                      <TrendingUpIcon sx={{ mr: 1, color: '#ffc107' }} />
                      <Typography variant="h6" sx={{ fontWeight: '600', color: '#ffc107' }}>
                        Evolução da Carteira
                      </Typography>
                    </Box>
                    
                    <Box display="flex" gap={1} mt={{ xs: 2, sm: 0 }} flexWrap="wrap">                      <TextField
                        label="Data Inicial"
                        type="date"
                        size="small"
                        value={dateRange.startDate}
                        onChange={(e) => setDateRange(prev => ({ ...prev, startDate: e.target.value }))}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <DateRangeIcon fontSize="small" sx={{ color: 'white', marginLeft: '-8px' }} />
                            </InputAdornment>
                          ),
                        }}
                        sx={{ 
                          width: { xs: '100%', sm: 160 },
                          '& .MuiInputLabel-root': { marginLeft: '12px' },
                          '& .MuiInputBase-input': { paddingLeft: '8px' }
                        }}
                      />
                        <TextField
                        label="Data Final"
                        type="date"
                        size="small"
                        value={dateRange.endDate}
                        onChange={(e) => setDateRange(prev => ({ ...prev, endDate: e.target.value }))}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <DateRangeIcon fontSize="small" sx={{ color: 'white', marginLeft: '-8px' }} />
                            </InputAdornment>
                          ),
                        }}
                        sx={{ 
                          width: { xs: '100%', sm: 160 },
                          '& .MuiInputLabel-root': { marginLeft: '12px' },
                          '& .MuiInputBase-input': { paddingLeft: '8px' }
                        }}
                      />                        <Button 
                        variant="contained" 
                        size="small" 
                        onClick={() => loadPortfolioData(true)}
                        className="apply-button"
                        sx={{ 
                          height: 40, 
                          minWidth: 100,
                          marginLeft: 1,
                          backgroundColor: '#ffc107', 
                          color: '#000',
                          fontWeight: 'bold',
                          '&:hover': {
                            backgroundColor: '#ffca28',
                            transform: 'scale(1.05)',
                            transition: 'all 0.2s ease'
                          }
                        }}
                      >
                        Aplicar
                      </Button>
                    </Box>
                  </Box>
                  <Box className="chart-container" height="320px">
                    <EvolutionChart evolution={portfolioData?.summary?.evolution || []} />                  </Box>                </Paper>
              </Box>
            </Box>
              
              <Box className="section-divider" sx={{ 
                borderBottom: '1px solid rgba(255,255,255,0.12)', 
                width: '100%', 
                my: 3 
              }} />
              
              {/* Row 3: Holdings Table - full width */}
            <Box mt={4} sx={{ width: '100%' }}>
              <Typography variant="h6" gutterBottom sx={{ 
                fontWeight: 600, 
                display: 'flex', 
                alignItems: 'center', 
                mb: 2,
                color: '#ffc107'
              }}>
                <ShowChartIcon sx={{ mr: 1, color: '#ffc107' }} />
                Seus Ativos
              </Typography>              <Paper sx={{ 
                p: 3, 
                borderRadius: 2, 
                width: '100%',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }} className="assets-table-container">
                <HoldingsTable holdings={portfolioData?.summary?.assets || []} />
              </Paper>
            </Box>
          </Box>
        )}
      </Container>
    </Layout>
  );
};

// Component for empty portfolio state
const EmptyPortfolioState = () => (
  <Paper
    sx={{
      p: 4,
      textAlign: 'center',
      borderRadius: 2,
    }}
  >
    <Typography variant="h6" gutterBottom>
      Nenhum portfólio encontrado
    </Typography>
    <Typography variant="body2" color="text.secondary" paragraph>
      Parece que você ainda não importou seu portfólio. Vá para a página de gerenciar portfólio para importar seus dados.
    </Typography>
    <Button
      variant="contained"
      component={RouterLink}
      to="/file-upload"
      sx={{ mt: 2 }}
    >
      Importar Portfólio
    </Button>
  </Paper>
);

// Component for summary items
const SummaryItem = ({ label, value, isPositive, isNegative }) => (
  <Box 
    sx={{ 
      display: 'flex', 
      justifyContent: 'space-between',
      borderBottom: '1px solid',
      borderColor: 'divider',
      py: 1.5
    }}
  >
    <Typography variant="body2" color="text.secondary">
      {label}
    </Typography>
    <Typography 
      variant="body1" 
      fontWeight="500" 
      sx={{
        color: isPositive ? 'success.main' : (isNegative ? 'error.main' : 'text.primary')
      }}
    >
      {value}
    </Typography>
  </Box>
);

export default Dashboard;
