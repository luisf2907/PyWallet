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
  const [currentYear] = useState(new Date().getFullYear());
  const [currentMonth] = useState(new Date().getMonth() + 1);
  
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
    // Normalize all dividend fields for compatibility with backend
    const normalized = allDividends.map((div) => {
      return {
        ...div,
        ex_date: div.date,
        payment_date: div.payment_date || div.date,
        type: div.event_type || div.type || 'Dividendo',
        id: div.id || `${div.ticker}-${div.date}`,
        date_obj: new Date(div.date)
      };
    });
    
    // Filter dividends for the selected year using a consistent date field
    const yearDividends = normalized.filter(div => {
      return div.date_obj.getFullYear() === parseInt(year);
    });
    
    // Recalcular totais
    recalculateTotals(yearDividends);
    
    // Update month details
    updateMonthDetails(normalized, year, selectedMonth);
  };
  
  // Função dedicada para recalcular totais de forma consistente
  const recalculateTotals = (yearDividends) => {
    const monthTotals = Array(12).fill(0);
    
    yearDividends.forEach(div => {
      if (div.received !== false) { // Considerando received como true por padrão
        const month = div.date_obj.getMonth();
        monthTotals[month] += div.value || 0;
      }
    });
    
    const total = monthTotals.reduce((sum, val) => sum + val, 0);
    setMonthlyTotals(monthTotals);
    setYearTotal(total);
  };
  // Update details for a specific month (order: alfabetical by ticker)
  const updateMonthDetails = (allDividends, year, month) => {
    // Limpar os detalhes do mês anterior ao trocar de mês
    setMonthDetails([]);
    
    const normalized = allDividends.map((div) => ({
      ...div,
      // Normalizar campos para garantir consistência
      ex_date: div.date,
      payment_date: div.payment_date || div.date,
      type: div.event_type || div.type || 'Dividendo',
      id: div.id || `${div.ticker}-${div.date}`,
      // Criar um objeto Date consistente para filtragem
      date_obj: new Date(div.date)
    }));
    
    // Aplicar filtro rigoroso por ano e mês usando sempre a mesma referência de data
    const monthDivs = normalized.filter(div => {
      return div.date_obj.getFullYear() === parseInt(year) && 
             div.date_obj.getMonth() === month - 1;
    });
    
    // Ordenar alfabeticamente por ticker
    monthDivs.sort((a, b) => {
      return a.ticker.localeCompare(b.ticker);
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
      let dividend = monthDetails.find(d => d.id === dividendId);
      if (!dividend) {
        dividend = dividends.find(d => d.id === dividendId);
      }
      if (!dividend) throw new Error('Dividendo não encontrado');
      
      // Atualizar no backend
      await dividendAPI.updateReceiptStatus({
        ticker: dividend.ticker,
        date: dividend.date,  // Usar sempre date para consistência
        received
      });
      
      // 1. Atualizar o dataset principal
      const newDividends = dividends.map(d =>
        d.id === dividendId ? { ...d, received } : d
      );
      setDividends(newDividends);
      
      // 2. Atualizar os detalhes do mês atual para refletir o novo status
      const newMonthDetails = monthDetails.map(d =>
        d.id === dividendId ? { ...d, received } : d
      );
      setMonthDetails(newMonthDetails);
      
      // 3. Normalizar e recalcular totais imediatamente
      const normalized = newDividends.map((div) => ({
        ...div,
        ex_date: div.date,
        payment_date: div.payment_date || div.date,
        type: div.event_type || div.type || 'Dividendo',
        id: div.id || `${div.ticker}-${div.date}`,
        date_obj: new Date(div.date)
      }));
      
      // Filtrar para o ano atual
      const yearDividends = normalized.filter(div => 
        div.date_obj.getFullYear() === parseInt(selectedYear)
      );
      
      // Recalcular totais para atualizar UI imediatamente
      recalculateTotals(yearDividends);
      
      showAlert(
        `Provento ${received ? 'marcado como recebido' : 'marcado como não recebido'}`,
        'success'
      );
    } catch (err) {
      showAlert(err.message || 'Erro ao atualizar status', 'error');
    } finally {
      setUpdating(false);
    }
  };  // Update month details when selected month changes
  useEffect(() => {
    if (dividends.length > 0) {
      // Limpar o estado antes de atualizar para evitar persistência incorreta
      setMonthDetails([]);
      // Normalizar dados e aplicar filtragem rigorosa
      const normalized = dividends.map((div) => ({
        ...div,
        ex_date: div.date,
        payment_date: div.payment_date || div.date,
        type: div.event_type || div.type || 'Dividendo',
        id: div.id || `${div.ticker}-${div.date}`,
        date_obj: new Date(div.date)
      }));
      updateMonthDetails(normalized, selectedYear, selectedMonth);
    }
  }, [selectedMonth]);
    // Reprocessar dados quando o ano ou dividends mudam
  useEffect(() => {
    if (dividends.length > 0) {
      processDividendsForYear(dividends, selectedYear);
    }
  }, [selectedYear, dividends]);
  
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
      <Box
        mb={3}
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        sx={{
          width: '100%',
          maxWidth: 'none',
          px: 0,
          mx: 0,
        }}
      >
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
        </Box>
      </Box>
      {/* Chart title with year and total */}
      <Box mb={2} sx={{ width: '100%', maxWidth: 'none', px: 0, mx: 0 }}>
        <Typography variant="subtitle1" fontWeight={700} fontSize={22} color="text.primary">
          {`Proventos acumulados para o ano ${selectedYear}: `}
          <span style={{ color: '#22c55e', fontWeight: 800, fontSize: 26 }}>{formatCurrency(yearTotal)}</span>
        </Typography>
      </Box>
      {error && <Alert type="error" message={error} />}
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
          <CircularProgress />
        </Box>
      ) : dividends.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center', borderRadius: 2, width: '100%', maxWidth: 'none', mx: 0 }}>
          <Typography variant="h6" gutterBottom>
            Nenhum provento encontrado
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Os proventos serão exibidos aqui conforme forem anunciados pelas empresas.
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3} sx={{ width: '100%', maxWidth: 'none', mx: 0 }}>
          {/* Monthly chart + details stacked, both full width */}
          <Grid item xs={12} sx={{ width: '100%', maxWidth: 'none', mx: 0 }}>
            <Box display="flex" flexDirection="column" gap={3} sx={{ width: '100%', maxWidth: 'none', flex: 1, px: 0, mx: 0 }}>
              <Paper sx={{ p: 3, borderRadius: 2, mb: 0, width: '100%', maxWidth: 'none', mx: 0, overflowX: 'auto' }}>
                <Typography variant="h6" mb={2}>
                  Distribuição Mensal de Proventos
                </Typography>
                <Box height="400px" width="100%" maxWidth="none" minWidth={700}>
                  <DividendsChart 
                    data={monthlyTotals} 
                    year={selectedYear} 
                    currentYear={currentYear}
                    currentMonth={currentMonth}
                    onMonthSelect={handleMonthSelect} 
                  />
                </Box>
              </Paper>
              <Paper sx={{ p: 3, borderRadius: 2, width: '100%', maxWidth: 'none', mx: 0, overflowX: 'auto' }}>
                <Typography variant="h6" mb={2}>
                  Detalhamento dos Proventos em {getMonthName(selectedMonth)}/{selectedYear}
                </Typography>
                {monthDetails.length === 0 ? (
                  <Box textAlign="center" py={3}>
                    <Typography variant="body1">Nenhum provento encontrado neste mês</Typography>
                  </Box>
                ) : (
                  <TableContainer sx={{ width: '100%', maxWidth: 'none', mx: 0, minWidth: 900 }}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell align="center">Empresa</TableCell>
                          <TableCell align="center">Tipo</TableCell>
                          <TableCell align="center">Valor</TableCell>
                          <TableCell align="center">Quantidade</TableCell>
                          <TableCell align="center">Total</TableCell>
                          <TableCell align="center">Data Pagamento</TableCell>
                          <TableCell align="center">Status</TableCell>
                          <TableCell align="center">Recebimento</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>                        {monthDetails.map((dividend) => {
                          let statusLabel, statusColor;
                          if (dividend.received !== false) {
                            statusLabel = 'Recebido';
                            statusColor = 'success';
                          } else {
                            statusLabel = 'Não Recebido';
                            statusColor = 'error';
                          }
                          
                          // Estilo para linhas de dividendos não recebidos
                          const rowStyle = dividend.received === false ? {
                            opacity: 0.65,
                            color: 'text.disabled'
                          } : {};
                          
                          return (
                            <TableRow 
                              key={dividend.id} 
                              sx={rowStyle}
                            >
                              <TableCell align="center">
                                <Typography variant="body2" fontWeight="500">
                                  {dividend.ticker}
                                </Typography>
                              </TableCell>
                              <TableCell align="center">
                                <Chip
                                  label={dividend.type}
                                  size="small"
                                  color={dividend.type === 'Dividendo' ? 'primary' : 'secondary'}
                                  variant="outlined"
                                  sx={{ minWidth: 90, justifyContent: 'center' }}
                                />
                              </TableCell>                              <TableCell align="center">
                                {(() => {
                                  // Cálculo seguro do valor unitário
                                  if (dividend.value_per_share) {
                                    return formatCurrency(dividend.value_per_share);
                                  } else if (dividend.value && dividend.quantity && dividend.quantity > 0) {
                                    return formatCurrency(dividend.value / dividend.quantity);
                                  } else {
                                    return '-';
                                  }
                                })()}
                              </TableCell>
                              <TableCell align="center">
                                {dividend.quantity ? dividend.quantity : '-'}
                              </TableCell>                              <TableCell align="center">
                                <Chip
                                  label={dividend.value ? formatCurrency(dividend.value) : '-'}
                                  size="small"
                                  sx={{ 
                                    backgroundColor: dividend.received === false ? '#aaaaaa' : '#22c55e', 
                                    color: '#111', 
                                    fontWeight: 700, 
                                    minWidth: 90, 
                                    justifyContent: 'center' 
                                  }}
                                />
                              </TableCell>
                              <TableCell align="center">
                                {dividend.payment_date ? 
                                  new Date(dividend.payment_date).toLocaleDateString('pt-BR') : 
                                  'Não definida'
                                }
                              </TableCell>
                              <TableCell align="center">
                                <Chip
                                  label={statusLabel}
                                  color={statusColor}
                                  size="small"
                                  sx={statusColor === 'error' ? { backgroundColor: '#ef4444', color: '#fff', minWidth: 90, justifyContent: 'center' } : { minWidth: 90, justifyContent: 'center' }}
                                />
                              </TableCell>
                              <TableCell align="center">
                                <Box display="flex" justifyContent="center" alignItems="center">
                                  <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: updating ? 'not-allowed' : 'pointer' }}>
                                    <input
                                      type="checkbox"
                                      checked={dividend.received === true}
                                      onChange={e => updateReceiptStatus(dividend.id, e.target.checked)}
                                      disabled={updating}
                                      style={{ display: 'none' }}
                                      aria-label="Recebimento"
                                    />
                                    <span style={{
                                      display: 'inline-block',
                                      width: 22,
                                      height: 22,
                                      borderRadius: 6,
                                      border: `2px solid ${dividend.received ? '#22c55e' : '#888'}`,
                                      background: dividend.received ? '#22c55e' : 'transparent',
                                      transition: 'all 0.2s',
                                      position: 'relative',
                                      boxShadow: dividend.received ? '0 0 0 2px #22c55e33' : 'none',
                                    }}>
                                      {dividend.received && (
                                        <svg width="16" height="16" viewBox="0 0 16 16" style={{ position: 'absolute', top: 2, left: 2 }}>
                                          <polyline points="2,9 7,14 14,4" style={{ fill: 'none', stroke: '#fff', strokeWidth: 2 }} />
                                        </svg>
                                      )}
                                    </span>
                                  </label>
                                </Box>
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </Paper>
            </Box>
          </Grid>
        </Grid>
      )}
    </Layout>
  );
};

export default Dividends;
