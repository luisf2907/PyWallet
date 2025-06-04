// Base API configuration for all service modules
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: '/api', // Will be proxied by Vite to http://localhost:5000/api
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for authentication
});

// Interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Logout user on 401 Unauthorized, but only if not in the login page
    if (error.response && error.response.status === 401 && !window.location.pathname.includes('/login') && window.location.pathname !== '/') {
      console.error('Erro de autenticação. Redirecionando para login...');
      // We can't use useNavigate here directly since this is outside React component
      // Instead, set a flag in localStorage to redirect on next render
      localStorage.setItem('auth_redirect', 'true');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Helper function to call API
export const fetchAPI = async (endpoint, method = 'GET', data = null) => {
  try {
    const config = {
      method,
    };

    if (data) {
      config.data = data;
    }    console.log(`Fazendo requisição ${method} para ${endpoint}`, data ? 'com dados' : 'sem dados');
    const response = await apiClient(endpoint, config);
    console.log(`Dados da resposta ${endpoint}:`, response.data);
    
    return response.data;
  } catch (error) {
    console.error(`Erro na API ${endpoint}:`, error);
    
    // Adicionar informações mais detalhadas para fins de depuração
    if (error.response) {
      // O servidor respondeu com um status de erro
      console.error('Detalhes do erro da resposta:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers
      });
    } else if (error.request) {
      // A requisição foi feita mas não houve resposta
      console.error('Sem resposta do servidor. Detalhes da requisição:', error.request);
    } else {
      // Ocorreu um erro ao configurar a requisição
      console.error('Erro ao configurar a requisição:', error.message);
    }
    
    throw error.response?.data?.error || error.message || 'Erro na comunicação com o servidor';
  }
};

// Helper function for file uploads
export const uploadFile = async (endpoint, file, additionalData = {}) => {
  const formData = new FormData();
  formData.append('file', file);

  // Add additional data
  Object.entries(additionalData).forEach(([key, value]) => {
    formData.append(key, value);
  });

  try {
    const response = await apiClient.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('Erro no upload:', error);
    throw error.response?.data?.error || error.message || 'Erro no upload do arquivo';
  }
};
