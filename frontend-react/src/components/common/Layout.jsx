import React from 'react';
import { Sidebar } from '../common';
import { Box } from '@mui/material';
import './Layout.css';

/**
 * Layout component that includes sidebar and main content area
 * 
 * @param {Object} props Component properties
 * @param {React.ReactNode} props.children Content to display in the main area
 */
const Layout = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Sidebar />
      <Box
        component="main"
        className="main-content-container"
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          backgroundColor: 'background.default',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
