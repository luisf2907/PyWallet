// Authentication API service
import { fetchAPI } from './apiClient';

export const authAPI = {
  // Register a new user
  register: (userData) => fetchAPI('/register', 'POST', userData),
  
  // Login user
  login: (credentials) => fetchAPI('/login', 'POST', credentials),
  
  // Logout user
  logout: () => fetchAPI('/logout', 'POST'),
  
  // Get current user
  getCurrentUser: () => fetchAPI('/user'),

  // Reset account (delete all user data except registration)
  resetAccount: () => fetchAPI('/reset-account', 'POST'),
};
