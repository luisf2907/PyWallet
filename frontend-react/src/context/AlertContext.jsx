import React, { createContext, useState } from 'react';
import { Alert, Snackbar } from '@mui/material';

export const AlertContext = createContext();

export const AlertProvider = ({ children }) => {
  const [alert, setAlert] = useState({
    open: false,
    message: '',
    type: 'info', // 'error', 'warning', 'info', 'success'
  });

  const showAlert = (message, type = 'info') => {
    setAlert({
      open: true,
      message,
      type,
    });
  };

  const closeAlert = () => {
    setAlert((prev) => ({
      ...prev,
      open: false,
    }));
  };
  return (
    <AlertContext.Provider
      value={{
        alert,
        showAlert,
        hideAlert: closeAlert,
      }}
    >
      {children}
        <Snackbar
        open={alert.open}
        autoHideDuration={5000}
        onClose={closeAlert}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={closeAlert} 
          severity={alert.type} 
          sx={{ width: '100%' }}
          variant="filled"
        >
          {alert.message}
        </Alert>
      </Snackbar>
    </AlertContext.Provider>
  );
};
