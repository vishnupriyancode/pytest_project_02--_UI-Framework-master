import axios from 'axios';
import { downloadBlob, createToast, detectBrowser, canDownloadBlob } from '../utils/downloadHelper';
import API_CONFIG, { testApiConnection } from '../config/apiConfig';

// Use the API configuration 
const API_BASE_URL = API_CONFIG.BASE_URL;

// Create axios instance with retry functionality
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.HEADERS,
  withCredentials: true
});

// Add request interceptor for retries and error handling
apiClient.interceptors.request.use(
  config => {
    // Add retry count to config if not present
    if (!config.retryCount) {
      config.retryCount = 0;
    }
    
    // Add timestamp to prevent caching
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      };
    }
    
    return config;
  },
  error => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for better error handling and retries
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const config = error.config;
    
    // If we haven't reached max retries and the error is retryable
    if (
      config.retryCount < API_CONFIG.RETRY_ATTEMPTS && 
      (error.code === 'ECONNABORTED' || 
       error.response?.status >= 500 ||
       !error.response)
    ) {
      config.retryCount += 1;
      
      // Wait before retrying (exponential backoff)
      const delay = Math.min(1000 * (Math.pow(2, config.retryCount) - 1), 10000);
      await new Promise(resolve => setTimeout(resolve, delay));
      
      console.log(`Retrying request (${config.retryCount}/${API_CONFIG.RETRY_ATTEMPTS})`);
      return apiClient(config);
    }
    
    // Log the error details
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout:', error);
      createToast('Request timed out. Please try again.', 'error');
    } else if (error.response) {
      console.error('API Error:', error.response.status, error.response.data);
      
      // Handle specific HTTP status codes
      switch (error.response.status) {
        case 401:
          createToast('Authentication required. Please log in again.', 'error');
          // Optionally redirect to login page
          break;
        case 403:
          createToast('Access denied. You do not have permission.', 'error');
          break;
        case 404:
          createToast('Resource not found.', 'error');
          break;
        case 429:
          createToast('Too many requests. Please try again later.', 'error');
          break;
        case 500:
          createToast('Server error. Please try again later.', 'error');
          break;
        default:
          createToast(error.response.data.message || 'An error occurred.', 'error');
      }
    } else if (error.request) {
      console.error('No response received:', error.request);
      createToast('No response from server. Please check your connection.', 'error');
    } else {
      console.error('Error:', error.message);
      createToast('An unexpected error occurred.', 'error');
    }
    
    return Promise.reject(error);
  }
);

// Export the configured client
export default apiClient;

// Health check function with improved error handling
export const checkApiHealth = async () => {
  try {
    // First test the connection
    const connectionTest = await testApiConnection(API_CONFIG.HEALTH_CHECK.TIMEOUT);
    if (!connectionTest.success) {
      return {
        success: false,
        error: connectionTest.error,
        isTimeout: connectionTest.error.includes('timeout')
      };
    }
    
    // If connection test passes, make the actual health check request
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.HEALTH_CHECK, {
      timeout: API_CONFIG.HEALTH_CHECK.TIMEOUT
    });
    
    return { 
      success: true, 
      data: response.data,
      status: response.status
    };
  } catch (error) {
    console.error('Health check failed:', error);
    return { 
      success: false, 
      error: error.message || 'Health check failed',
      isTimeout: error.code === 'ECONNABORTED'
    };
  }
};

// Start periodic health checks
let healthCheckInterval;

export const startHealthChecks = () => {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
  }
  
  healthCheckInterval = setInterval(async () => {
    const result = await checkApiHealth();
    if (!result.success) {
      console.warn('API health check failed:', result.error);
    }
  }, API_CONFIG.HEALTH_CHECK.CHECK_INTERVAL);
};

// Stop health checks
export const stopHealthChecks = () => {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
    healthCheckInterval = null;
  }
};

// Process all JSON files on startup
export const processAllJsons = async () => {
  try {
    const response = await apiClient.post('/process-all-jsons');
    return response.data;
  } catch (error) {
    console.error('Error processing JSON files:', error);
    throw error;
  }
};

// Get list of processed JSON files with error handling
export const getProcessedJsons = async () => {
  try {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.GET_PROCESSED);
    return response.data;
  } catch (error) {
    console.error('Error fetching Run JSONs:', error);
    throw error;
  }
};

// Download Excel report with improved error handling
export const downloadExcelReport = async (id, retryCount = 0) => {
  try {
    console.log(`Initiating Excel report download for ID: ${id} (Attempt: ${retryCount + 1})`);
    
    // Check if API URL is properly configured
    if (!API_BASE_URL || API_BASE_URL === 'http://localhost:5000') {
      console.warn('Using API URL:', API_BASE_URL);
    }
    
    // Check if API is accessible before proceeding
    const connectionTest = await testApiConnection(5000);
    if (!connectionTest.success) {
      throw new Error(`Failed to connect to API server: ${connectionTest.error || 'Unknown error'}`);
    }
    
    // Create a direct link to download the file
    const downloadUrl = `${API_BASE_URL}${API_CONFIG.ENDPOINTS.DOWNLOAD_EXCEL(id)}`;
    console.log(`Download URL: ${downloadUrl}`);
    
    // Create an anchor element and trigger the download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    return {
      success: true,
      message: `Excel report download initiated for ID: ${id}`
    };
  } catch (error) {
    console.error('Error downloading Excel report:', error);
    
    // Retry logic with exponential backoff
    if (retryCount < API_CONFIG.RETRY_ATTEMPTS - 1) {
      const delay = Math.min(1000 * (Math.pow(2, retryCount) - 1), 10000);
      console.log(`Retrying download (${retryCount + 2}/${API_CONFIG.RETRY_ATTEMPTS}) after ${delay}ms...`);
      return new Promise(resolve => {
        setTimeout(() => {
          resolve(downloadExcelReport(id, retryCount + 1));
        }, delay);
      });
    }
    
    throw error;
  }
};

// Upload multiple JSON files with improved error handling
export const uploadMultipleJsonFiles = async (formData) => {
  try {
    // First check API connection
    console.log('Checking API connectivity before upload...');
    const connectionTest = await testApiConnection(5000);
    if (!connectionTest.success) {
      throw new Error(`API server is not accessible: ${connectionTest.error}`);
    }
    
    // Log the request for debugging
    console.log('Sending bulk upload request to:', `${API_BASE_URL}${API_CONFIG.ENDPOINTS.PROCESS_MULTIPLE}`);
    
    const response = await apiClient.post(API_CONFIG.ENDPOINTS.PROCESS_MULTIPLE, formData, {
      headers: {
        'Accept': 'application/json'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error uploading files:', error);
    throw error;
  }
};

// Original API functions with improved error handling
export const uploadJsonFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(API_CONFIG.ENDPOINTS.UPLOAD_JSON, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

export const getResponseById = async (editId) => {
  try {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.GET_RESPONSE(editId));
    return response.data;
  } catch (error) {
    console.error('Error fetching response:', error);
    throw error;
  }
};

export const exportResponsesToExcel = async (filters = {}) => {
  try {
    console.log('Initiating export of all responses to Excel', filters);
    
    // Show loading indicator
    const loadingToast = document.createElement('div');
    loadingToast.className = 'fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-md shadow-lg z-50';
    loadingToast.textContent = 'Preparing Excel export...';
    document.body.appendChild(loadingToast);
    
    const response = await apiClient.get(
      '/export-responses', 
      {
        params: filters, // Pass filters to the backend
        responseType: 'blob',
        timeout: 60000, // 60 second timeout for large exports
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        },
        onDownloadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          if (progressEvent.total) {
            loadingToast.textContent = `Downloading Excel file: ${percentCompleted}%`;
          }
        }
      }
    );
    
    // Remove loading indicator
    document.body.removeChild(loadingToast);
    
    // Validate content type
    const contentType = response.headers['content-type'];
    if (!contentType || 
        (!contentType.includes('excel') && 
         !contentType.includes('spreadsheetml') && 
         !contentType.includes('octet-stream'))) {
      console.error('Unexpected content type for Excel export:', contentType);
      
      // Try to read error from response if it's text/json
      if (contentType.includes('text') || contentType.includes('json')) {
        const reader = new FileReader();
        reader.onload = function() {
          try {
            const errorData = JSON.parse(reader.result);
            throw new Error(`Server error: ${errorData.message || 'Unknown error'}`);
          } catch (e) {
            throw new Error('Invalid response from server. Expected Excel file.');
          }
        };
        reader.readAsText(response.data);
        return;
      }
      
      throw new Error(`Invalid response format. Expected Excel file but got ${contentType}`);
    }
    
    // Create download blob
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    // Add date to filename for uniqueness
    const date = new Date().toISOString().split('T')[0];
    const filename = `api_responses_${date}.xlsx`;
    
    // Check browser compatibility
    if (!canDownloadBlob()) {
      createToast('Your browser does not support automatic downloads. Please try a modern browser.', 'error', 5000);
      throw new Error('Browser does not support file downloads');
    }
    
    // Log browser information for debugging
    console.log('Attempting bulk export download in browser:', detectBrowser());
    
    try {
      await downloadBlob(blob, filename);
      createToast('Excel export completed successfully!', 'success');
      return { success: true, filename };
    } catch (downloadError) {
      console.error('Error during file download:', downloadError);
      createToast('Download failed. Please try again.', 'error');
      throw downloadError;
    }
  } catch (error) {
    console.error('Error exporting responses to Excel:', error);
    
    // Remove any existing loading toast
    const existingToast = document.querySelector('.fixed.top-4.right-4');
    if (existingToast) {
      document.body.removeChild(existingToast);
    }
    
    // Show error message
    const errorToast = document.createElement('div');
    errorToast.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-md shadow-lg z-50';
    errorToast.innerHTML = `
      <div class="font-bold">Excel Export Failed</div>
      <div class="text-sm">${error.message || 'Unknown error'}</div>
      <div class="text-xs mt-1">Please try again or contact support.</div>
    `;
    document.body.appendChild(errorToast);
    
    // Remove error message after 5 seconds
    setTimeout(() => {
      document.body.removeChild(errorToast);
    }, 5000);
    
    throw error;
  }
};

export const processEditFromLocalJson = async (filePath, editId = 'Edit 1') => {
  try {
    console.log(`Processing edit from local JSON file: ${filePath}`);
    
    // Create request payload
    const payload = {
      file_path: filePath,
      edit_id: editId
    };
    
    // Make the API request
    const response = await apiClient.post('/process-edit', payload);
    
    console.log('Edit processing response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error processing edit from local JSON:', error);
    
    // Provide more detailed error information
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      throw new Error(`Server error: ${error.response.status} - ${error.response.data.message || 'Unknown error'}`);
    } else if (error.request) {
      // The request was made but no response was received
      throw new Error('No response received from server. API server may be down.');
    } else {
      // Something happened in setting up the request that triggered an Error
      throw new Error(`Request error: ${error.message}`);
    }
  }
};