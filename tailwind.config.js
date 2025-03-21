module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Status colors
        status: {
          success: '#06B6D4', // Teal 500
          failed: '#F43F5E',  // Rose 500
          pending: '#FBBF24', // Amber 400
          processing: '#8B5CF6', // Violet 500
        },
        
        // Custom brand colors
        brand: {
          primary: '#0891B2', // Teal 600
          secondary: '#6B7280', // Gray 500
          accent: '#0EA5E9', // Sky 500
        },
        
        // Semantic UI colors
        ui: {
          background: '#F9FAFB', // Gray 50
          card: '#FFFFFF',
          border: '#E5E7EB', // Gray 200
          hover: '#F3F4F6', // Gray 100
        },
      },
      boxShadow: {
        'card': '0 2px 4px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1)',
        'popup': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
      borderRadius: {
        'card': '0.5rem',
        'button': '0.375rem',
      },
    },
  },
  plugins: [],
}