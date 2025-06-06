import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Paper,
  Link,
  Stack,
  TextField,
  ButtonGroup
} from '@mui/material';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import SaveIcon from '@mui/icons-material/Save';
import CompactHoldingsTable from '../components/portfolio/CompactHoldingsTable';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import SkipNextIcon from '@mui/icons-material/SkipNext';
import DownloadIcon from '@mui/icons-material/Download';
import { Layout, Alert, FileUpload, FractionedTickerNote } from '../components/common';
import { portfolioAPI } from '../api/portfolioAPI';
import { useAlert } from '../hooks/useAlert';
import PortfolioImportTable from '../components/PortfolioImportTable';
import './FileUpload.css';

// Função para normalizar tickers fracionados (ex: VALE3F -> VALE3)
const normalizeTicker = (ticker) => {
  if (!ticker) return '';
  
  // Remove espaços e converte para maiúsculas
  ticker = ticker.trim().toUpperCase();
  
  // Detecta se é um ticker fracionado (termina com F)
  if (ticker.match(/^[A-Z0-9]{4,6}F$/)) {
    // Remove o F final para converter para a versão normal do ticker
    return ticker.slice(0, -1);
  }
  
  return ticker;
};

const FileUploadPage = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [holdings, setHoldings] = useState([]);
  const [loadingHoldings, setLoadingHoldings] = useState(true);
  
  const { showAlert } = useAlert();
  const navigate = useNavigate();
  
  // Carregar os ativos do portfólio ao montar o componente
  useEffect(() => {
    const fetchHoldings = async () => {
      try {
        setLoadingHoldings(true);
        const response = await portfolioAPI.getPortfolio();
        console.log('API response:', response);
        if (response && response.holdings) {
          console.log('Holdings encontrados:', response.holdings);
          setHoldings(response.holdings);
        } else {
          console.log('Nenhum holding encontrado na resposta');
          setHoldings([]);
        }
      } catch (error) {
        console.error('Erro ao carregar ativos do portfólio:', error);
        setHoldings([]);
      } finally {
        setLoadingHoldings(false);
      }
    };
    
    fetchHoldings();
  }, []);
  
  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
    setErrorMessage('');
  };
  
  const handleUpload = async () => {
    if (!file) {
      setErrorMessage('Por favor, selecione um arquivo para upload.');
      return;
    }
    
    try {
      setUploading(true);
      await portfolioAPI.uploadPortfolio(file);
      
      showAlert('Portfólio carregado com sucesso!', 'success');
      setTimeout(() => navigate('/dashboard'), 1500);
    } catch (error) {
      setErrorMessage(error.message || 'Erro ao fazer upload do arquivo.');
    } finally {
      setUploading(false);
    }
  };
  
  const handleDownloadTemplate = () => {
    portfolioAPI.downloadTemplate();
  };
  
  // Função para resetar a conta
  const handleResetAccount = async () => {
    setResetLoading(true);
    try {
      const { authAPI } = await import('../api/authAPI');
      await authAPI.resetAccount();
      showAlert('Todos os dados da sua conta foram apagados com sucesso.', 'success');
      setResetDialogOpen(false);
      // Opcional: recarregar a página ou redirecionar
      setTimeout(() => window.location.reload(), 1500);
    } catch (error) {
      showAlert(error.message || 'Erro ao resetar a conta.', 'error');
    } finally {
      setResetLoading(false);
    }
  };
  
  // Determinar se há ativos e se deve ajustar o layout
  const hasHoldings = !loadingHoldings && holdings && holdings.length > 0;
  console.log('Estado dos holdings:', { 
    loadingHoldings, 
    hasHoldings, 
    holdingsLength: holdings.length,
    shouldRenderTable: hasHoldings
  });
  
  return (
    <Layout>
      {/* Adicionar o CompactHoldingsTable apenas se houver ativos */}
      {hasHoldings && <CompactHoldingsTable holdings={holdings} />}
      
      <Box 
        maxWidth="md" 
        sx={{
          mx: hasHoldings ? '5px' : 'auto', // 5px da sidebar se tiver ativos, auto se não
          ml: hasHoldings ? '5px' : 'auto', // 5px da sidebar se tiver ativos, auto se não
          width: hasHoldings ? 'calc(100% - 240px)' : undefined, // Considerar o espaço para a tabela compacta (220px + 20px de margem)
          transition: 'margin 0.3s, width 0.3s' // Transição suave
        }}
      >
        <Box mb={4}>
          <Typography variant="h4" component="h1" gutterBottom fontWeight="600" sx={{
            background: 'linear-gradient(45deg, #ffc107, #ffd54f)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1
          }}>
            Gerenciar Portfólio
          </Typography>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            Configure sua carteira de investimentos de forma simples e rápida. Faça upload do seu arquivo ou use nosso modelo.
          </Typography>
        </Box>
        
        {errorMessage && (
          <Alert 
            type="error" 
            message={errorMessage} 
            onClose={() => setErrorMessage('')}
          />
        )}
        
        {/* Rest of the component... */}
      </Box>
    </Layout>
  );
};

// Rest of the file (EmpresaUpdateSection, etc.)

export default FileUploadPage;
