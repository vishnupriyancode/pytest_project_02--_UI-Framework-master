import axios from 'axios';
import { downloadBlob, createToast, detectBrowser, canDownloadBlob } from '../utils/downloadHelper';
import API_CONFIG, { testApiConnection } from '../config/apiConfig';

// Use the API configuration 
const API_BASE_URL = API_CONFIG.BASE_URL;

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.HEADERS,
  // Add CORS settings
  withCredentials: API_CONFIG.CORS.credentials === 'include',
});

// Add response interceptor for better error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout:', error);
    } else if (error.response) {
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

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

// Get list of processed JSON files
export const getProcessedJsons = async () => {
  try {
    const response = await apiClient.get('/processed-jsons');
    return response.data;
  } catch (error) {
    console.error('Error fetching Run JSONs:', error);
    throw error;
  }
};

// Download Excel report for specific processed JSON
export const downloadExcelReport = async (id, retryCount = 0) => {
  try {
    console.log(`Initiating Excel report download for ID: ${id} (Attempt: ${retryCount + 1})`);
    
    // Check if API URL is properly configured
    if (!API_BASE_URL || API_BASE_URL === 'http://localhost:5000') {
      console.warn('Using API URL:', API_BASE_URL);
    }
    
    // Dynamically import the testApiConnection function
    const apiConfigModule = await import('../config/apiConfig');
    const testApiConnection = apiConfigModule.testApiConnection;
    
    // Check if API is accessible before proceeding
    const connectionTest = await testApiConnection(5000);
    if (!connectionTest.success) {
      console.error('API server is not reachable:', connectionTest.error);
      throw new Error(`Failed to connect to API server: ${connectionTest.error || 'Unknown error'}`);
    }
    
    // Create a direct link to download the file
    const downloadUrl = `${API_BASE_URL}/download-excel/${id}`;
    console.log(`Download URL: ${downloadUrl}`);
    
    // Create an anchor element and trigger the download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.target = '_blank'; // Open in new tab
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
    
    // Retry logic
    if (retryCount < API_CONFIG.RETRY_ATTEMPTS - 1) {
      console.log(`Retrying download (${retryCount + 2}/${API_CONFIG.RETRY_ATTEMPTS})...`);
      return new Promise(resolve => {
        setTimeout(() => {
          resolve(downloadExcelReport(id, retryCount + 1));
        }, 2000); // Wait 2 seconds before retrying
      });
    }
    
    throw error;
  }
};

// Upload multiple JSON files for bulk processing
export const uploadMultipleJsonFiles = async (formData) => {
  try {
    // First check API connection to ensure server is running
    console.log('Checking API connectivity before upload...');
    try {
      const checkResponse = await fetch(`${API_BASE_URL}/health-check`, { 
        method: 'GET',
        mode: 'cors',
        credentials: 'include',
        headers: API_CONFIG.HEADERS
      });
      
      if (!checkResponse.ok) {
        throw new Error(`API server returned ${checkResponse.status}: ${checkResponse.statusText}`);
      }
    } catch (connError) {
      console.error('API connectivity check failed:', connError);
      throw new Error(`API server is not accessible: ${connError.message}`);
    }
    
    // Log the request for debugging
    console.log('Sending bulk upload request to:', `${API_BASE_URL}/process-multiple-jsons`);
    
    // Try direct fetch API with proper CORS settings
    const response = await fetch(`${API_BASE_URL}/process-multiple-jsons`, {
      method: 'POST',
      body: formData,
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Accept': 'application/json'
        // Don't set Content-Type for multipart/form-data, browser will add it with boundary
      }
    });
    
    // Check response status
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Server returned ${response.status}: ${response.statusText}`);
      console.error('Error response:', errorText);
      throw new Error(`Server error: ${response.status} ${response.statusText}`);
    }
    
    // Parse response data
    const responseData = await response.json();
    console.log('Upload response:', responseData);
    return responseData;
  } catch (error) {
    console.error('Error processing multiple files:', error);
    
    // Enhance error details for debugging
    let errorMessage = 'Network error during file upload';
    if (error.name === 'AbortError') {
      errorMessage = 'Request timed out';
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    const enhancedError = new Error(errorMessage);
    enhancedError.originalError = error;
    throw enhancedError;
  }
};

// Original API functions for file upload, etc.
export const uploadJsonFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/upload-json', formData, {
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
    const response = await apiClient.get(`/get-response/${editId}`);
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