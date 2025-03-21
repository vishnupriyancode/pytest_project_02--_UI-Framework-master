/**
 * Color Scheme Configuration
 * 
 * This file defines the color palette for the application.
 * These colors are designed to be accessible, attractive, and consistent.
 */

// Main Status Colors
const STATUS_COLORS = {
  // Professional indigo/teal palette for a modern look
  SUCCESS: '#06B6D4', // Vibrant teal
  FAILED: '#F43F5E',  // Soft rose
  PENDING: '#FBBF24', // Warm amber
  PROCESSING: '#8B5CF6', // Rich purple
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
    '#0EA5E9', // Sky blue
    '#F97316', // Orange
    '#10B981', // Emerald
    '#8B5CF6', // Violet
  ],
  
  // Gradient backgrounds for cards and containers
  GRADIENTS: {
    SUCCESS: 'linear-gradient(135deg, #06B6D4 0%, #0891B2 100%)',
    FAILED: 'linear-gradient(135deg, #F43F5E 0%, #E11D48 100%)',
    INFO: 'linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)',
  },
};

// UI Component Colors
const UI_COLORS = {
  // Button colors
  BUTTON: {
    PRIMARY: '#0891B2', // Teal 600
    SECONDARY: '#6B7280', // Gray 500
    DANGER: '#E11D48', // Rose 600
    SUCCESS: '#059669', // Emerald 600
  },
  
  // Background colors
  BACKGROUND: {
    LIGHT: '#F9FAFB', // Gray 50
    CARD: '#FFFFFF',
    DARK: '#1F2937', // Gray 800
    HIGHLIGHT: '#F0F9FF', // Sky 50
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
    FOCUS: '#0EA5E9', // Sky 500
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