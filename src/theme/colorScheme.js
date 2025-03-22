/**
 * Color Scheme Configuration
 * 
 * This file defines the color palette for the application.
 * These colors are designed to be accessible, attractive, and consistent.
 */

// Main Status Colors
const STATUS_COLORS = {
  // Professional gray palette
  SUCCESS: '#4A4A4A', // Dark Gray
  FAILED: '#A8A8A8',  // Darker Silver
  PENDING: '#D3D3D3', // Light Silver
  PROCESSING: '#E8E8E8', // Additional Light Gray if needed
};

// Chart and Visualization Colors
const CHART_COLORS = {
  // Primary palette (for pie charts)
  PRIMARY: [
    STATUS_COLORS.SUCCESS,
    STATUS_COLORS.FAILED,
    STATUS_COLORS.PENDING,
    STATUS_COLORS.PROCESSING,
  ],
  
  // Secondary palette with softer tones (for line/area charts)
  SECONDARY: [
    '#4A4A4A', // Dark Gray for Success
    '#A8A8A8', // Darker Silver for Failed
    '#D3D3D3', // Light Silver for Pending
    '#E8E8E8', // Light Gray
  ],
};

// UI Component Colors
const UI_COLORS = {
  // Button colors
  BUTTON: {
    PRIMARY: '#4A4A4A', // Dark Gray
    SECONDARY: '#A8A8A8', // Darker Silver
    DANGER: '#808080', // Medium Gray
    SUCCESS: '#4A4A4A', // Dark Gray
  },
  
  // Background colors
  BACKGROUND: {
    LIGHT: '#F9FAFB', // Gray 50
    CARD: '#FFFFFF',
    DARK: '#1F2937', // Gray 800
    HIGHLIGHT: '#F3F4F6', // Gray 100
  },
  
  // Text colors
  TEXT: {
    PRIMARY: '#1F2937', // Gray 800
    SECONDARY: '#4B5563', // Gray 600
    LIGHT: '#9CA3AF', // Gray 400
    INVERTED: '#F9FAFB', // Gray 50
  },
  
  // Border colors
  BORDER: {
    LIGHT: '#E5E7EB', // Gray 200
    MEDIUM: '#D1D5DB', // Gray 300
    FOCUS: '#4A4A4A', // Dark Gray
  }
};

// Export individual color schemes
export { STATUS_COLORS, CHART_COLORS, UI_COLORS };

// Export a combined theme
const THEME = {
  status: STATUS_COLORS,
  chart: CHART_COLORS,
  ui: UI_COLORS,
};

export default THEME; 