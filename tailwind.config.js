module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Status colors
        status: {
          success: '#4A4A4A', // Dark Gray
          failed: '#A8A8A8',  // Darker Silver
          pending: '#D3D3D3', // Light Silver
          processing: '#E8E8E8', // Light Gray
        },
        
        // Custom brand colors
        brand: {
          primary: '#4A4A4A', // Dark Gray
          secondary: '#A8A8A8', // Darker Silver
          accent: '#D3D3D3', // Light Silver
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
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}