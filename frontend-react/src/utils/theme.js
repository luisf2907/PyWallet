import { createTheme } from '@mui/material/styles';

// Cores extraídas do HTML original
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#ffc107', // accent-color do HTML original
    },
    secondary: {
      main: '#a0a0a0', // text-secondary do HTML original
    },
    background: {
      default: '#121212', // primary-color do HTML original
      paper: '#1e1e1e',   // secondary-color do HTML original
    },
    text: {
      primary: '#ffffff', // text-color do HTML original
      secondary: '#a0a0a0', // text-secondary do HTML original
    },
    success: {
      main: '#10b981', // green do HTML original
    },    error: {
      main: '#ef4444', // red do HTML original
    },
    purple: {
      main: '#9c27b0', // purple for BDR labels
    },
    divider: '#333333', // border-color do HTML original
  },
  shape: {
    borderRadius: 8,
  },
  typography: {
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '0.75rem',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '0.5rem',
          padding: '0.75rem',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
          },
        },
        containedPrimary: {
          background: 'linear-gradient(45deg, #ffc107, #ffd54f)',
          color: '#121212',
          '&:hover': {
            boxShadow: '0 5px 15px rgba(255, 193, 7, 0.3)',
          },
        },
        outlined: {
          borderColor: '#333333',
          '&:hover': {
            background: 'rgba(255, 255, 255, 0.05)',
          },
        },
      },
    },
  },
});

export default theme;
