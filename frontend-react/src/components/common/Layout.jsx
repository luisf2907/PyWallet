import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { Box, useMediaQuery, useTheme } from '@mui/material';
import './Layout.css';

/**
 * Layout component that includes sidebar and main content area
 * 
 * @param {Object} props Component properties
 * @param {React.ReactNode} props.children Content to display in the main area
 */
const Layout = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md')); // Use md breakpoint for mobile/tablet
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile); // Sidebar open by default on desktop, closed on mobile

  const handleDrawerToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {isMobile && <Header isMobile={isMobile} onToggleSidebar={handleDrawerToggle} />} 
      <Sidebar 
        isMobile={isMobile} 
        isOpen={sidebarOpen} 
        onClose={handleDrawerToggle} 
      />
      <Box
        component="main"
        className="main-content-container"
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          backgroundColor: 'background.default',
          paddingTop: isMobile ? '56px' : 0, // Add padding to offset fixed header on mobile
          marginLeft: isMobile ? 0 : (sidebarOpen ? '250px' : 0), // Adjust margin based on sidebar state for desktop
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
