import React from 'react';
import { Box, Typography, Avatar, List, ListItem, ListItemIcon, ListItemText, 
  Button, Divider, ListItemButton } from '@mui/material';
import { NavLink } from 'react-router-dom';
import {
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  AttachMoney as MoneyIcon,
  FileUpload as FileUploadIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useAuth } from '../../hooks/useAuth';

// Styled NavLink component for active navigation
const StyledNavLink = styled(NavLink)(({ theme }) => ({
  textDecoration: 'none',
  color: 'inherit',
  width: '100%',
  '&.active .MuiListItemButton-root': {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    borderRadius: theme.shape.borderRadius,
    '& .MuiListItemIcon-root': {
      color: theme.palette.primary.contrastText,
    }
  },
}));

const Sidebar = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };  return (
    <Box
      className="sidebar"
      sx={{
        width: '250px',
        minWidth: '250px',
        height: '100vh',
        backgroundColor: 'background.paper',
        boxShadow: 2,
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        flexShrink: 0,
        zIndex: 1200,
      }}
    >
      {/* Logo and app title */}
      <Box 
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          p: 2, 
          gap: 1 
        }}
      >
        <Avatar
          sx={{
            bgcolor: 'primary.main',
            color: 'primary.contrastText',
          }}
        >
          <MoneyIcon />
        </Avatar>
        <Typography variant="h6" component="div" fontWeight="600">
          PyWallet
        </Typography>
      </Box>

      {/* User greeting */}
      <Typography variant="body2" sx={{ px: 2, pb: 2 }}>
        Olá, {user?.name || 'Usuário'}!
      </Typography>

      {/* Navigation */}
      <Typography
        variant="caption"
        sx={{
          px: 2,
          py: 0.5,
          color: 'text.secondary',
          fontWeight: 600,
        }}
      >
        Navegação
      </Typography>

      <List sx={{ px: 1 }}>
        <StyledNavLink to="/dashboard" end>
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 1, py: 1 }}>
              <ListItemIcon sx={{ minWidth: 42 }}>
                <DashboardIcon />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItemButton>
          </ListItem>
        </StyledNavLink>

        <StyledNavLink to="/file-upload">
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 1, py: 1 }}>
              <ListItemIcon sx={{ minWidth: 42 }}>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText primary="Gerenciar Portfólio" />
            </ListItemButton>
          </ListItem>
        </StyledNavLink>

        <StyledNavLink to="/dividends">
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 1, py: 1 }}>
              <ListItemIcon sx={{ minWidth: 42 }}>
                <MoneyIcon />
              </ListItemIcon>
              <ListItemText primary="Proventos" />
            </ListItemButton>
          </ListItem>
        </StyledNavLink>
      </List>

      {/* Action buttons */}
      <Box sx={{ px: 2, mt: 1 }}>
        <Button
          component={NavLink}
          to="/file-upload"
          fullWidth
          variant="contained"
          startIcon={<FileUploadIcon />}
          sx={{ mb: 1 }}
        >
          Importar Novo Portfólio
        </Button>
        
        <Button
          fullWidth
          variant="outlined"
          color="inherit"
          startIcon={<LogoutIcon />}
          onClick={handleLogout}
        >
          Sair
        </Button>
      </Box>

      {/* Footer */}
      <Box
        sx={{
          mt: 'auto',
          p: 2,
          textAlign: 'center',
          color: 'text.secondary',
          fontSize: '0.75rem',
        }}
      >
        PyWallet v1.0.0<br />© 2025 - Todos os direitos reservados
      </Box>
    </Box>
  );
};

export default Sidebar;
