import React from 'react';
import { AppBar, Toolbar, IconButton, Box } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useTheme } from '@mui/material/styles';

const Header = ({ isMobile, onToggleSidebar }) => {
  const theme = useTheme();

  if (!isMobile) {
    return null; // No header on desktop for now, sidebar is fixed
  }

  return (
    <AppBar 
      position="fixed" // Fixed at the top
      sx={{ 
        zIndex: theme.zIndex.drawer + 1, // Ensure header is above the drawer
        backgroundColor: theme.palette.background.paper, // Match sidebar/layout style
        boxShadow: theme.shadows[2],
        transition: theme.transitions.create(['margin', 'width'], {
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
            color: theme.palette.text.primary, // Ensure icon color contrasts with background
            // Basic fade effect can be controlled by parent's logic for sidebar state
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
