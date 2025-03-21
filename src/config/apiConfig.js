/**
 * API Configuration
 * 
 * This file contains configuration for API endpoints.
 * Update these values based on your environment (development, staging, production)
 */

// Detect environment and set base URL accordingly
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  const port = window.location.port;
  
  // Production environment
  if (hostname === 'your-production-domain.com') {
    return 'https://api.your-production-domain.com';
  }
  
  // Staging environment
  if (hostname === 'staging.your-domain.com') {
    return 'https://api-staging.your-domain.com';
  }
  
  // Development environments - important: use the correct port from the error logs
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // For local development, API server should always be on localhost:5000
    return 'http://localhost:5000';
  }
  
  // Default fallback (development)
  return 'http://localhost:5000';
};

// API health check configuration
const HEALTH_CHECK_CONFIG = {
  // Endpoint for checking API health
  ENDPOINT: '/health-check',
  // Timeout for health check (milliseconds)
  TIMEOUT: 5000,
  // Interval for automatic health checks (milliseconds)
  CHECK_INTERVAL: 60000, // 1 minute
  // Number of retry attempts for health check
  RETRY_ATTEMPTS: 2
};

// Configuration object
const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  TIMEOUT: 30000, // Default timeout for requests (30 seconds)
  RETRY_ATTEMPTS: 3, // Number of retry attempts for failed requests
  HEALTH_CHECK: HEALTH_CHECK_CONFIG,
  
  // Request headers
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    // Add these headers to help with CORS issues
    'X-Requested-With': 'XMLHttpRequest',
    'Cache-Control': 'no-cache'
  },
  
  // CORS configuration - updated with more flexible settings
  CORS: {
    credentials: 'same-origin', // Changed from 'include' to avoid CORS issues
    mode: 'cors',
    cache: 'no-cache',
    redirect: 'follow'
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