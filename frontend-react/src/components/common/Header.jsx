import React from 'react';
import { AppBar, Toolbar, IconButton, Box } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useTheme } from '@mui/material/styles';

const Header = ({ isMobile, onToggleSidebar, sidebarOpen }) => { // Added sidebarOpen
  const theme = useTheme();

  if (!isMobile) {
    return null;
  }

  return (
    <AppBar 
      position="fixed"
      elevation={0} // Make AppBar transparent
      sx={{ 
        zIndex: theme.zIndex.drawer + 1,
        backgroundColor: 'transparent', // Ensure background is transparent
        boxShadow: 'none', // Remove shadow for full transparency
        transition: theme.transitions.create(['opacity', 'visibility'], { // Transition for icon
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
      }}
    >
      <Toolbar sx={{ minHeight: '56px !important', paddingLeft: '12px !important', paddingRight: '12px !important' }}>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={onToggleSidebar}
          sx={{ 
            mr: 2,
            color: theme.palette.text.primary,
            opacity: sidebarOpen ? 0 : 1, // Fade out when sidebar is open
            visibility: sidebarOpen ? 'hidden' : 'visible', // Hide when sidebar is open
            transition: theme.transitions.create(['opacity', 'visibility'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
          }}
        >
          <MenuIcon />
        </IconButton>
        {/* You can add a title or other elements here if needed */}
        {/* <Typography variant="h6" noWrap component="div" sx={{ color: theme.palette.text.primary }}>
          Prophit!
        </Typography> */}
      </Toolbar>
    </AppBar>
  );
};

export default Header;
