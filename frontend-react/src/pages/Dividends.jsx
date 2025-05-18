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
  CircularProgress,
  IconButton,
  Button,
  TextField,
  InputAdornment,
  Divider,
  Grid
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import { Layout, Alert } from '../components/common';
import { DividendsChart } from '../components/dividends';
import { dividendAPI } from '../api/dividendAPI';
import { useAlert } from '../hooks/useAlert';

const Dividends = () => {
  const [dividends, setDividends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState('');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [monthlyTotals, setMonthlyTotals] = useState(Array(12).fill(0));
  const [yearTotal, setYearTotal] = useState(0);
  const [monthDetails, setMonthDetails] = useState([]);
  
  const { showAlert } = useAlert();
  
  // Load dividends data
  const loadDividends = async () => {
    try {
      setLoading(true);
      setError('');
      
      const data = await dividendAPI.getDividends();
      const allDividends = data.dividends || [];
      setDividends(allDividends);
      
      // Process data for the selected year
      processDividendsForYear(allDividends, selectedYear);
    } catch (err) {
      setError(err.message || 'Erro ao carregar dados de proventos');
      showAlert('Erro ao carregar proventos', 'error');
    } finally {
      setLoading(false);
    }
  };
  
  // Process dividends for a specific year
  const processDividendsForYear = (allDividends, year) => {
    // Filter dividends for the selected year
    const yearDividends = allDividends.filter(div => {
      const divDate = new Date(div.payment_date || div.ex_date);
      return divDate.getFullYear() === parseInt(year);
    });
    
    // Calculate monthly totals
    const monthTotals = Array(12).fill(0);
    yearDividends.forEach(div => {
      const divDate = new Date(div.payment_date || div.ex_date);
      const month = divDate.getMonth();
      monthTotals[month] += div.value || 0;
    });
    
    // Calculate year total
    const total = monthTotals.reduce((sum, val) => sum + val, 0);
    
    setMonthlyTotals(monthTotals);
    setYearTotal(total);
    
    // Update month details
    updateMonthDetails(allDividends, year, selectedMonth);
  };
  
  // Update details for a specific month
  const updateMonthDetails = (allDividends, year, month) => {
    const monthDivs = allDividends.filter(div => {
      const divDate = new Date(div.payment_date || div.ex_date);
      return divDate.getFullYear() === parseInt(year) && 
             divDate.getMonth() === month - 1;
    });
    
    // Sort by date
    monthDivs.sort((a, b) => {
      const dateA = new Date(a.payment_date || a.ex_date);
      const dateB = new Date(b.payment_date || b.ex_date);
      return dateA - dateB;
    });
    
    setMonthDetails(monthDivs);
  };
  
  // Handle month selection from chart
  const handleMonthSelect = (month) => {
    setSelectedMonth(month);
    updateMonthDetails(dividends, selectedYear, month);
  };
  
  // Handle year change
  const handleYearChange = (e) => {
    const year = parseInt(e.target.value);
    setSelectedYear(year);
    processDividendsForYear(dividends, year);
  };
  
  // Update dividend receipt status
  const updateReceiptStatus = async (dividendId, received) => {
    try {
      setUpdating(true);
      
      await dividendAPI.updateReceiptStatus({
        dividend_id: dividendId,
        received
      });
      
      // Update local state
      setDividends(prevDividends => 
        prevDividends.map(dividend => 
          dividend.id === dividendId 
            ? { ...dividend, received } 
            : dividend
        )
      );
      
      showAlert(
        `Provento ${received ? 'marcado como recebido' : 'marcado como não recebido'}`, 
        'success'
      );
    } catch (err) {
      showAlert(err.message || 'Erro ao atualizar status', 'error');
    } finally {
      setUpdating(false);
    }
  };
    // Update month details when selected month changes
  useEffect(() => {
    if (dividends.length > 0) {
      updateMonthDetails(dividends, selectedYear, selectedMonth);
    }
  }, [selectedMonth]);
  
  // Load data on component mount
  useEffect(() => {
    loadDividends();
  }, []);
  
  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2
    }).format(value);
  };
  
  // Get month name
  const getMonthName = (month) => {
    const monthNames = [
      'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    return monthNames[month - 1];
  };
  
  return (
    <Layout>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" component="h1" fontWeight="600" sx={{
          background: 'linear-gradient(45deg, #ffc107, #ffd54f)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Proventos
        </Typography>
        
        <Box display="flex" alignItems="center" gap={2}>
          <TextField
            label="Ano"
            type="number"
            size="small"
            value={selectedYear}
            onChange={handleYearChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <CalendarMonthIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
            sx={{ width: 130 }}
          />
          
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadDividends}
            disabled={loading}
          >
            Atualizar
          </Button>
        </Box>
      </Box>
      
      {error && <Alert type="error" message={error} />}
      
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
          <CircularProgress />
        </Box>
      ) : dividends.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>
            Nenhum provento encontrado
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Os proventos serão exibidos aqui conforme forem anunciados pelas empresas.
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {/* Annual summary */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, borderRadius: 2, mb: 3 }}>
              <Typography variant="h6" mb={1}>
                Resumo Anual
              </Typography>
              <Typography>
                Proventos acumulados em {selectedYear}:&nbsp;
                <Typography component="span" fontWeight="600" color="primary">
                  {formatCurrency(yearTotal)}
                </Typography>
              </Typography>
            </Paper>
          </Grid>
          
          {/* Monthly chart */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, borderRadius: 2, mb: 3 }}>
              <Typography variant="h6" mb={2}>
                Distribuição Mensal de Proventos
              </Typography>
              
              <Box height="400px">
                <DividendsChart 
                  data={monthlyTotals} 
                  year={selectedYear} 
                  onMonthSelect={handleMonthSelect} 
                />
              </Box>
            </Paper>
          </Grid>
          
          {/* Monthly details */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, borderRadius: 2 }}>
              <Typography variant="h6" mb={2}>
                Detalhamento dos Proventos em {getMonthName(selectedMonth)}/{selectedYear}
              </Typography>
                {monthDetails.length === 0 ? (
                <Box textAlign="center" py={3}>
                  <Typography variant="body1">Nenhum provento encontrado neste mês</Typography>
                </Box>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Empresa</TableCell>
                        <TableCell>Tipo</TableCell>
                        <TableCell align="right">Valor</TableCell>
                        <TableCell align="right">Data Com</TableCell>
                        <TableCell align="right">Data Pagamento</TableCell>
                        <TableCell align="center">Status</TableCell>
                        <TableCell align="center">Ações</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {monthDetails.map((dividend) => (
                        <TableRow key={dividend.id}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="500">
                              {dividend.ticker}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={dividend.type}
                              size="small"
                              color={dividend.type === 'Dividendo' ? 'primary' : 'secondary'}
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell align="right">
                            R$ {dividend.value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </TableCell>
                          <TableCell align="right">
                            {new Date(dividend.ex_date).toLocaleDateString('pt-BR')}
                          </TableCell>
                          <TableCell align="right">
                            {dividend.payment_date ? 
                              new Date(dividend.payment_date).toLocaleDateString('pt-BR') : 
                              'Não definida'
                            }
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={dividend.received ? 'Recebido' : 'Pendente'}
                              color={dividend.received ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="center">
                            <IconButton
                              color="success"
                              size="small"
                              disabled={updating || dividend.received}
                              onClick={() => updateReceiptStatus(dividend.id, true)}
                            >
                              <CheckIcon fontSize="small" />
                            </IconButton>
                            <IconButton
                              color="error"
                              size="small"
                              disabled={updating || !dividend.received}
                              onClick={() => updateReceiptStatus(dividend.id, false)}
                            >
                              <CloseIcon fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Layout>
  );
};

export default Dividends;
