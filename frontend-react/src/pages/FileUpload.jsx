import React, { useState } from 'react';
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
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import SkipNextIcon from '@mui/icons-material/SkipNext';
import DownloadIcon from '@mui/icons-material/Download';
import { Layout, Alert, FileUpload } from '../components/common';
import { portfolioAPI } from '../api/portfolioAPI';
import { useAlert } from '../hooks/useAlert';

const FileUploadPage = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  
  const { showAlert } = useAlert();
  const navigate = useNavigate();
  
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
  
  return (
    <Layout>
      <Box maxWidth="md" mx="auto">
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
        
        <Alert 
          type="info" 
          message="Por favor, faça upload de um arquivo CSV ou XLSX com os dados da sua carteira."
        />
        
        <FileUpload 
          acceptedFormats={['.csv', '.xlsx']}
          onFileSelect={handleFileSelect}
          uploading={uploading}
        />
        
        <Stack direction="row" spacing={2} mb={4}>
          <Button
            variant="contained"
            startIcon={<ArrowForwardIcon />}
            disabled={!file || uploading}
            onClick={handleUpload}
            sx={{ flex: 1 }}
          >
            {uploading ? <CircularProgress size={24} color="inherit" /> : 'Continuar para o Dashboard'}
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<SkipNextIcon />}
            onClick={() => navigate('/dashboard')}
            sx={{ flex: 1 }}
          >
            Pular por enquanto
          </Button>
        </Stack>
        
        <Box mb={4}>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleDownloadTemplate}
            fullWidth
          >
            Baixar modelo de planilha
          </Button>
        </Box>
        
        {/* Seção para alterar posição de empresa específica */}
        <EmpresaUpdateSection />
      </Box>
    </Layout>
  );
};

// Componente para atualização manual de empresas
const EmpresaUpdateSection = () => {
  const [codigo, setCodigo] = useState('');
  const [preco, setPreco] = useState('');
  const [quantidade, setQuantidade] = useState('');
  const [operacaoTipo, setOperacaoTipo] = useState('compra');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  
  const { showAlert } = useAlert();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    
    // Validação básica
    if (!codigo) {
      setErrorMessage('Por favor, informe o código da empresa.');
      return;
    }
    
    if (!preco || isNaN(parseFloat(preco.replace(',', '.')))) {
      setErrorMessage('Por favor, informe um preço válido.');
      return;
    }
    
    if (!quantidade || isNaN(parseInt(quantidade))) {
      setErrorMessage('Por favor, informe uma quantidade válida.');
      return;
    }
    
    // Preparar dados para envio
    const data = {
      codigo: codigo.toUpperCase(),
      preco: parseFloat(preco.replace(',', '.')),
      quantidade: parseInt(quantidade),
      tipo_operacao: operacaoTipo
    };
    
    try {
      setIsSubmitting(true);
      const result = await portfolioAPI.updateEmpresa(data);
      
      showAlert(result.message || 'Posição atualizada com sucesso!', 'success');
      
      // Limpar o formulário
      setCodigo('');
      setPreco('');
      setQuantidade('');
    } catch (error) {
      setErrorMessage(error.message || 'Erro ao atualizar posição.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 3,
        borderRadius: 2,
        borderTop: '1px solid',
        borderColor: 'divider',
        mt: 4
      }}
    >
      <Typography variant="h5" gutterBottom>
        Alterar por Empresa
      </Typography>
      
      <Typography variant="body2" color="text.secondary" paragraph>
        Adicione ou modifique a posição de uma empresa específica em seu portfólio.
      </Typography>
      
      {errorMessage && (
        <Alert 
          type="error" 
          message={errorMessage} 
          onClose={() => setErrorMessage('')} 
          sx={{ mb: 2 }}
        />
      )}
      
      <Paper
        sx={{
          p: 3,
          borderRadius: 2,
          backgroundColor: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Box component="form" onSubmit={handleSubmit}>
          <Box mb={2}>
            <Typography variant="body2" gutterBottom>
              Código da empresa:
            </Typography>
            <TextField
              fullWidth
              id="empresa-codigo"
              placeholder="Ex: PETR4, VALE3, etc."
              value={codigo}
              onChange={(e) => setCodigo(e.target.value)}
              disabled={isSubmitting}
              size="small"
            />
          </Box>
          
          <Box mb={2}>
            <Typography variant="body2" gutterBottom>
              Tipo de operação:
            </Typography>
            <ButtonGroup fullWidth>
              <Button
                variant={operacaoTipo === 'compra' ? 'contained' : 'outlined'}
                onClick={() => setOperacaoTipo('compra')}
                startIcon={<ArrowUpwardIcon />}
              >
                Compra
              </Button>
              <Button
                variant={operacaoTipo === 'venda' ? 'contained' : 'outlined'}
                onClick={() => setOperacaoTipo('venda')}
                startIcon={<ArrowDownwardIcon />}
              >
                Venda
              </Button>
            </ButtonGroup>
          </Box>
          
          <Box mb={2}>
            <Typography variant="body2" gutterBottom>
              Preço médio:
            </Typography>
            <TextField
              fullWidth
              id="empresa-preco"
              placeholder="Use ponto ou vírgula para decimais"
              value={preco}
              onChange={(e) => setPreco(e.target.value)}
              disabled={isSubmitting}
              size="small"
            />
          </Box>
          
          <Box mb={2}>
            <Typography variant="body2" gutterBottom>
              Quantidade:
            </Typography>
            <TextField
              fullWidth
              id="empresa-quantidade"
              placeholder="Número inteiro positivo"
              value={quantidade}
              onChange={(e) => setQuantidade(e.target.value)}
              disabled={isSubmitting}
              size="small"
              helperText="Para remover uma posição, defina a quantidade como zero."
            />
          </Box>
          
          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={isSubmitting}
            startIcon={isSubmitting ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          >
            {isSubmitting ? 'Processando...' : 'Salvar Alterações'}
          </Button>
        </Box>
      </Paper>
    </Paper>
  );
};

export default FileUploadPage;
