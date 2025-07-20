// Portfolio API service
import { fetchAPI, uploadFile } from './apiClient';

export const portfolioAPI = {
  // Test API connection
  testConnection: () => fetchAPI('/status', 'GET'),
  
  // Upload portfolio file
  uploadPortfolio: (file) => uploadFile('/upload-portfolio', file),
  
  // Get portfolio summary with date parameters
  getSummary: (startDate, endDate) => {
    const params = new URLSearchParams();
    
    if (startDate && /^\d{4}-\d{2}-\d{2}$/.test(startDate)) {
      params.append('start_date', startDate);
    }
    
    if (endDate && /^\d{4}-\d{2}-\d{2}$/.test(endDate)) {
      params.append('end_date', endDate);
    }
    
    const endpoint = `/portfolio-summary${params.toString() ? `?${params.toString()}` : ''}`;
    return fetchAPI(endpoint);
  },
  
  // Get portfolio distribution
  getDistribution: () => fetchAPI('/portfolio-distribution'),
  
  // Get current exchange rate
  getExchangeRate: () => fetchAPI('/exchange-rate'),
  
  // Download template
  downloadTemplate: () => {
    // Link to Google Drive template
    const googleDriveTemplateUrl = 'https://drive.google.com/uc?export=download&id=1W3GI8bGTNxyMdgJ05qEhPUUE_MW1AJFU';
    window.open(googleDriveTemplateUrl);
    return Promise.resolve({ message: 'Download iniciado' });
  },
  
  // Register investment contribution
  registerAporte: (data) => fetchAPI('/register-aporte', 'POST', data),
    // Manual update for a company
  updateEmpresa: (data) => fetchAPI('/empresa-update', 'POST', data),
    // Sobrescrever portfólio manualmente (importação via tabela)
  overwritePortfolio: (data) => fetchAPI('/upload-portfolio', 'POST', data),  // Registrar aportes em lote (importação via tabela em modo não sobrescrever)
  batchUpdatePortfolio: async (data) => {
    try {
      // Tentar primeiro com a URL correta
      return await fetchAPI('/register-aporte-batch', 'POST', data);
    } catch (error) {
      console.log('Erro na primeira tentativa, tentando URL alternativa...');
      // Em caso de falha, tentar com a URL alternativa
      return await fetchAPI('/batch-update', 'POST', data);
    }  },
  
  // Validar um ticker
  validateTicker: async (ticker) => {
    // Valida o ticker sem modificar o portfólio
    try {
      if (!ticker || ticker.length < 3 || ticker.includes('=') || ticker.match(/^[A-Z]{3,6}BRL=X$/)) {
        return { isValid: false };
      }
      
      // Tratamento especial para FIIs (terminados em 11)
      if (ticker.match(/^[A-Z0-9]{4}11$/)) {
        console.log(`Ticker de FII detectado: ${ticker}, considerando válido`);
        return { isValid: true };
      }
      
      // Se for um ticker fracionado (termina com F), normaliza antes de validar
      let normalizedTicker = ticker;
      if (ticker.match(/^[A-Z0-9]{4,6}F$/)) {
        normalizedTicker = ticker.slice(0, -1);
        console.log(`Ticker fracionado detectado: ${ticker} -> normalizado para: ${normalizedTicker}`);
      }
      
      await fetchAPI('/validate-ticker', 'POST', { ticker: normalizedTicker });
      return { isValid: true };
    } catch (error) {
      return { isValid: false, error };
    }
  },
  // Obter o portfólio atual com todos os ativos
  getPortfolio: async () => {
    try {
      // Usa o mesmo endpoint do summary que já retorna os holdings
      const response = await fetchAPI('/portfolio-summary');
      console.log('Resposta da API /portfolio-summary:', response);
      
      // Verifica se a resposta contém dados esperados
      if (response && response.holdings) {
        return response;
      } else if (response && response.assets) {
        // Se o campo se chamar assets, adapta para o formato esperado
        return { 
          ...response, 
          holdings: response.assets 
        };
      } else if (Array.isArray(response)) {
        // Se a resposta for um array, assume que é diretamente o array de holdings
        return { holdings: response };
      } else {
        console.warn('Formato de resposta desconhecido:', response);
        return { holdings: [] };
      }
    } catch (error) {
      console.error('Erro ao obter portfólio:', error);
      throw error;
    }
  },

  // ===== MÉTODOS PARA CRIPTOMOEDAS =====
  
  // Validar criptomoeda
  validateCrypto: async (crypto) => {
    try {
      if (!crypto || crypto.length < 2) {
        return { isValid: false };
      }
      
      const response = await fetchAPI('/crypto/validate', 'POST', { crypto });
      return {
        isValid: response.isValid,
        symbol: response.symbol,
        name: response.name,
        coingecko_id: response.coingecko_id,
        auto_recognized: response.auto_recognized,
        current_price: response.current_price
      };
    } catch (error) {
      return { isValid: false, error };
    }
  },

  // Estimar preço médio de criptomoeda
  estimateCryptoPrice: async (crypto, days = 30) => {
    try {
      const response = await fetchAPI('/crypto/estimate-price', 'POST', { crypto, days });
      return response;
    } catch (error) {
      console.error('Erro ao estimar preço de cripto:', error);
      throw error;
    }
  },

  // Atualizar carteira de criptomoedas em lote (modo Aporte/Retirada)
  batchUpdateCryptoPortfolio: async (data) => {
    try {
      return await fetchAPI('/crypto/batch-update', 'POST', data);
    } catch (error) {
      console.error('Erro no batch update de criptomoedas:', error);
      throw error;
    }
  },

  // Sobrescrever carteira de criptomoedas completamente
  overwriteCryptoPortfolio: async (data) => {
    try {
      return await fetchAPI('/crypto/overwrite', 'POST', data);
    } catch (error) {
      console.error('Erro ao sobrescrever carteira de criptomoedas:', error);
      throw error;
    }
  },

  // Limpar cache de criptomoedas (útil para desenvolvimento)
  cleanupCryptoCache: async () => {
    try {
      return await fetchAPI('/crypto/cleanup-cache', 'POST');
    } catch (error) {
      console.error('Erro ao limpar cache de criptomoedas:', error);
      throw error;
    }
  }
};
