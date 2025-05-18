import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import CurrencyExchangeIcon from '@mui/icons-material/CurrencyExchange';

/**
 * Component to display the current exchange rate
 */
const ExchangeRate = ({ rate }) => {
  if (!rate) {
    return null;
  }
    return (    <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }} className="exchange-rate-box">
      <Chip
        icon={<CurrencyExchangeIcon fontSize="small" />}
        label={`USD/BRL: ${rate.toFixed(4).replace('.', ',')}`}
        color="primary"
        variant="outlined"
        size="small"
        sx={{ fontWeight: 'bold' }}
      />
    </Box>
  );
};

export default ExchangeRate;
