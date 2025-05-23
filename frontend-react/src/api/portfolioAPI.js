// Portfolio API service
import { fetchAPI, uploadFile } from './apiClient';

export const portfolioAPI = {
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
  overwritePortfolio: (data) => fetchAPI('/upload-portfolio', 'POST', data),
  
  // Validar um ticker
  validateTicker: async (ticker) => {
    // Valida o ticker fazendo uma requisição de aporte com valores dummy
    try {
      if (!ticker || ticker.length < 4 || ticker.includes('=') || ticker.match(/^[A-Z]{3,6}BRL=X$/)) {
        return { isValid: false };
      }
      await fetchAPI('/register-aporte', 'POST', { tipo: 'compra', ticker, preco: 1, quantidade: 1 });
      return { isValid: true };
    } catch (error) {
      return { isValid: false, error };
    }
  }
};
