/**
 * API Configuration
 * 
 * This file contains configuration for API endpoints.
 * Update these values based on your environment (development, staging, production)
 */

// Detect environment and set base URL accordingly
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  
  // Production environment
  if (hostname === 'your-production-domain.com') {
    return 'https://api.your-production-domain.com';
  }
  
  // Development environment - use port 5000 for API server
  return 'http://localhost:5000';
};

// API health check configuration
const HEALTH_CHECK_CONFIG = {
  ENDPOINT: '/health-check',
  TIMEOUT: 30000, // Increased timeout to 30 seconds
  CHECK_INTERVAL: 30000, // Check every 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 5000 // 5 seconds between retries
};

// Configuration object
const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  HEALTH_CHECK: HEALTH_CHECK_CONFIG,
  
  // Request headers
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  
  // CORS configuration
  CORS: {
    credentials: 'include',
    mode: 'cors',
    cache: 'default'
  },
  
  // Endpoints
  ENDPOINTS: {
    PROCESS_ALL: '/process-all-jsons',
    GET_PROCESSED: '/processed-jsons',
    DOWNLOAD_EXCEL: (id) => `/download-excel/${id}`,
    UPLOAD_JSON: '/upload-json',
    PROCESS_MULTIPLE: '/process-multiple-jsons',
    GET_RESPONSE: (id) => `/get-response/${id}`,
    EXPORT_RESPONSES: '/export-responses',
  },

  // Fallback configuration if API is unreachable
  FALLBACK: {
    ENABLED: true, // Enable fallback mode when API is unreachable
    RETRY_INTERVAL: 5000, // Time between retries in fallback mode
    SIMULATE_SUCCESS: true // For development: simulate successful operations
  }
};

// Function to test API connection (can be used outside NetworkStatusIndicator)
export const testApiConnection = async (timeout = 5000) => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${HEALTH_CHECK_CONFIG.ENDPOINT}`, {
      method: 'GET',
      cache: 'no-cache',
      signal: controller.signal,
      mode: 'cors',
      credentials: 'same-origin', // Changed from 'include' to avoid CORS issues
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });
    
    clearTimeout(timeoutId);
    
    return {
      success: response.ok,
      status: response.status,
      statusText: response.statusText
    };
  } catch (error) {
    console.error('API connection test failed:', error);
    return {
      success: false,
      error: error.name === 'AbortError' ? 'Timeout' : error.message
    };
  }
};

// Export the config object only
export default API_CONFIG; 