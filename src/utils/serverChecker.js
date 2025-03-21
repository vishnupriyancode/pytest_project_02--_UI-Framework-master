/**
 * Server Checker Utility
 * 
 * This utility provides functions to check if the API server is running
 * and properly configured for CORS, file downloads, etc.
 */

import API_CONFIG, { testApiConnection } from '../config/apiConfig';

/**
 * Checks if the server is running and accessible
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export const isServerRunning = async () => {
  return testApiConnection(5000);
};

/**
 * Checks if CORS is properly configured on the server
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export const checkServerCors = async () => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    // Check CORS specifically with an OPTIONS request
    const response = await fetch(`${API_CONFIG.BASE_URL}/health-check`, {
      method: 'OPTIONS',
      signal: controller.signal,
      mode: 'cors',
      headers: {
        'Access-Control-Request-Method': 'GET',
        'Origin': window.location.origin
      }
    });
    
    clearTimeout(timeoutId);
    
    // Check for CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
      'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
      'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
    };
    
    const corsConfigured = corsHeaders['Access-Control-Allow-Origin'] !== null;
    
    return {
      success: response.ok && corsConfigured,
      corsHeaders,
      statusCode: response.status
    };
  } catch (error) {
    console.error('CORS check failed:', error);
    return {
      success: false,
      error: error.name === 'AbortError' ? 'Connection timeout' : error.message
    };
  }
};

/**
 * Tests if the server can handle file downloads properly
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export const testFileDownload = async () => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    // Attempt to download a test file
    const response = await fetch(`${API_CONFIG.BASE_URL}/test-download`, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Accept': 'application/octet-stream'
      }
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      return {
        success: false,
        error: `Server returned ${response.status}: ${response.statusText}`
      };
    }
    
    // Check content-type header
    const contentType = response.headers.get('content-type');
    const contentDisposition = response.headers.get('content-disposition');
    
    return {
      success: true,
      contentType,
      contentDisposition,
      hasProperHeaders: !!contentDisposition && !!contentType
    };
  } catch (error) {
    console.error('File download test failed:', error);
    return {
      success: false,
      error: error.name === 'AbortError' ? 'Connection timeout' : error.message
    };
  }
};

/**
 * Run all server checks and return a comprehensive report
 * @returns {Promise<Object>} Server check results
 */
export const runServerDiagnostics = async () => {
  const results = {
    timestamp: new Date().toISOString(),
    serverUrl: API_CONFIG.BASE_URL,
    browser: navigator.userAgent,
    checks: {}
  };
  
  // Check server reachability
  results.checks.serverRunning = await isServerRunning();
  
  // If server is running, check CORS configuration
  if (results.checks.serverRunning.success) {
    results.checks.corsConfiguration = await checkServerCors();
    results.checks.fileDownload = await testFileDownload();
  }
  
  // Overall status
  results.success = results.checks.serverRunning.success &&
                   (results.checks.corsConfiguration?.success || false);
  
  return results;
};

export default {
  isServerRunning,
  checkServerCors,
  testFileDownload,
  runServerDiagnostics
}; 