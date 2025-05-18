import React, { useState, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  IconButton, 
  Button,
  CircularProgress
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CloseIcon from '@mui/icons-material/Close';
import { useAlert } from '../../hooks/useAlert';

// Hidden input element
const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  whiteSpace: 'nowrap',
  width: 1,
});

/**
 * File upload component with drag and drop support
 * 
 * @param {Object} props Component properties
 * @param {Array<string>} props.acceptedFormats Accepted file formats (e.g. ['.csv', '.xlsx'])
 * @param {function} props.onFileSelect Callback when file is selected
 * @param {boolean} props.uploading Whether file is currently uploading
 */
const FileUpload = ({ 
  acceptedFormats = ['.csv', '.xlsx'], 
  onFileSelect,
  uploading = false 
}) => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const { showAlert } = useAlert();
  
  // Handle drag events
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };
  
  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files.length) {
      handleFiles(e.dataTransfer.files[0]);
    }
  };
  
  // Handle file selection
  const handleFileChange = (e) => {
    if (e.target.files.length) {
      handleFiles(e.target.files[0]);
    }
  };
  
  // Process selected file
  const handleFiles = (selectedFile) => {
    const fileExt = '.' + selectedFile.name.split('.').pop().toLowerCase();
    
    if (!acceptedFormats.includes(fileExt)) {
      showAlert(`Formato não aceito. Por favor, selecione ${acceptedFormats.join(' ou ')}.`, 'error');
      return;
    }
    
    setFile(selectedFile);
    
    if (onFileSelect) {
      onFileSelect(selectedFile);
    }
  };
  
  // Clear selected file
  const handleClearFile = () => {
    setFile(null);
    
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    
    if (onFileSelect) {
      onFileSelect(null);
    }
  };
  
  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  return (
    <Box sx={{ mb: 2 }}>
      {/* Upload area */}
      {!file ? (
        <Paper
          elevation={0}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          sx={{
            border: '2px dashed',
            borderColor: isDragging ? 'primary.main' : 'divider',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            backgroundColor: 'rgba(255, 255, 255, 0.02)',
            position: 'relative',
            overflow: 'hidden',
            '&:hover': {
              borderColor: 'primary.main',
              transform: 'translateY(-2px)',
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'linear-gradient(45deg, transparent, rgba(255, 193, 7, 0.05), transparent)',
              transform: isDragging ? 'translateX(0)' : 'translateX(-100%)',
              transition: 'transform 0.6s ease',
            },
            '&:hover::before': {
              transform: 'translateX(100%)',
            },
          }}
        >
          <CloudUploadIcon 
            sx={{ 
              fontSize: 56, 
              color: 'primary.main',
              opacity: 0.8,
              mb: 2
            }} 
          />
          <Typography variant="h6" gutterBottom>
            Arraste e solte seu arquivo aqui
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Formatos aceitos: {acceptedFormats.join(', ')}
          </Typography>
          
          <VisuallyHiddenInput
            ref={fileInputRef}
            type="file"
            accept={acceptedFormats.join(',')}
            onChange={handleFileChange}
          />
        </Paper>
      ) : (
        // File details
        <Paper
          sx={{
            p: 2,
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'divider',
            position: 'relative',
            animation: 'slideIn 0.3s ease',
            '@keyframes slideIn': {
              from: {
                opacity: 0,
                transform: 'translateY(-10px)',
              },
              to: {
                opacity: 1,
                transform: 'translateY(0)',
              },
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 3,
              background: 'linear-gradient(to right, #ffc107, #ffd54f)',
            },
          }}
        >
          <IconButton
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              color: 'text.secondary',
              transition: 'all 0.3s ease',
              '&:hover': {
                color: 'error.main',
                transform: 'rotate(90deg)',
              },
            }}
            onClick={handleClearFile}
            disabled={uploading}
          >
            <CloseIcon />
          </IconButton>
          
          <Typography variant="subtitle1" fontWeight={500} gutterBottom>
            {file.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {formatFileSize(file.size)}
          </Typography>
          
          {uploading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
};

export default FileUpload;
