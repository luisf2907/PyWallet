import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import { useAlert } from '../hooks/useAlert';
import { Alert } from '../components/common';

const ProphitLogo = '/Prophit_logo.png';

const Login = () => {
  const [tab, setTab] = useState(0);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [registerData, setRegisterData] = useState({ name: '', email: '', password: '', confirmPassword: '' });
  const [registerLoading, setRegisterLoading] = useState(false);
  const [registerError, setRegisterError] = useState('');

  const { login, register } = useAuth();
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

  const handleRegister = async (e) => {
    e.preventDefault();
    setRegisterError('');
    const { name, email, password, confirmPassword } = registerData;
    if (!name || !email || !password || !confirmPassword) {
      setRegisterError('Por favor, preencha todos os campos.');
      return;
    }
    if (password !== confirmPassword) {
      setRegisterError('As senhas não coincidem.');
      return;
    }
    try {
      setRegisterLoading(true);
      await register({ name, email, password });
      showAlert('Cadastro realizado com sucesso!', 'success');
      setTab(0);
      setRegisterData({ name: '', email: '', password: '', confirmPassword: '' });
    } catch (err) {
      setRegisterError(err.message || 'Erro ao cadastrar.');
    } finally {
      setRegisterLoading(false);
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
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 2, mb: 1 }}>
            <img src={ProphitLogo} alt="Prophit Logo" style={{ width: 180, height: 180, marginTop: -48, marginBottom: 0, objectFit: 'contain', display: 'block' }} />
            <Typography variant="h4" component="h1" sx={{ mt: 1, fontWeight: 700, fontFamily: 'Montserrat, Segoe UI, Arial, sans-serif', letterSpacing: 1 }}>
              PROPHIT!
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Gerencie seus investimentos de forma simples
            </Typography>
          </Box>
        </Box>
        <Tabs value={tab} onChange={(_, v) => { setTab(v); setError(''); setRegisterError(''); }} centered sx={{ mb: 2 }}>
          <Tab label="Login" />
          <Tab label="Cadastro" />
        </Tabs>
        {tab === 0 && (
          <>
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
                © 2025 Prophit! - Todos os direitos reservados
              </Typography>
            </Box>
          </>
        )}
        {tab === 1 && (
          <>
            {registerError && <Alert type="error" message={registerError} onClose={() => setRegisterError('')} />}
            <Box component="form" onSubmit={handleRegister} sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                label="Nome completo"
                name="name"
                autoComplete="name"
                value={registerData.name}
                onChange={e => setRegisterData({ ...registerData, name: e.target.value })}
                disabled={registerLoading}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                label="Email"
                name="email"
                autoComplete="email"
                value={registerData.email}
                onChange={e => setRegisterData({ ...registerData, email: e.target.value })}
                disabled={registerLoading}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                label="Senha"
                name="password"
                type="password"
                autoComplete="new-password"
                value={registerData.password}
                onChange={e => setRegisterData({ ...registerData, password: e.target.value })}
                disabled={registerLoading}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                label="Confirmar senha"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                value={registerData.confirmPassword}
                onChange={e => setRegisterData({ ...registerData, confirmPassword: e.target.value })}
                disabled={registerLoading}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2, py: 1.2 }}
                disabled={registerLoading}
              >
                {registerLoading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Cadastrar'
                )}
              </Button>
            </Box>
          </>
        )}
      </Paper>
    </Box>
  );
};

export default Login;
