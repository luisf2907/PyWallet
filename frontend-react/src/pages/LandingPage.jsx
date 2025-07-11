import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Container,
  Grid,
  Card,
  CardContent,
  Stack,
  Paper,
  useMediaQuery,
  useTheme
} from '@mui/material';
import AssessmentIcon from '@mui/icons-material/Assessment';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import EqualizerIcon from '@mui/icons-material/Equalizer';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';

const ProphitLogo = '/Prophit_logo.png';

const FeatureCard = ({ icon, title, description }) => (
  <Card 
    elevation={4}
    sx={{ 
      height: '100%', 
      transition: 'transform 0.3s, box-shadow 0.3s',
      '&:hover': {
        transform: 'translateY(-8px)',
        boxShadow: '0 12px 20px rgba(0, 0, 0, 0.3)'
      }
    }}
  >
    <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
      <Box 
        sx={{ 
          p: 1.5, 
          borderRadius: '50%', 
          mb: 2,
          background: 'linear-gradient(45deg, rgba(255, 193, 7, 0.2), rgba(255, 213, 79, 0.2))',
          color: 'primary.main',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center'
        }}
      >
        {icon}
      </Box>
      <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 600 }}>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {description}
      </Typography>
    </CardContent>
  </Card>
);

const LandingPage = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Renderiza a versão móvel ou desktop com base no tamanho da tela
  return isMobile ? <MobileLandingPage navigate={navigate} /> : <DesktopLandingPage navigate={navigate} />;
};

// Versão para dispositivos móveis (exatamente como estava)
const MobileLandingPage = ({ navigate }) => {
  return (
    <Box 
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
      }}
    >
      {/* Header */}
      <Box 
        sx={{ 
          py: 2, 
          px: 4, 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <img 
            src={ProphitLogo} 
            alt="Prophit Logo" 
            style={{ 
              width: 40,
              height: 40,
              objectFit: 'contain',
              marginRight: 12
            }}
          />
          <Typography 
            variant="h5" 
            component="h1" 
            sx={{ 
              fontWeight: 700, 
              fontFamily: 'Montserrat, Segoe UI, Arial, sans-serif',
              letterSpacing: 1 
            }}
          >
            Prophit!
          </Typography>
        </Box>
        <Button 
          component={Link}
          to="/login"
          variant="contained" 
          color="primary" 
          sx={{ 
            px: 3,
            py: 1,
            fontWeight: 600
          }}
        >
          Entrar
        </Button>
      </Box>

      {/* Hero Section */}
      <Box 
        sx={{ 
          pt: { xs: 8, md: 12 }, 
          pb: { xs: 10, md: 14 },
          background: 'linear-gradient(to bottom, rgba(18, 18, 18, 0.9), rgba(18, 18, 18, 0.95))',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: 'radial-gradient(circle at 20% 30%, rgba(255, 193, 7, 0.15) 0%, transparent 60%), radial-gradient(circle at 80% 70%, rgba(255, 193, 7, 0.1) 0%, transparent 50%)',
            zIndex: 0
          }
        }}
      >
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ textAlign: { xs: 'center', md: 'left' } }}>
                <Typography 
                  variant="h2" 
                  component="h2" 
                  sx={{ 
                    fontWeight: 800, 
                    mb: 3,
                    fontSize: { xs: '2.5rem', md: '3.5rem' },
                    background: 'linear-gradient(45deg, #ffc107 30%, #ffd54f 90%)',
                    backgroundClip: 'text',
                    textFillColor: 'transparent',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Gerencie seus investimentos de forma inteligente
                </Typography>
                <Typography 
                  variant="h6" 
                  color="text.secondary" 
                  sx={{ mb: 4, fontWeight: 400, lineHeight: 1.6 }}
                >
                  Acompanhe, analise e otimize sua carteira de investimentos com uma plataforma completa e fácil de usar.
                </Typography>
                <Button 
                  component={Link}
                  to="/login"
                  variant="contained" 
                  size="large" 
                  sx={{ 
                    py: 1.5,
                    px: 4,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    boxShadow: '0 8px 25px rgba(255, 193, 7, 0.3)'
                  }}
                >
                  Começar agora
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6} sx={{ display: 'flex', justifyContent: 'center' }}>
              <Box 
                sx={{
                  position: 'relative',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  width: '100%',
                  maxWidth: 500,
                  height: 'auto',
                }}
              >
                <img 
                  src={ProphitLogo} 
                  alt="Prophit Dashboard" 
                  style={{ 
                    width: '100%',
                    maxWidth: 380,
                    height: 'auto',
                    zIndex: 2,
                    filter: 'drop-shadow(0 10px 30px rgba(255, 193, 7, 0.3))'
                  }}
                />
                <Box 
                  sx={{
                    position: 'absolute',
                    width: '80%',
                    height: '80%',
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(255, 193, 7, 0.2) 0%, transparent 70%)',
                    filter: 'blur(40px)',
                    zIndex: 1
                  }}
                />
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 8, md: 12 } }}>
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography 
            variant="h3" 
            component="h2" 
            sx={{ 
              fontWeight: 700, 
              mb: 2,
              color: 'primary.main' 
            }}
          >
            Recursos
          </Typography>
          <Typography 
            variant="h6" 
            color="text.secondary" 
            sx={{ maxWidth: 700, mx: 'auto' }}
          >
            Tudo o que você precisa para gerenciar seus investimentos em um só lugar
          </Typography>
        </Box>
        
        <Grid container spacing={4}>
          <Grid item xs={12} sm={6} md={3}>
            <FeatureCard 
              icon={<AccountBalanceWalletIcon sx={{ fontSize: 40 }} />}
              title="Gestão de Portfólio"
              description="Acompanhe todos os seus investimentos em uma visão consolidada e atualizada."
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FeatureCard 
              icon={<TrendingUpIcon sx={{ fontSize: 40 }} />}
              title="Análise de Desempenho"
              description="Acompanhe a evolução dos seus investimentos ao longo do tempo com gráficos detalhados."
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FeatureCard 
              icon={<EqualizerIcon sx={{ fontSize: 40 }} />}
              title="Distribuição de Ativos"
              description="Visualize como seus investimentos estão distribuídos por classes de ativos."
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FeatureCard 
              icon={<AssessmentIcon sx={{ fontSize: 40 }} />}
              title="Controle de Dividendos"
              description="Acompanhe os dividendos recebidos e projete rendimentos futuros."
            />
          </Grid>
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box sx={{ backgroundColor: 'background.paper', py: { xs: 8, md: 12 } }}>
        <Container maxWidth="md">
          <Paper 
            elevation={6}
            sx={{ 
              p: { xs: 4, md: 6 }, 
              borderRadius: 4,
              background: 'linear-gradient(135deg, rgba(30, 30, 30, 0.9) 0%, rgba(18, 18, 18, 0.95) 100%)',
              position: 'relative',
              overflow: 'hidden',
              '&::after': {
                content: '""',
                position: 'absolute',
                top: 0,
                right: 0,
                width: '100%',
                height: '100%',
                backgroundImage: 'radial-gradient(circle at 90% 10%, rgba(255, 193, 7, 0.15) 0%, transparent 60%)',
                zIndex: 0
              }
            }}
          >
            <Box sx={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
              <Typography 
                variant="h4" 
                component="h2" 
                sx={{ 
                  fontWeight: 700, 
                  mb: 3,
                  color: 'primary.main'
                }}
              >
                Pronto para otimizar seus investimentos?
              </Typography>
              <Typography 
                variant="body1" 
                color="text.secondary" 
                sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}
              >
                Comece agora mesmo a usar o Prophit! e descubra como é fácil acompanhar e analisar seus investimentos de forma eficiente.
              </Typography>
              <Button 
                component={Link}
                to="/login"
                variant="contained" 
                size="large" 
                sx={{ 
                  py: 1.5,
                  px: 4,
                  fontWeight: 600
                }}
              >
                Acessar a plataforma
              </Button>
            </Box>
          </Paper>
        </Container>
      </Box>

      {/* Footer */}
      <Box 
        sx={{ 
          py: 4, 
          mt: 'auto',
          borderTop: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.default'
        }}
      >
        <Container>
          <Stack 
            direction={{ xs: 'column', md: 'row' }} 
            justifyContent="space-between" 
            alignItems="center" 
            spacing={2}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <img 
                src={ProphitLogo} 
                alt="Prophit Logo" 
                style={{ 
                  width: 32,
                  height: 32,
                  objectFit: 'contain',
                  marginRight: 10
                }}
              />
              <Typography variant="body2" color="text.secondary">
                © 2025 Prophit! - Todos os direitos reservados
              </Typography>
            </Box>
            <Stack direction="row" spacing={3}>
              <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                Termos de Uso
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                Política de Privacidade
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                Contato
              </Typography>
            </Stack>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
};

// Versão para desktop (a ser discutida)
const DesktopLandingPage = ({ navigate }) => {
  return (
    <Box 
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
      }}
    >
      {/* Header */}
      <Box 
        sx={{ 
          py: 2, 
          px: 4, 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <img 
            src={ProphitLogo} 
            alt="Prophit Logo" 
            style={{ 
              width: 40,
              height: 40,
              objectFit: 'contain',
              marginRight: 12
            }}
          />
          <Typography 
            variant="h5" 
            component="h1" 
            sx={{ 
              fontWeight: 700, 
              fontFamily: 'Montserrat, Segoe UI, Arial, sans-serif',
              letterSpacing: 1 
            }}
          >
            Prophit!
          </Typography>
        </Box>
        <Button 
          component={Link}
          to="/login"
          variant="contained" 
          color="primary" 
          sx={{ 
            px: 3,
            py: 1,
            fontWeight: 600
          }}
        >
          Entrar
        </Button>
      </Box>

      {/* Conteúdo Desktop (a ser implementado após consulta) */}
      <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Typography variant="h5" color="text.secondary">
          Versão desktop a ser implementada conforme orientações
        </Typography>
      </Box>

      {/* Footer */}
      <Box 
        sx={{ 
          py: 4, 
          mt: 'auto',
          borderTop: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.default'
        }}
      >
        <Container>
          <Stack 
            direction="row" 
            justifyContent="space-between" 
            alignItems="center" 
            spacing={2}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <img 
                src={ProphitLogo} 
                alt="Prophit Logo" 
                style={{ 
                  width: 32,
                  height: 32,
                  objectFit: 'contain',
                  marginRight: 10
                }}
              />
              <Typography variant="body2" color="text.secondary">
                © 2025 Prophit! - Todos os direitos reservados
              </Typography>
            </Box>
            <Stack direction="row" spacing={3}>
              <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                Termos de Uso
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                Política de Privacidade
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                Contato
              </Typography>
            </Stack>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;
