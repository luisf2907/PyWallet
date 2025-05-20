import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Box, Typography, useTheme } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Monthly dividends chart component (bar chart)
 */
const DividendsChart = ({ data = [], year, currentYear, currentMonth, onMonthSelect }) => {
  const theme = useTheme();
  
  if (!data || data.length === 0) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height="100%" 
        minHeight="250px"
      >
        <Typography color="text.secondary">
          Sem dados de proventos disponíveis para {year || 'este ano'}
        </Typography>
      </Box>
    );
  }

  // Month labels
  const monthLabels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

  // Determine which months should be visually disabled (future months for current year)
  const barColors = data.map((val, idx) => {
    if (parseInt(year) === currentYear && idx + 1 > currentMonth) {
      return theme.palette.mode === 'dark'
        ? 'rgba(120,120,120,0.18)'
        : 'rgba(200,200,200,0.18)'; // faded/disabled
    }
    return 'rgba(255, 193, 7, 0.6)';
  });
  const hoverColors = data.map((val, idx) => {
    if (parseInt(year) === currentYear && idx + 1 > currentMonth) {
      return theme.palette.mode === 'dark'
        ? 'rgba(120,120,120,0.25)'
        : 'rgba(200,200,200,0.25)';
    }
    return 'rgba(255, 193, 7, 0.8)';
  });

  // Format currency values
  const formatter = new Intl.NumberFormat('pt-BR', {
    style: 'currency', 
    currency: 'BRL',
    minimumFractionDigits: 2
  });
  
  const chartData = {
    labels: monthLabels,
    datasets: [
      {
        label: 'Proventos (R$)',
        data: data,
        backgroundColor: barColors,
        borderColor: '#ffc107',
        borderWidth: 1,
        borderRadius: 4,
        hoverBackgroundColor: hoverColors,
      }
    ]
  };
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    onClick: (event, elements) => {
      if (elements.length > 0 && onMonthSelect) {
        const index = elements[0].index;
        onMonthSelect(index + 1); // Month is 1-indexed
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: theme.palette.mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.1)' 
            : 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          color: theme.palette.text.secondary,
          callback: (value) => formatter.format(value)
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: theme.palette.text.secondary
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        callbacks: {
          title: (tooltipItems) => {
            const monthIndex = tooltipItems[0].dataIndex;
            return `${monthLabels[monthIndex]} ${year || ''}`;
          },
          label: (context) => {
            const value = context.raw || 0;
            return formatter.format(value);
          }
        }
      }
    }
  };
  
  return (
    <Box height="350px" position="relative">
      <Bar data={chartData} options={options} />
    </Box>
  );
};

export default DividendsChart;
