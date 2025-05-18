import React from 'react';
import { Box, Alert as MuiAlert, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

/**
 * Alert component for displaying messages
 * 
 * @param {Object} props Component properties
 * @param {string} props.type Alert type ('error', 'warning', 'info', 'success')
 * @param {string} props.message Alert message
 * @param {function} props.onClose Function to call when closing the alert
 */
const Alert = ({ type = 'info', message, onClose }) => {
  if (!message) return null;
  
  return (
    <Box mb={2}>
      <MuiAlert
        severity={type}
        variant="filled"
        action={
          onClose ? (
            <IconButton
              aria-label="close"
              color="inherit"
              size="small"
              onClick={onClose}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          ) : undefined
        }
        sx={{
          display: 'flex',
          alignItems: 'center',
          '& .MuiAlert-icon': {
            fontSize: '1.1rem',
          }
        }}
      >
        {message}
      </MuiAlert>
    </Box>
  );
};

export default Alert;
