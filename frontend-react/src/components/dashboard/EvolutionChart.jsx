import React from 'react';
import { Line } from 'react-chartjs-2';
import { Box, Typography, useTheme } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

/**
 * Portfolio evolution chart component (line chart)
 */
const EvolutionChart = ({ evolution = [], isMobile }) => { // Added isMobile prop
  const theme = useTheme();
  
  if (!evolution || evolution.length === 0) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height="100%" 
        minHeight="250px"
      >
        <Typography color="text.secondary">
          Sem dados de evolução disponíveis
        </Typography>
      </Box>
    );
  }

  // Sort evolution data by date
  const sortedData = [...evolution].sort((a, b) => {
    return new Date(a.date).getTime() - new Date(b.date).getTime();
  });
  
  const labels = sortedData.map(item => {
    const date = new Date(item.date);
    return date.toLocaleDateString('pt-BR');
  });
  
  const values = sortedData.map(item => item.value);
  
  const formatter = new Intl.NumberFormat('pt-BR', {
    style: 'currency', 
    currency: 'BRL',
    minimumFractionDigits: 0
  });
  
  const chartData = {
    labels,
    datasets: [
      {
        label: 'Valor do Portfólio',
        data: values,
        borderColor: theme.palette.primary.main,
        backgroundColor: `rgba(${hexToRgb(theme.palette.primary.main)}, 0.1)`,
        borderWidth: 2,
        tension: 0.2,
        fill: true,
        pointRadius: isMobile ? 0 : 3, // Conditionally set pointRadius
        pointBackgroundColor: theme.palette.primary.main,
        pointBorderColor: theme.palette.background.paper,
        pointHoverRadius: isMobile ? 0 : 5, // Conditionally set pointHoverRadius
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: theme.palette.primary.main,
        pointHoverBorderWidth: 2
      }
    ]
  };
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: false,
        display: !isMobile, // Conditionally display Y-axis
        grid: {
          color: theme.palette.mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.1)' 
            : 'rgba(0, 0, 0, 0.1)',
          drawBorder: false
        },
        ticks: {
          color: theme.palette.text.secondary,
          callback: (value) => formatter.format(value)
        }
      },
      x: {
        grid: {
          display: false,
          drawBorder: false
        },
        ticks: {
          color: theme.palette.text.secondary,
          maxRotation: 45,
          minRotation: 45,
          autoSkip: true,
          maxTicksLimit: isMobile ? 4 : 12 // Conditionally set maxTicksLimit
        }
      }
    },
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        padding: 12,
        cornerRadius: 5,
        displayColors: false,
        callbacks: {
          title: (tooltipItems) => {
            return tooltipItems[0].label;
          },
          label: (context) => {
            const label = context.dataset.label || '';
            const value = context.raw || 0;
            return `${label}: ${formatter.format(value)}`;
          }
        }
      }
    }
  };
  
  return (
    <Box height="350px" position="relative">
      <Line data={chartData} options={options} />
    </Box>
  );
};

// Utility function to convert hex to RGB
const hexToRgb = (hex) => {
  // Remove # if present
  hex = hex.replace('#', '');
  
  // Parse hex
  const bigint = parseInt(hex, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  
  return `${r}, ${g}, ${b}`;
};

export default EvolutionChart;
