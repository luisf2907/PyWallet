import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Adicionar esta linha
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
    port: 3000,
    allowedHosts: ['desktop-dccjd16.hair-bull.ts.net'], // Adicionar esta linha
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
});
