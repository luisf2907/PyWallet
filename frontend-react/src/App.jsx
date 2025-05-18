import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from './hooks/useAuth';

// Importar as páginas usando React.lazy para code splitting
const Login = React.lazy(() => import('./pages/Login'));
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const FileUpload = React.lazy(() => import('./pages/FileUpload'));
const Dividends = React.lazy(() => import('./pages/Dividends'));
const NotFound = React.lazy(() => import('./pages/NotFound'));

// Componente de loading
const LoadingPage = () => (
  <Box
    sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh'
    }}
  >
    <CircularProgress color="primary" />
  </Box>
);

// Proteção de rotas
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  // Se estiver carregando, mostra o componente de loading
  if (loading) {
    return <LoadingPage />;
  }
  
  // Apenas redireciona se não estiver autenticado e não estiver carregando
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

function App() {
  return (
    <Suspense fallback={<LoadingPage />}>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/file-upload"
          element={
            <ProtectedRoute>
              <FileUpload />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dividends"
          element={
            <ProtectedRoute>
              <Dividends />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
}

export default App;
