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
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
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
  const [forgotOpen, setForgotOpen] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotMsg, setForgotMsg] = useState('');
  const [resetOpen, setResetOpen] = useState(false);
  const [resetToken, setResetToken] = useState('');
  const [resetPassword, setResetPassword] = useState('');
  const [resetPassword2, setResetPassword2] = useState('');
  const [resetLoading, setResetLoading] = useState(false);

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

  const handleForgot = async () => {
    setForgotMsg('');
    if (!forgotEmail) {
      setForgotMsg('Informe seu e-mail.');
      return;
    }
    setForgotLoading(true);
    try {
      const res = await fetch('/api/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotEmail })
      });
      const data = await res.json();
      if (res.ok) {
        setForgotOpen(false);
        setForgotEmail('');
        showAlert('E-mail de recuperação enviado!', 'success');
        setTimeout(() => setResetOpen(true), 400); // abre modal de token
      } else {
        showAlert(data.message || 'E-mail não cadastrado.', 'error');
        setForgotMsg('erro');
      }
    } catch (err) {
      showAlert('Erro ao conectar ao servidor.', 'error');
      setForgotMsg('erro');
    } finally {
      setForgotLoading(false);
    }
  };

  const handleResetPassword = async () => {
    if (!resetToken || !resetPassword || !resetPassword2) {
      showAlert('Preencha todos os campos.', 'error');
      return;
    }
    if (resetPassword !== resetPassword2) {
      showAlert('As senhas não coincidem.', 'error');
      return;
    }
    setResetLoading(true);
    try {
      const res = await fetch('/api/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: resetToken, password: resetPassword })
      });
      const data = await res.json();
      if (res.ok) {
        setResetOpen(false);
        setResetToken('');
        setResetPassword('');
        setResetPassword2('');
        showAlert('Senha redefinida com sucesso!', 'success');
      } else {
        showAlert(data.message || 'Token inválido ou expirado.', 'error');
      }
    } catch (err) {
      showAlert('Erro ao conectar ao servidor.', 'error');
    } finally {
      setResetLoading(false);
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
              Prophit!
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
              <Button
                variant="text"
                size="small"
                sx={{ mt: 1, mb: 1, textTransform: 'none' }}
                onClick={() => setForgotOpen(true)}
                fullWidth
              >
                Esqueci minha senha
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
      <Dialog open={forgotOpen} onClose={() => { setForgotOpen(false); setForgotMsg(''); setForgotEmail(''); }} maxWidth="xs" fullWidth PaperProps={{ sx: { minHeight: 220 } }}>
        <DialogTitle>Recuperar senha</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="E-mail"
            type="email"
            fullWidth
            value={forgotEmail}
            onChange={e => { setForgotEmail(e.target.value); setForgotMsg(''); }}
            disabled={forgotLoading}
            error={forgotMsg === 'erro'}
            sx={forgotMsg === 'erro' ? { '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'error.main', borderWidth: 2 } } } : {}}
          />
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            Insira seu email de cadastro.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setForgotOpen(false); setForgotMsg(''); setForgotEmail(''); }} disabled={forgotLoading}>Cancelar</Button>
          <Button onClick={handleForgot} disabled={forgotLoading} variant="contained">Enviar</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={resetOpen} onClose={() => { setResetOpen(false); setResetToken(''); setResetPassword(''); setResetPassword2(''); }} maxWidth="xs" fullWidth PaperProps={{ sx: { minHeight: 260 } }}>
        <DialogTitle>Redefinir senha</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="Token recebido por e-mail"
            type="text"
            fullWidth
            value={resetToken}
            onChange={e => setResetToken(e.target.value)}
            disabled={resetLoading}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Nova senha"
            type="password"
            fullWidth
            value={resetPassword}
            onChange={e => setResetPassword(e.target.value)}
            disabled={resetLoading}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Confirmar nova senha"
            type="password"
            fullWidth
            value={resetPassword2}
            onChange={e => setResetPassword2(e.target.value)}
            disabled={resetLoading}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setResetOpen(false); setResetToken(''); setResetPassword(''); setResetPassword2(''); }} disabled={resetLoading}>Cancelar</Button>
          <Button onClick={handleResetPassword} disabled={resetLoading} variant="contained">Redefinir</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Login;
