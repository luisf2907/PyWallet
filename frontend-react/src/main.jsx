import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { CssBaseline, ThemeProvider } from '@mui/material';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import { AlertProvider } from './context/AlertContext';
import theme from './utils/theme';
import './index.css';

// Removendo StrictMode para evitar renderizações duplas em desenvolvimento
ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AlertProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </AlertProvider>
    </ThemeProvider>
  </BrowserRouter>
);
