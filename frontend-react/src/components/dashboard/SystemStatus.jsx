import React, { useEffect, useState } from 'react';
import { Box, Chip, Typography, CircularProgress } from '@mui/material';
import SyncIcon from '@mui/icons-material/Sync';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { utilsAPI } from '../../api/utilsAPI';
import { formatDateTime } from '../../utils/formatters';

// Helper to format minutes ago from a float value
function formatMinutesAgoValue(minutesAgo) {
  if (minutesAgo == null || isNaN(minutesAgo)) return '';
  if (minutesAgo < 1) return 'agora mesmo';
  if (minutesAgo < 60) return `${minutesAgo.toFixed(1)} min atrás`;
  const diffHr = minutesAgo / 60;
  return `${diffHr.toFixed(1)}h atrás`;
}

const SystemStatus = ({ onPriceUpdate }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdateTime, setLastUpdateTime] = useState(0);
  const fetchStatus = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await utilsAPI.getSystemStatus();
      setStatus(res);
      
      // Verificar se há uma atualização de preço recente
      if (res && res.price_update && !res.price_update.update_in_progress) {
        const lastUpdateMinutes = res.price_update.last_update_minutes_ago || 0;
        const lastUpdateTimeMs = Date.now() - (lastUpdateMinutes * 60 * 1000);
        
        // Se a última atualização for mais recente do que a que conhecemos
        // E se for menos de 5 minutos atrás, acionar o callback
        if (lastUpdateTimeMs > lastUpdateTime && lastUpdateMinutes < 5) {
          setLastUpdateTime(lastUpdateTimeMs);
          
          // Chamar o callback apenas se fornecido
          if (typeof onPriceUpdate === 'function') {
            console.log('Notificando Dashboard sobre atualização de preços');
            onPriceUpdate();
          }
        }
      }
    } catch (err) {
      setError('Erro ao consultar status do sistema');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  let content = null;
  if (loading) {
    content = (
      <Chip icon={<CircularProgress size={16} color="inherit" />} label="Verificando status..." size="small" />
    );
  } else if (error) {
    content = (
      <Chip icon={<ErrorIcon color="error" />} label={error} color="error" size="small" />
    );
  } else if (status && status.price_update) {
    if (status.price_update.update_in_progress) {
      content = (
        <Chip icon={<SyncIcon className="spin" />} label="Atualizando preços..." color="primary" size="small" />
      );
    } else {
      content = (
        <Chip 
          icon={<CheckCircleIcon color="success" />} 
          label={`Última atualização: ${formatMinutesAgoValue(status.price_update.last_update_minutes_ago)}`} 
          color="success" 
          size="small" 
        />
      );
    }
  }

  return (
    <Box sx={{ position: 'fixed', top: 16, right: 16, zIndex: 1200 }}>
      {content}
      <style>{`.spin { animation: spin 1.2s linear infinite; } @keyframes spin { 0%{transform:rotate(0deg);} 100%{transform:rotate(360deg);} }`}</style>
    </Box>
  );
};

export default SystemStatus;
