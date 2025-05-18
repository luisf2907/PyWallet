import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';

const NotFound = () => {
  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: (theme) => `linear-gradient(135deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          width: '100%',
          maxWidth: 500,
          textAlign: 'center',
          borderRadius: 2,
        }}
      >
        <SentimentDissatisfiedIcon
          sx={{ 
            fontSize: 80,
            color: 'primary.main',
            mb: 2
          }} 
        />
        
        <Typography variant="h4" gutterBottom>
          Página não encontrada
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph>
          A página que você está tentando acessar não existe ou foi movida.
        </Typography>
        
        <Button
          variant="contained"
          component={RouterLink}
          to="/dashboard"
          sx={{ mt: 2 }}
        >
          Voltar para o Dashboard
        </Button>
      </Paper>
    </Box>
  );
};

export default NotFound;
