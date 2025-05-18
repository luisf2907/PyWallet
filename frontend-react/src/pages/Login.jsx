import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Avatar,
  CircularProgress
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { useAuth } from '../hooks/useAuth';
import { useAlert } from '../hooks/useAlert';
import { Alert } from '../components/common';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuth();
  const { showAlert } = useAlert();
  const navigate = useNavigate();
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('Por favor, preencha todos os campos.');
      return;
    }
    
    try {
      setIsLoading(true);
      const response = await login({ email: username, password });
      
      // Pequeno delay para garantir que o estado seja atualizado antes de navegar
      setTimeout(() => {
        showAlert('Login realizado com sucesso!', 'success');
        navigate('/dashboard', { replace: true });
      }, 100);
    } catch (err) {
      setError(err.message || 'Erro ao fazer login. Verifique suas credenciais.');
    } finally {
      setIsLoading(false);
    }
  };
  
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
          maxWidth: 400,
          borderRadius: 2,
        }}
      >
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Avatar
            sx={{
              m: '0 auto',
              bgcolor: 'primary.main',
              width: 56,
              height: 56,
            }}
          >
            <LockOutlinedIcon fontSize="large" />
          </Avatar>
          <Typography variant="h4" component="h1" sx={{ mt: 2, fontWeight: 500 }}>
            PyWallet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Gerencie seus investimentos de forma simples
          </Typography>
        </Box>
        
        {error && <Alert type="error" message={error} onClose={() => setError('')} />}
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="username"
            label="Nome de usuário"
            name="username"
            autoComplete="username"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isLoading}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Senha"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2, py: 1.2 }}
            disabled={isLoading}
          >
            {isLoading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Entrar'
            )}
          </Button>
          <Typography variant="body2" color="text.secondary" align="center">
            © 2025 PyWallet - Todos os direitos reservados
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default Login;
