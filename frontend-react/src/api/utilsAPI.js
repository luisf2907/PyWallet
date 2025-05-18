// Utility API service
import { fetchAPI } from './apiClient';

export const utilsAPI = {
  // Get exchange rate
  getExchangeRate: () => fetchAPI('/exchange-rate'),
  
  // Check system health
  healthCheck: () => fetchAPI('/health'),
  
  // Get system status
  getSystemStatus: () => fetchAPI('/system-status')
};
