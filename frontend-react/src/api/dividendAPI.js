// Dividends API service
import { fetchAPI } from './apiClient';

export const dividendAPI = {
  // Get user dividends
  getDividends: () => fetchAPI('/dividends'),
  
  // Update dividend receipt status
  updateReceiptStatus: (data) => fetchAPI('/dividend-receipt', 'POST', data),
  
  // Get dividend receipt status
  getReceiptStatus: () => fetchAPI('/dividend-receipt')
};
