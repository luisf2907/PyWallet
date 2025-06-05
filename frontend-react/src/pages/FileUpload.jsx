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
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import SkipNextIcon from '@mui/icons-material/SkipNext';
import DownloadIcon from '@mui/icons-material/Download';
import { Layout, Alert, FileUpload, FractionedTickerNote } from '../components/common';
import { portfolioAPI } from '../api/portfolioAPI';
import { useAlert } from '../hooks/useAlert';
import PortfolioImportTable from '../components/PortfolioImportTable';

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
        
        {/* 1. PLANILHA ONLINE - Primeira opção */}
        <Paper
          variant="outlined"
          sx={{
            p: 0,
            borderRadius: 2,
            overflow: 'hidden',
            mb: 4,
            bgcolor: 'transparent',  // Fundo transparente para não interferir
            width: '100%',
            boxShadow: 'none'  // Sem sombra adicional
          }}
        >
          <PortfolioImportTable 
            onSave={() => {
              showAlert('Portfólio atualizado com sucesso!', 'success');
              setTimeout(() => navigate('/dashboard'), 1500);
            }} 
          />
        </Paper>

        {/* 2. ALTERAR POR EMPRESA - Segunda opção */}
        <EmpresaUpdateSection />
        
        {/* 3. UPLOAD DE ARQUIVO - Última opção */}
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
            Importar Arquivo
          </Typography>          <Typography variant="body2" color="text.secondary" paragraph>
            Você também pode fazer upload de um arquivo CSV ou XLSX com os dados da sua carteira.
          </Typography>
          
          <Typography variant="body2" paragraph>
            Formatos aceitos: CSV e XLSX.
          </Typography>
          
          <FractionedTickerNote />
          
          <Box mt={2}>
            <FileUpload 
              acceptedFormats={['.csv', '.xlsx']}
              onFileSelect={handleFileSelect}
              uploading={uploading}
            />
          </Box>
          
          <Stack direction="row" spacing={2} mt={3}>
            <Button
              variant="contained"
              startIcon={<ArrowForwardIcon />}
              disabled={!file || uploading}
              onClick={handleUpload}
              sx={{
                flex: 1,
                backgroundColor: !file ? '#e0e0e0!important' : '#ffc107!important',
                color: '#000!important',
                fontWeight: 600,
                boxShadow: !file ? 'none' : undefined,
                minWidth: 0,
                width: '100%',
                maxWidth: '100%',
                '&:hover': {
                  backgroundColor: !file ? '#e0e0e0!important' : '#ffca28!important',
                  boxShadow: !file ? 'none' : undefined,
                  color: '#000!important',
                },
                '&.Mui-disabled': {
                  backgroundColor: '#e0e0e0!important',
                  color: '#000!important',
                  opacity: 1,
                },
              }}
            >
              {uploading ? <CircularProgress size={24} color="inherit" /> : 'Importar Arquivo'}
            </Button>
          </Stack>
          
          <Box mt={3}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<DownloadIcon />}
              onClick={handleDownloadTemplate}
              fullWidth
              sx={{
                background: 'linear-gradient(90deg, #2563eb 0%, #1e40af 100%)',
                color: '#fff',
                fontWeight: 600,
                fontSize: '1rem',
                py: 1.5,
                boxShadow: '0 4px 12px rgba(37,99,235,0.15)',
                '&:hover': {
                  background: 'linear-gradient(90deg, #1e40af 0%, #2563eb 100%)',
                  boxShadow: '0 6px 16px rgba(37,99,235,0.22)',
                },
              }}
            >
              Baixar modelo de planilha
            </Button>
          </Box>
        </Paper>
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
  const [codigoError, setCodigoError] = useState(false);
  const [precoError, setPrecoError] = useState(false);
  const [quantidadeError, setQuantidadeError] = useState(false);
  const [validatingTicker, setValidatingTicker] = useState(false);
  const [tickerValid, setTickerValid] = useState(null); // null = não validado, true = ok, false = inválido
  const codigoRef = useRef();

  // Função para validar ticker
  const validateTicker = async (ticker) => {
    if (!ticker) return;
    setValidatingTicker(true);
    setTickerValid(null);
    setCodigoError(false);
    
    try {
      // Não aceita tickers de moedas nem strings de 1 caractere
      if (ticker.length < 3 || ticker.includes('=') || ticker.match(/^[A-Z]{3,6}BRL=X$/)) {
        throw new Error('Ticker não permitido');
      }
      
      // Normaliza o ticker (converte fracionado para normal)
      const normalizedTicker = normalizeTicker(ticker);
      
      // Chama o endpoint de aporte com tipo 'compra', preco e quantidade dummy só para validar ticker
      await portfolioAPI.registerAporte({ tipo: 'compra', ticker: normalizedTicker, preco: 1, quantidade: 1 });
      setTickerValid(true);
      
      // Se o ticker foi normalizado (era fracionado), atualiza o valor do input
      if (normalizedTicker !== ticker) {
        setCodigo(normalizedTicker);
      }
    } catch (err) {
      setTickerValid(false);
      setCodigoError(true);
    } finally {
      setValidatingTicker(false);
    }
  };

  // onBlur do campo código
  const handleCodigoBlur = async () => {
    if (codigo) {
      await validateTicker(codigo.trim().toUpperCase());
    }
  };

  // Handler para mudança no campo código
  const handleCodigoChange = (e) => {
    const value = e.target.value.toUpperCase();
    setCodigo(value);
    
    // Reseta a validação quando o valor muda
    setTickerValid(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setCodigoError(false);
    setPrecoError(false);
    setQuantidadeError(false);
    
    // Validação básica
    if (!codigo) {
      setErrorMessage('Por favor, informe o código da empresa.');
      setCodigoError(true);
      return;
    }
    
    if (tickerValid === false) {
      setErrorMessage('O código informado não é um ativo válido.');
      setCodigoError(true);
      return;
    }
    
    if (!preco || isNaN(parseFloat(preco.replace(',', '.')))) {
      setErrorMessage('Por favor, informe um preço válido.');
      setPrecoError(true);
      return;
    }
    
    if (!quantidade || isNaN(parseInt(quantidade))) {
      setErrorMessage('Por favor, informe uma quantidade válida.');
      setQuantidadeError(true);
      return;
    }
    
    // Normalizar o ticker antes de enviar
    const normalizedTicker = normalizeTicker(codigo);
    
    // Preparar dados para envio
    const data = {
      codigo: normalizedTicker,
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
      // Validações detalhadas para venda
      let msg = error.message || 'Erro ao atualizar posição.';
      if (operacaoTipo === 'venda') {
        if (msg.includes('não existe no portfólio') || msg.includes('não está na carteira')) {
          msg = `Você não possui o ativo ${normalizedTicker}`;
          setCodigoError(true);
        } else if (msg.includes('maior que a disponível') || msg.includes('insuficiente para venda')) {
          msg = `Você não possui quantidade suficiente de ${normalizedTicker} para vender`;
          setQuantidadeError(true);
        }
      }
      setErrorMessage(msg);
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
      </Typography>      <Typography variant="body2" color="text.secondary" paragraph>
        Adicione ou modifique a posição de uma empresa específica em seu portfólio.
      </Typography>

      <FractionedTickerNote />
      
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
              onChange={handleCodigoChange}
              onBlur={handleCodigoBlur}
              disabled={isSubmitting}
              size="small"
              error={codigoError || (tickerValid === false && !validatingTicker)}
              inputRef={codigoRef}
              sx={{
                '& .MuiOutlinedInput-root': {
                  ...(tickerValid === true && !validatingTicker ? {
                    '& fieldset': {
                      borderColor: '#10b981', // verde
                      boxShadow: '0 0 0 1.5px #10b981',
                    },
                  } : {}),
                  ...(tickerValid === false && !validatingTicker ? {
                    '& fieldset': {
                      borderColor: '#ef4444', // vermelho
                      boxShadow: '0 0 0 1.5px #ef4444',
                    },
                  } : {}),
                },
              }}
              helperText={
                validatingTicker ? 'Validando ativo...' :
                tickerValid === false ? 'O código informado não é um ativo válido.' :
                tickerValid === true ? 'Ativo válido!' :
                ''
              }
              FormHelperTextProps={{
                sx: {
                  color: tickerValid === true && !validatingTicker ? '#10b981' : tickerValid === false && !validatingTicker ? '#ef4444' : undefined,
                  fontWeight: tickerValid === true && !validatingTicker ? 600 : undefined,
                }
              }}
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
              error={precoError}
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
              error={quantidadeError}
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
