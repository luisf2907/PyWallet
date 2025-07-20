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

// Componente para exibir screenshots do produto
const ProductShowcase = ({ isMobile = false }) => {
  const showcaseImages = [
    {
      src: ProphitLogo, // Será substituído por screenshot real
      alt: "Dashboard Principal",
      title: "Visão Geral Completa",
      description: "Acompanhe todos os seus investimentos em uma única tela"
    },
    {
      src: ProphitLogo, // Será substituído por screenshot real  
      alt: "Análise de Dividendos",
      title: "Controle de Dividendos",
      description: "Monitore dividendos recebidos e projeções futuras"
    },
    {
      src: ProphitLogo, // Será substituído por screenshot real
      alt: "Gestão de Portfólio", 
      title: "Gestão Inteligente",
      description: "Gerencie sua carteira com ferramentas avançadas"
    }
  ];

  if (isMobile) {
    return (
      <Box 
        sx={{
          position: 'relative',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          width: '100%',
          maxWidth: 400,
          height: 'auto',
          mx: 'auto'
        }}
      >
        <Paper
          elevation={20}
          sx={{
            width: '100%',
            height: 280,
            borderRadius: 3,
            background: 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            border: '1px solid',
            borderColor: 'divider',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 32,
              background: 'linear-gradient(90deg, #ffc107 0%, #ffd54f 100%)',
              opacity: 0.9
            }
          }}
        >
          <img 
            src={ProphitLogo} 
            alt="Prophit Dashboard" 
            style={{ 
              width: 80,
              height: 80,
              objectFit: 'contain',
              marginTop: 16,
              filter: 'drop-shadow(0 5px 15px rgba(255, 193, 7, 0.3))'
            }}
          />
          <Typography 
            variant="h6" 
            color="text.primary" 
            sx={{ mt: 2, fontWeight: 600 }}
          >
            Dashboard Prophit!
          </Typography>
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ mt: 1, textAlign: 'center', px: 3 }}
          >
            Gerencie seus investimentos com facilidade
          </Typography>
        </Paper>
        
        {/* Efeito de brilho */}
        <Box 
          sx={{
            position: 'absolute',
            width: '90%',
            height: '90%',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(255, 193, 7, 0.15) 0%, transparent 70%)',
            filter: 'blur(30px)',
            zIndex: -1
          }}
        />
      </Box>
    );
  }

  return (
    <Box 
      sx={{
        position: 'relative',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: 500
      }}
    >
      {/* Mockup principal do dashboard */}
      <Paper
        elevation={24}
        sx={{
          width: '100%',
          maxWidth: 600,
          height: 400,
          borderRadius: 3,
          background: 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)',
          display: 'flex',
          flexDirection: 'column',
          border: '1px solid',
          borderColor: 'divider',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 40,
            background: 'linear-gradient(90deg, #ffc107 0%, #ffd54f 100%)',
            opacity: 0.8
          }
        }}
      >
        {/* Header do mockup */}
        <Box sx={{ p: 2, pt: 6 }}>
          <Typography variant="h5" color="primary.main" sx={{ fontWeight: 700 }}>
            Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Visão Geral
          </Typography>
        </Box>
        
        {/* Conteúdo do mockup */}
        <Box sx={{ flex: 1, p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Cards de métricas */}
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Paper sx={{ p: 1.5, bgcolor: 'background.paper', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">VALOR TOTAL</Typography>
                <Typography variant="h6" color="primary.main" sx={{ fontWeight: 600 }}>
                  R$ 23.946,76
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6}>
              <Paper sx={{ p: 1.5, bgcolor: 'background.paper', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">RETORNO</Typography>
                <Typography variant="h6" color="error.main" sx={{ fontWeight: 600 }}>
                  -1,43%
                </Typography>
              </Paper>
            </Grid>
          </Grid>
          
          {/* Gráfico simulado */}
          <Paper sx={{ flex: 1, p: 2, bgcolor: 'background.paper', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Box sx={{ textAlign: 'center' }}>
              <EqualizerIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="body2" color="text.secondary">
                Evolução da Carteira
              </Typography>
            </Box>
          </Paper>
        </Box>
      </Paper>
      
      {/* Elementos decorativos */}
      <Box 
        sx={{
          position: 'absolute',
          width: '120%',
          height: '120%',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(255, 193, 7, 0.1) 0%, transparent 70%)',
          filter: 'blur(60px)',
          zIndex: -1
        }}
      />
    </Box>
  );
};

const FeatureCard = ({ icon, title, description }) => (
  <Card 
    elevation={4}
    sx={{ 
      height: 170, // Altura fixa reduzida (~15% menor)
      width: '100%',
      maxWidth: 340, // Largura máxima para simetria
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center', // Centraliza conteúdo
      justifyContent: 'center', // Centraliza verticalmente
      transition: 'transform 0.3s, box-shadow 0.3s',
      mx: 'auto', // Centraliza horizontalmente
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: '0 8px 16px rgba(0, 0, 0, 0.3)'
      }
    }}
  >
    <CardContent 
      sx={{ 
        p: 2.5,
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        textAlign: 'center',
        height: '100%',
        justifyContent: 'center', // Centraliza verticalmente
        gap: 1.5 // Espaçamento uniforme entre elementos
      }}
    >
      {/* Ícone - espaço fixo */}
      <Box 
        sx={{ 
          p: 1.2, 
          borderRadius: '50%', 
          background: 'linear-gradient(45deg, rgba(255, 193, 7, 0.2), rgba(255, 213, 79, 0.2))',
          color: 'primary.main',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          width: 44,
          height: 44,
          flexShrink: 0
        }}
      >
        {icon}
      </Box>
      
      {/* Título - espaço fixo */}
      <Box sx={{ height: 32, display: 'flex', alignItems: 'center' }}>
        <Typography 
          variant="h6" 
          sx={{ 
            fontWeight: 600,
            fontSize: '1rem',
            lineHeight: 1.2,
            textAlign: 'center',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}
        >
          {title}
        </Typography>
      </Box>
      
      {/* Descrição - espaço flexível */}
      <Box sx={{ flex: 1, display: 'flex', alignItems: 'center' }}>
        <Typography 
          variant="body2" 
          color="text.secondary"
          sx={{
            lineHeight: 1.4,
            fontSize: '0.85rem',
            textAlign: 'center',
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}
        >
          {description}
        </Typography>
      </Box>
    </CardContent>
  </Card>
);

const LandingPage = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

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
                  Seus investimentos, organizados de um jeito que faz sentido
                </Typography>
                <Typography 
                  variant="h6" 
                  color="text.secondary" 
                  sx={{ mb: 4, fontWeight: 400, lineHeight: 1.6 }}
                >
                  Chega de planilhas confusas! Acompanhe, analise e otimize sua carteira de investimentos de forma simples e descomplicada.
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
              <ProductShowcase isMobile={true} />
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Seção de Funcionalidades com Imagens */}
      <Box sx={{ backgroundColor: 'background.paper', py: { xs: 8, md: 12 } }}>
        <Container maxWidth="lg">
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
              Veja como funciona
            </Typography>
            <Typography 
              variant="h6" 
              color="text.secondary" 
              sx={{ maxWidth: 700, mx: 'auto' }}
            >
              Veja como é fácil gerenciar seus investimentos na prática
            </Typography>
          </Box>

          <Grid container spacing={4} justifyContent="center">
            {/* Dashboard Principal */}
            <Grid item xs={12} md={4}>
              <Paper
                elevation={12}
                sx={{
                  borderRadius: 3,
                  overflow: 'hidden',
                  background: 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)',
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <Box sx={{ p: 0, position: 'relative' }}>
                  {/* Header do mockup */}
                  <Box 
                    sx={{ 
                      height: 32,
                      background: 'linear-gradient(90deg, #ffc107 0%, #ffd54f 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      px: 2
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#000' }}>
                      Dashboard
                    </Typography>
                  </Box>
                  
                  {/* Conteúdo simulando o dashboard */}
                  <Box sx={{ p: 3 }}>
                    <Typography variant="h6" color="primary.main" sx={{ mb: 2, fontWeight: 600 }}>
                      Visão Geral
                    </Typography>
                    
                    {/* Cards de métricas */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                      <Grid item xs={6}>
                        <Paper sx={{ p: 3.2, bgcolor: 'background.default', borderRadius: 1 }}>
                          <Typography variant="caption" color="text.secondary">VALOR TOTAL</Typography>
                          <Typography variant="h6" color="primary.main" sx={{ fontWeight: 600 }}>
                            R$ 23.946,76
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={6}>
                        <Paper sx={{ p: 3.2, bgcolor: 'background.default', borderRadius: 1 }}>
                          <Typography variant="caption" color="text.secondary">RETORNO</Typography>
                          <Typography variant="h6" color="error.main" sx={{ fontWeight: 600 }}>
                            -1,43%
                          </Typography>
                        </Paper>
                      </Grid>
                    </Grid>
                    
                    {/* Gráfico simulado */}
                    <Paper sx={{ p: 3, bgcolor: 'background.default', borderRadius: 1, textAlign: 'center' }}>
                      <TrendingUpIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                      <Typography variant="body2" color="text.secondary">
                        Evolução da Carteira
                      </Typography>
                    </Paper>
                  </Box>
                </Box>
              </Paper>
            </Grid>

            {/* Dividendos */}
            <Grid item xs={12} md={4}>
              <Paper
                elevation={12}
                sx={{
                  borderRadius: 3,
                  overflow: 'hidden',
                  background: 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)',
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <Box sx={{ p: 0 }}>
                  {/* Header */}
                  <Box 
                    sx={{ 
                      height: 32,
                      background: 'linear-gradient(90deg, #ffc107 0%, #ffd54f 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      px: 2
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#000' }}>
                      Proventos
                    </Typography>
                  </Box>
                  
                  {/* Conteúdo */}
                  <Box sx={{ p: 3 }}>
                    <Typography variant="h5" color="primary.main" sx={{ mb: 1, fontWeight: 700 }}>
                      Proventos acumulados para o ano 2024: 
                    </Typography>
                    <Typography variant="h4" color="success.main" sx={{ mb: 3, fontWeight: 700 }}>
                      R$ 2.583,33
                    </Typography>
                    
                    {/* Gráfico de barras simulado */}
                    <Paper sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Distribuição Mensal de Proventos
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'end', gap: 0.5, height: 60 }}>
                        {[20, 15, 30, 18, 45, 35, 8, 42, 25, 28, 32, 60].map((height, index) => (
                          <Box 
                            key={index}
                            sx={{ 
                              flex: 1, 
                              height: `${height}%`, 
                              bgcolor: 'primary.main', 
                              borderRadius: 0.5,
                              minHeight: 4
                            }} 
                          />
                        ))}
                      </Box>
                    </Paper>
                  </Box>
                </Box>
              </Paper>
            </Grid>

            {/* Gestão de Portfólio */}
            <Grid item xs={12} md={4}>
              <Paper
                elevation={12}
                sx={{
                  borderRadius: 3,
                  overflow: 'hidden',
                  background: 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)',
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <Box sx={{ p: 0 }}>
                  {/* Header */}
                  <Box 
                    sx={{ 
                      height: 32,
                      background: 'linear-gradient(90deg, #ffc107 0%, #ffd54f 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      px: 2
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#000' }}>
                      Gerenciar Portfólio
                    </Typography>
                  </Box>
                  
                  {/* Conteúdo */}
                  <Box sx={{ p: 3 }}>
                    <Typography variant="h6" color="primary.main" sx={{ mb: 3, fontWeight: 600 }}>
                      Alterar Posições (Compra/Venda)
                    </Typography>
                    
                    {/* Tabela simulada */}
                    <Paper sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Seus Ativos
                      </Typography>
                      
                      {/* Headers */}
                      <Grid container spacing={11} sx={{ mb: 1 }}>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="text.secondary">Ativo</Typography>
                        </Grid>
                        <Grid item xs={3}>
                          <Typography variant="caption" color="text.secondary">Qtd</Typography>
                        </Grid>
                        <Grid item xs={5}>
                          <Typography variant="caption" color="text.secondary">Valor</Typography>
                        </Grid>
                      </Grid>
                      
                      {/* Linhas simuladas */}
                      {['PETR4', 'VALE3', 'ITSA3'].map((ticker, index) => (
                        <Grid container spacing={9} key={ticker} sx={{ py: 1.2 }}>
                          <Grid item xs={4}>
                            <Typography variant="body2">{ticker}</Typography>
                          </Grid>
                          <Grid item xs={3}>
                            <Typography variant="body2">{[100, 250, 124][index]}</Typography>
                          </Grid>
                          <Grid item xs={5}>
                            <Typography variant="body2" color="primary.main">
                              R$ {['2.557', '1.910', '1.290'][index]}
                            </Typography>
                          </Grid>
                        </Grid>
                      ))}
                    </Paper>
                  </Box>
                </Box>
              </Paper>
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
          </Typography>            <Typography 
              variant="h6" 
              color="text.secondary" 
              sx={{ maxWidth: 700, mx: 'auto' }}
            >
              Tudo o que você precisa para cuidar dos seus investimentos, sem complicação
            </Typography>
        </Box>
        
        <Grid 
          container 
          spacing={4} 
          alignItems="stretch"
          justifyContent="center"
          sx={{ 
            '& .MuiGrid-item': {
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              '& > *': {
                width: '100%',
                maxWidth: 340 // Garante largura máxima igual aos cards
              }
            }
          }}
        >
          {/* Primeira linha */}
          <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
            <FeatureCard 
              icon={<AccountBalanceWalletIcon sx={{ fontSize: 32 }} />}
              title="Gestão de Portfólio"
              description="Veja todos os seus investimentos em um lugar só. Simples assim!"
            />
          </Grid>
          <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
            <FeatureCard 
              icon={<TrendingUpIcon sx={{ fontSize: 32 }} />}
              title="Análise de Desempenho"
              description="Gráficos bonitos que mostram se você está ganhando ou perdendo dinheiro."
            />
          </Grid>
          
          {/* Segunda linha */}
          <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
            <FeatureCard 
              icon={<EqualizerIcon sx={{ fontSize: 32 }} />}
              title="Distribuição de Ativos"
              description="Descubra onde está concentrado seu dinheiro e balance melhor sua carteira."
            />
          </Grid>
          <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
            <FeatureCard 
              icon={<AssessmentIcon sx={{ fontSize: 32 }} />}
              title="Controle de Dividendos"
              description="Acompanhe a grana que entra todo mês dos seus dividendos."
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

// Versão para desktop - layout otimizado para telas maiores
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
      {/* Header com navegação expandida */}
      <Box 
        sx={{ 
          py: 2, 
          px: 6, 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid',
          borderColor: 'divider',
          position: 'sticky',
          top: 0,
          zIndex: 100,
          backgroundColor: 'background.default',
          backdropFilter: 'blur(10px)'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <img 
            src={ProphitLogo} 
            alt="Prophit Logo" 
            style={{ 
              width: 48,
              height: 48,
              objectFit: 'contain',
              marginRight: 16
            }}
          />
          <Typography 
            variant="h4" 
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
        
        {/* Navegação do header */}
        <Stack direction="row" spacing={4} alignItems="center">
          <Typography 
            variant="body1" 
            sx={{ 
              cursor: 'pointer', 
              fontWeight: 500,
              '&:hover': { color: 'primary.main' },
              transition: 'color 0.3s'
            }}
          >
            Recursos
          </Typography>
          <Typography 
            variant="body1" 
            sx={{ 
              cursor: 'pointer', 
              fontWeight: 500,
              '&:hover': { color: 'primary.main' },
              transition: 'color 0.3s'
            }}
          >
            Como funciona
          </Typography>
          <Typography 
            variant="body1" 
            sx={{ 
              cursor: 'pointer', 
              fontWeight: 500,
              '&:hover': { color: 'primary.main' },
              transition: 'color 0.3s'
            }}
          >
            Suporte
          </Typography>
          <Button 
            component={Link}
            to="/login"
            variant="contained" 
            color="primary" 
            size="large"
            sx={{ 
              px: 4,
              py: 1.2,
              fontWeight: 600,
              borderRadius: 2
            }}
          >
            Entrar
          </Button>
        </Stack>
      </Box>

      {/* Hero Section - Otimizado para desktop */}
      <Box 
        sx={{ 
          pt: 8, 
          pb: 12,
          background: 'linear-gradient(135deg, rgba(18, 18, 18, 0.9) 0%, rgba(30, 30, 30, 0.95) 100%)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: 'radial-gradient(circle at 25% 25%, rgba(255, 193, 7, 0.15) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(255, 193, 7, 0.1) 0%, transparent 50%)',
            zIndex: 0
          }
        }}
      >
        <Container maxWidth="xl" sx={{ position: 'relative', zIndex: 1 }}>
          <Grid container spacing={8} alignItems="center" sx={{ minHeight: '70vh' }}>
            <Grid item xs={12} lg={6}>
              <Box sx={{ maxWidth: 600 }}>
                <Typography 
                  variant="h1" 
                  component="h2" 
                  sx={{ 
                    fontWeight: 800, 
                    mb: 3,
                    fontSize: '4rem',
                    lineHeight: 1.1,
                    background: 'linear-gradient(45deg, #ffc107 30%, #ffd54f 90%)',
                    backgroundClip: 'text',
                    textFillColor: 'transparent',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Finalmente, seus investimentos organizados de verdade
                </Typography>
                <Typography 
                  variant="h5" 
                  color="text.secondary" 
                  sx={{ mb: 5, fontWeight: 400, lineHeight: 1.6 }}
                >
                  Esqueça as planilhas complicadas. Uma plataforma simples, intuitiva e poderosa 
                  para você acompanhar seus investimentos sem dor de cabeça.
                </Typography>
                <Stack direction="row" spacing={3}>
                  <Button 
                    component={Link}
                    to="/login"
                    variant="contained" 
                    size="large" 
                    sx={{ 
                      py: 2,
                      px: 5,
                      fontSize: '1.2rem',
                      fontWeight: 600,
                      borderRadius: 2,
                      boxShadow: '0 8px 25px rgba(255, 193, 7, 0.4)',
                      '&:hover': {
                        boxShadow: '0 12px 35px rgba(255, 193, 7, 0.5)',
                        transform: 'translateY(-2px)'
                      },
                      transition: 'all 0.3s'
                    }}
                  >
                    Começar agora
                  </Button>
                  <Button 
                    variant="outlined" 
                    size="large" 
                    sx={{ 
                      py: 2,
                      px: 5,
                      fontSize: '1.2rem',
                      fontWeight: 600,
                      borderRadius: 2,
                      borderColor: 'primary.main',
                      color: 'primary.main',
                      '&:hover': {
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        borderColor: 'primary.main'
                      }
                    }}
                  >
                    Ver demonstração
                  </Button>
                </Stack>
              </Box>
            </Grid>
            <Grid item xs={12} lg={6}>
              <ProductShowcase isMobile={false} />
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Seção de Funcionalidades com Imagens - Desktop */}
      <Box sx={{ backgroundColor: 'background.paper', py: 12 }}>
        <Container maxWidth="xl">
          <Box sx={{ textAlign: 'center', mb: 10 }}>
            <Typography 
              variant="h2" 
              component="h2" 
              sx={{ 
                fontWeight: 700, 
                mb: 3,
                color: 'primary.main' 
              }}
            >
              Veja como funciona
            </Typography>
            <Typography 
              variant="h5" 
              color="text.secondary" 
              sx={{ maxWidth: 800, mx: 'auto', lineHeight: 1.6 }}
            >
              Veja como é fácil gerenciar seus investimentos na prática
            </Typography>
          </Box>

          <Grid container spacing={6} justifyContent="center">
            {/* Dashboard Principal */}
            <Grid item xs={12} lg={4}>
              <Paper
                elevation={16}
                sx={{
                  borderRadius: 4,
                  overflow: 'hidden',
                  background: 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)',
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <Box sx={{ p: 0, position: 'relative' }}>
                  {/* Header do mockup */}
                  <Box 
                    sx={{ 
                      height: 40,
                      background: 'linear-gradient(90deg, #ffc107 0%, #ffd54f 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      px: 3
                    }}
                  >
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#000' }}>
                      Dashboard
                    </Typography>
                  </Box>
                  
                  {/* Conteúdo simulando o dashboard */}
                  <Box sx={{ p: 3 }}>
                    <Typography variant="h6" color="primary.main" sx={{ mb: 2, fontWeight: 600 }}>
                      Visão Geral
                    </Typography>
                    
                    {/* Cards de métricas */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                      <Grid item xs={6}>
                        <Paper sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                          <Typography variant="caption" color="text.secondary">VALOR TOTAL</Typography>
                          <Typography variant="h6" color="primary.main" sx={{ fontWeight: 600 }}>
                            R$ 23.946,76
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={6}>
                        <Paper sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                          <Typography variant="caption" color="text.secondary">RETORNO</Typography>
                          <Typography variant="h6" color="error.main" sx={{ fontWeight: 600 }}>
                            -1,43%
                          </Typography>
                        </Paper>
                      </Grid>
                    </Grid>
                    
                    {/* Gráfico simulado */}
                    <Paper sx={{ p: 3, bgcolor: 'background.default', borderRadius: 1, textAlign: 'center' }}>
                      <TrendingUpIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                      <Typography variant="body2" color="text.secondary">
                        Evolução da Carteira
                      </Typography>
                    </Paper>
                  </Box>
                </Box>
              </Paper>
            </Grid>

            {/* Dividendos */}
            <Grid item xs={12} lg={4}>
              <Paper
                elevation={16}
                sx={{
                  borderRadius: 4,
                  overflow: 'hidden',
                  background: 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)',
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <Box sx={{ p: 0 }}>
                  {/* Header */}
                  <Box 
                    sx={{ 
                      height: 40,
                      background: 'linear-gradient(90deg, #ffc107 0%, #ffd54f 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      px: 3
                    }}
                  >
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#000' }}>
                      Proventos
                    </Typography>
                  </Box>
                  
                  {/* Conteúdo */}
                  <Box sx={{ p: 3 }}>
                    <Typography variant="h5" color="primary.main" sx={{ mb: 1, fontWeight: 700 }}>
                      Proventos acumulados para o ano 2024: 
                    </Typography>
                    <Typography variant="h4" color="success.main" sx={{ mb: 3, fontWeight: 700 }}>
                      R$ 2.583,33
                    </Typography>
                    
                    {/* Gráfico de barras simulado */}
                    <Paper sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Distribuição Mensal de Proventos
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'end', gap: 1, height: 105 }}>
                        {[20, 15, 30, 18, 45, 35, 20, 42, 25, 28, 52, 90].map((height, index) => (
                          <Box 
                            key={index}
                            sx={{ 
                              flex: 1, 
                              height: `${height}%`, 
                              bgcolor: 'primary.main', 
                              borderRadius: 0.5,
                              minHeight: 4
                            }} 
                          />
                        ))}
                      </Box>
                    </Paper>
                  </Box>
                </Box>
              </Paper>
            </Grid>

            {/* Gestão de Portfólio */}
            <Grid item xs={12} lg={4}>
              <Paper
                elevation={16}
                sx={{
                  borderRadius: 4,
                  overflow: 'hidden',
                  background: 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)',
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <Box sx={{ p: 0 }}>
                  {/* Header */}
                  <Box 
                    sx={{ 
                      height: 40,
                      background: 'linear-gradient(90deg, #ffc107 0%, #ffd54f 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      px: 3
                    }}
                  >
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#000' }}>
                      Gerenciar Portfólio
                    </Typography>
                  </Box>
                  
                  {/* Conteúdo */}
                  <Box sx={{ p: 3 }}>
                    <Typography variant="h6" color="primary.main" sx={{ mb: 3, fontWeight: 600 }}>
                      Alterar Posições (Compra/Venda)
                    </Typography>
                    
                    {/* Tabela simulada */}
                    <Paper sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Seus Ativos
                      </Typography>
                      
                      {/* Headers */}
                      <Grid container spacing={12} sx={{ mb: 1 }}>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="text.secondary">Ativo</Typography>
                        </Grid>
                        <Grid item xs={3}>
                          <Typography variant="caption" color="text.secondary">Qtd</Typography>
                        </Grid>
                        <Grid item xs={5}>
                          <Typography variant="caption" color="text.secondary">Valor</Typography>
                        </Grid>
                      </Grid>
                      
                      {/* Linhas simuladas */}
                      {['PETR4', 'VALE3', 'ITSA3'].map((ticker, index) => (
                        <Grid container spacing={10} key={ticker} sx={{ py: 1.2 }}>
                          <Grid item xs={4}>
                            <Typography variant="body2">{ticker}</Typography>
                          </Grid>
                          <Grid item xs={3}>
                            <Typography variant="body2">{[100, 250, 124][index]}</Typography>
                          </Grid>
                          <Grid item xs={5}>
                            <Typography variant="body2" color="primary.main">
                              R$ {['2.557', '1.910', '1.290'][index]}
                            </Typography>
                          </Grid>
                        </Grid>
                      ))}
                    </Paper>
                  </Box>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section - Layout desktop otimizado */}
      <Container maxWidth="xl" sx={{ py: 12 }}>
        <Box sx={{ textAlign: 'center', mb: 10 }}>
          <Typography 
            variant="h2" 
            component="h2" 
            sx={{ 
              fontWeight: 700, 
              mb: 3,
              color: 'primary.main' 
            }}
          >
            Recursos poderosos
          </Typography>
          <Typography 
            variant="h5" 
            color="text.secondary" 
            sx={{ maxWidth: 800, mx: 'auto', lineHeight: 1.6 }}
          >
            Tudo o que você precisa para tomar decisões inteligentes sobre seus investimentos
          </Typography>
        </Box>
        
        <Grid container spacing={4} justifyContent="center" alignItems="stretch">
          {/* Primeira linha */}
          <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
            <FeatureCard 
              icon={<AccountBalanceWalletIcon sx={{ fontSize: 32 }} />}
              title="Gestão de Portfólio"
              description="Veja todos os seus investimentos em um lugar só. Simples assim!"
            />
          </Grid>
          <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
            <FeatureCard 
              icon={<TrendingUpIcon sx={{ fontSize: 32 }} />}
              title="Análise de Performance"
              description="Gráficos bonitos que mostram se você está ganhando ou perdendo dinheiro."
            />
          </Grid>
          
          {/* Segunda linha */}
          <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
            <FeatureCard 
              icon={<EqualizerIcon sx={{ fontSize: 32 }} />}
              title="Distribuição de Ativos"
              description="Descubra onde está concentrado seu dinheiro e balance melhor sua carteira."
            />
          </Grid>
          <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
            <FeatureCard 
              icon={<AssessmentIcon sx={{ fontSize: 32 }} />}
              title="Controle de Dividendos"
              description="Acompanhe a grana que entra todo mês dos seus dividendos."
            />
          </Grid>
        </Grid>
      </Container>

      {/* CTA Section - Layout desktop */}
      <Box sx={{ backgroundColor: 'background.paper', py: 12 }}>
        <Container maxWidth="lg">
          <Paper 
            elevation={12}
            sx={{ 
              p: 8, 
              borderRadius: 4,
              background: 'linear-gradient(135deg, rgba(30, 30, 30, 0.95) 0%, rgba(18, 18, 18, 0.98) 100%)',
              position: 'relative',
              overflow: 'hidden',
              border: '1px solid',
              borderColor: 'divider',
              '&::after': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'linear-gradient(45deg, rgba(255, 193, 7, 0.05) 0%, transparent 60%)',
                zIndex: 0
              }
            }}
          >
            <Box sx={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
              <Typography 
                variant="h3" 
                component="h2" 
                sx={{ 
                  fontWeight: 700, 
                  mb: 3,
                  background: 'linear-gradient(45deg, #ffc107 30%, #ffd54f 90%)',
                  backgroundClip: 'text',
                  textFillColor: 'transparent',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Bora começar a investir melhor?
              </Typography>
              <Typography 
                variant="h6" 
                color="text.secondary" 
                sx={{ mb: 5, maxWidth: 600, mx: 'auto', lineHeight: 1.6 }}
              >
                Junte-se a milhares de investidores que já descobriram uma forma mais simples 
                de organizar seus investimentos. É grátis para começar!
              </Typography>
              <Button 
                component={Link}
                to="/login"
                variant="contained" 
                size="large" 
                sx={{ 
                  py: 2,
                  px: 6,
                  fontSize: '1.3rem',
                  fontWeight: 600,
                  borderRadius: 2,
                  boxShadow: '0 8px 25px rgba(255, 193, 7, 0.4)',
                  '&:hover': {
                    boxShadow: '0 12px 35px rgba(255, 193, 7, 0.5)',
                    transform: 'translateY(-2px)'
                  },
                  transition: 'all 0.3s'
                }}
              >
                Criar conta gratuita
              </Button>
            </Box>
          </Paper>
        </Container>
      </Box>

      {/* Footer desktop */}
      <Box 
        sx={{ 
          py: 6, 
          borderTop: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.default'
        }}
      >
        <Container maxWidth="xl">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <img 
                  src={ProphitLogo} 
                  alt="Prophit Logo" 
                  style={{ 
                    width: 40,
                    height: 40,
                    objectFit: 'contain',
                    marginRight: 16
                  }}
                />
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.5 }}>
                    Prophit!
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    © 2025 Prophit! - Todos os direitos reservados
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Stack 
                direction="row" 
                spacing={4} 
                justifyContent={{ xs: 'center', md: 'flex-end' }}
              >
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  sx={{ 
                    cursor: 'pointer', 
                    '&:hover': { color: 'primary.main' },
                    transition: 'color 0.3s'
                  }}
                >
                  Termos de Uso
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  sx={{ 
                    cursor: 'pointer', 
                    '&:hover': { color: 'primary.main' },
                    transition: 'color 0.3s'
                  }}
                >
                  Política de Privacidade
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  sx={{ 
                    cursor: 'pointer', 
                    '&:hover': { color: 'primary.main' },
                    transition: 'color 0.3s'
                  }}
                >
                  Suporte
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  sx={{ 
                    cursor: 'pointer', 
                    '&:hover': { color: 'primary.main' },
                    transition: 'color 0.3s'
                  }}
                >
                  Contato
                </Typography>
              </Stack>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;
