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
  TIMEOUT: 30000, // 30 seconds
  CHECK_INTERVAL: 30000, // Check every 30 seconds
  RETRY_ATTEMPTS: 5, // Increased retry attempts
  RETRY_DELAY: 5000 // 5 seconds between retries
};

// Configuration object
const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 5, // Increased retry attempts
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
    HEALTH_CHECK: '/health-check',
    TEST_CONNECTION: '/test-connection'
  },

  // Fallback configuration if API is unreachable
  FALLBACK: {
    ENABLED: true,
    RETRY_INTERVAL: 5000,
    SIMULATE_SUCCESS: true
  },

  // Network error handling
  NETWORK: {
    MAX_RETRIES: 5,
    RETRY_DELAY: 5000,
    TIMEOUT: 30000,
    BACKOFF_FACTOR: 2,
    MAX_BACKOFF: 10000
  }
};

// Function to test API connection with improved error handling
export const testApiConnection = async (timeout = 5000) => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    // First try a simple fetch to check basic connectivity
    try {
      await fetch(API_CONFIG.BASE_URL, { method: 'HEAD' });
    } catch (e) {
      console.warn('Basic connectivity check failed:', e);
    }
    
    // Then try the actual health check endpoint
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.HEALTH_CHECK}`, {
      method: 'GET',
      cache: 'no-cache',
      signal: controller.signal,
      mode: 'cors',
      credentials: 'include',
      headers: API_CONFIG.HEADERS
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return {
      success: true,
      status: response.status,
      statusText: response.statusText
    };
  } catch (error) {
    console.error('API connection test failed:', error);
    
    // Handle specific error types
    if (error.name === 'AbortError') {
      return {
        success: false,
        error: 'Connection timeout - API server is not responding'
      };
    }
    
    if (error.message.includes('Failed to fetch')) {
      // Check if the server is reachable
      try {
        await fetch(API_CONFIG.BASE_URL, { method: 'HEAD' });
        return {
          success: false,
          error: 'Network error - Server is reachable but API is not responding'
        };
      } catch (e) {
        return {
          success: false,
          error: 'Network error - Server is not reachable. Please check your connection and server status.'
        };
      }
    }
    
    if (error.message.includes('CORS')) {
      return {
        success: false,
        error: 'CORS error - API server is not properly configured for cross-origin requests'
      };
    }
    
    return {
      success: false,
      error: error.message || 'Unknown error occurred while connecting to API'
    };
  }
};

// Function to check if the server is running
export const checkServerStatus = async () => {
  try {
    const response = await fetch(API_CONFIG.BASE_URL, { method: 'HEAD' });
    return {
      success: true,
      status: response.status
    };
  } catch (error) {
    return {
      success: false,
      error: 'Server is not reachable'
    };
  }
};

export default API_CONFIG; 