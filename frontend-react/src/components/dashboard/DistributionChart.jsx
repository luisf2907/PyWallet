import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Box, Typography, useTheme } from '@mui/material';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale
} from 'chart.js';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale);

/**
 * Asset distribution chart component (doughnut/pie chart)
 */
const DistributionChart = ({ distribution = [] }) => {
  const theme = useTheme();
  
  if (!distribution || distribution.length === 0) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height="100%" 
        minHeight="250px"
      >
        <Typography color="text.secondary">
          Sem dados de distribuição disponíveis
        </Typography>
      </Box>
    );
  }  // Sort assets by percentage (descending) and use all assets
  const sortedAssets = [...distribution].sort((a, b) => b.percentage - a.percentage);
  
  // Include all assets in the chart
  const labels = sortedAssets.map(asset => {
    const type = asset.is_us_ticker ? "(US)" : (asset.is_bdr ? "(BDR)" : "");
    return `${asset.ticker} ${type}`;
  });  const data = sortedAssets.map(asset => asset.percentage);  // Generate a balanced red-orange-yellow gradient for better visual distribution
  const generateColors = (count) => {
    // Use a balanced palette with more oranges to create smoother transition 
    const colorPalette = [
      '#a50000', // Deep Red (highest values) - menos intenso que o anterior
      '#b30000', // Dark Red
      '#c10000', // Medium Red
      '#d00000', // Light Red
      '#e00000', // Bright Red
      '#ef2200', // Red-Orange
      '#f63a00', // Dark Orange-Red
      '#fa5000', // Reddish Orange
      '#fd6500', // Dark Orange
      '#ff7800', // Medium-Dark Orange
      '#ff8a00', // Medium Orange
      '#ff9c00', // Medium-Light Orange
      '#ffad00', // Light Orange
      '#ffbc00', // Amber Orange
      '#ffca00', // Dark Yellow-Orange
      '#ffd700', // Amber-Yellow
      '#ffe200', // Golden Yellow
      '#ffec00', // Bright Yellow
      '#fff500', // Lemon Yellow
      '#ffff00'  // Pure Yellow (lowest values)
    ];
    
    const colors = [];
    for (let i = 0; i < count; i++) {
      // For the first 20 assets, use distinct colors from the palette
      if (i < colorPalette.length) {
        colors.push(colorPalette[i]);
      } else {
        // For additional assets, create variations using interpolation between existing colors
        const baseIndex = i % colorPalette.length;
        const nextIndex = (baseIndex + 1) % colorPalette.length;
        const variation = (i / count) % 1;
        colors.push(interpolateColor(colorPalette[baseIndex], colorPalette[nextIndex], variation));
      }
    }
    return colors;
  };

  const chartData = {
    labels,
    datasets: [
      {
        data,
        backgroundColor: generateColors(labels.length),
        borderColor: theme.palette.background.paper,
        borderWidth: 1,
        hoverBorderColor: theme.palette.primary.main,
        hoverBorderWidth: 2,
      },
    ],
  };  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '50%',
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: theme.palette.text.primary,
          padding: 8,
          usePointStyle: true,
          boxWidth: 8,
          font: {
            size: 9,
            weight: '400' // Lighter weight
          },          generateLabels: (chart) => {
            const data = chart.data;
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label, i) => {
                const value = data.datasets[0].data[i];
                const backgroundColor = data.datasets[0].backgroundColor[i];
                // Format label more concisely for better display when showing all assets
                return {
                  text: `${label}: ${value.toFixed(1)}%`,
                  fillStyle: backgroundColor,
                  hidden: false,
                  index: i,
                  fontColor: theme.palette.text.primary
                };
              });
            }
            return [];
          }
        },
        display: true,
        align: 'center'
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.raw || 0;
            return `${label}: ${value.toFixed(2)}%`;
          }
        }
      }
    }
  };
  return (
    <Box height="380px" position="relative" sx={{ overflowY: "auto" }}>
      <Doughnut data={chartData} options={options} />
    </Box>
  );
};

// Utility function to interpolate between two colors with high saturation
const interpolateColor = (color1, color2, factor) => {
  const c1 = parseColor(color1);
  const c2 = parseColor(color2);
  
  const r = Math.round(c1.r + factor * (c2.r - c1.r));
  const g = Math.round(c1.g + factor * (c2.g - c1.g));
  const b = Math.round(c1.b + factor * (c2.b - c1.b));
  
  return `rgba(${r}, ${g}, ${b}, 0.8)`; // Balanced opacity for professional look
};

// Parse hex color to {r, g, b}
const parseColor = (color) => {
  // Handle hex colors
  if (color.startsWith('#')) {
    const hex = color.slice(1);
    return {
      r: parseInt(hex.substring(0, 2), 16),
      g: parseInt(hex.substring(2, 4), 16),
      b: parseInt(hex.substring(4, 6), 16)
    };
  }
  // Handle rgb/rgba colors
  const match = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (match) {
    return {
      r: parseInt(match[1]),
      g: parseInt(match[2]),
      b: parseInt(match[3])
    };
  }
  return { r: 0, g: 0, b: 0 }; // Default
};

export default DistributionChart;
