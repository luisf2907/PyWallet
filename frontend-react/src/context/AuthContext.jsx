import React, { createContext, useState, useEffect } from 'react';
import { authAPI } from '../api/authAPI';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        // Adicionando um pequeno atraso antes de verificar o status
        // para evitar recargas imediatas que podem causar loops
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const userData = await authAPI.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.log('Usuário não autenticado:', error.message);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      setUser(response.user);
      setIsAuthenticated(true);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      setUser(response.user);
      setIsAuthenticated(true);
      return response;
    } catch (error) {
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        login,
        logout,
        register,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
