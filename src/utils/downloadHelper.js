/**
 * A utility to reliably download files across different browsers
 */

/**
 * Download a blob as a file in the browser
 * @param {Blob} blob - The blob to download
 * @param {string} filename - The filename to use
 * @returns {Promise<boolean>} - Promise that resolves when download is initiated
 */
export const downloadBlob = (blob, filename) => {
  return new Promise((resolve, reject) => {
    try {
      // Method 1: Using createObjectURL and a link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      link.style.display = 'none';
      document.body.appendChild(link);
      
      // For Safari, we need to use a timeout
      setTimeout(() => {
        link.click();
        
        // For Firefox, we need to wait before revoking
        setTimeout(() => {
          window.URL.revokeObjectURL(url);
          document.body.removeChild(link);
          resolve(true);
        }, 100);
      }, 10);
    } catch (err) {
      console.error('Error in primary download method:', err);
      
      try {
        // Method 2: Fallback for older browsers
        const reader = new FileReader();
        reader.onload = function() {
          const dataUrl = reader.result;
          const link = document.createElement('a');
          link.href = dataUrl;
          link.download = filename;
          link.click();
          resolve(true);
        };
        reader.onerror = function(error) {
          console.error('FileReader error:', error);
          reject(new Error('Failed to read file data'));
        };
        reader.readAsDataURL(blob);
      } catch (fallbackErr) {
        console.error('Error in fallback download method:', fallbackErr);
        reject(fallbackErr);
      }
    }
  });
};

/**
 * Check if the browser supports downloading blobs
 * @returns {boolean} - Whether the browser supports downloads
 */
export const canDownloadBlob = () => {
  try {
    // Check for necessary browser features
    return (
      !!window.Blob &&
      !!window.URL &&
      !!window.URL.createObjectURL
    );
  } catch (e) {
    return false;
  }
};

/**
 * Detect browser type
 * @returns {string} - Browser name
 */
export const detectBrowser = () => {
  const userAgent = navigator.userAgent;
  
  if (userAgent.indexOf("Chrome") > -1) return "Chrome";
  if (userAgent.indexOf("Safari") > -1) return "Safari";
  if (userAgent.indexOf("Firefox") > -1) return "Firefox";
  if (userAgent.indexOf("MSIE") > -1 || userAgent.indexOf("Trident") > -1) return "IE";
  if (userAgent.indexOf("Edge") > -1) return "Edge";
  
  return "Unknown";
};

/**
 * Create a toast notification
 * @param {string} message - Message to display
 * @param {'success'|'error'|'info'} type - Type of toast
 * @param {number} duration - Duration in ms
 */
export const createToast = (message, type = 'info', duration = 3000) => {
  const toast = document.createElement('div');
  
  // Add styles based on type
  const bgColor = type === 'success' ? 'bg-green-500' : 
                  type === 'error' ? 'bg-red-500' : 'bg-blue-500';
  
  toast.className = `fixed right-4 z-50 px-4 py-2 rounded-md shadow-lg text-white ${bgColor}`;
  
  // Position based on existing toasts
  const existingToasts = document.querySelectorAll(`.${bgColor}`);
  if (type === 'error' || type === 'info') {
    toast.classList.add('top-4');
    if (existingToasts.length > 0) {
      toast.style.top = `${(existingToasts.length * 4) + 4}rem`;
    }
  } else {
    toast.classList.add('bottom-4');
    if (existingToasts.length > 0) {
      toast.style.bottom = `${(existingToasts.length * 4) + 4}rem`;
    }
  }
  
  toast.textContent = message;
  document.body.appendChild(toast);
  
  // Remove after duration
  setTimeout(() => {
    toast.classList.add('opacity-0', 'transition-opacity', 'duration-300');
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, duration);
  
  return toast;
}; 