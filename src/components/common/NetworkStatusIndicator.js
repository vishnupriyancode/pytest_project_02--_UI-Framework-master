import React, { useState, useEffect, useRef } from 'react';
import API_CONFIG from '../../config/apiConfig';

/**
 * Network Status Indicator
 * 
 * A component that shows the current status of the API connection
 * and allows users to manually check connectivity
 */
const NetworkStatusIndicator = () => {
  const [status, setStatus] = useState('unknown'); // 'connected', 'disconnected', 'checking', 'unknown'
  const [lastChecked, setLastChecked] = useState(null);
  const [errorDetails, setErrorDetails] = useState(null);
  const timeoutRef = useRef(null);
  const intervalRef = useRef(null);
  
  // Safely check network status on component mount
  useEffect(() => {
    // Initial check
    checkApiConnection();
    
    // Set up interval to check periodically
    intervalRef.current = setInterval(() => {
      checkApiConnection();
    }, API_CONFIG.HEALTH_CHECK.CHECK_INTERVAL);
    
    // Cleanup function to prevent memory leaks
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);
  
  const checkApiConnection = async () => {
    try {
      setStatus('checking');
      setErrorDetails(null);
      
      // Cancel any previous timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      // Import testApiConnection function dynamically to avoid circular dependencies
      const apiConfigModule = await import('../../config/apiConfig');
      const testConnection = apiConfigModule.testApiConnection;
      
      // Use the imported test function
      const result = await testConnection(API_CONFIG.HEALTH_CHECK.TIMEOUT);
      
      if (result.success) {
        setStatus('connected');
        setErrorDetails(null);
      } else {
        setStatus('disconnected');
        setErrorDetails(result.error || 'API server unreachable');
      }
    } catch (error) {
      console.error('API connection check error:', error);
      setStatus('disconnected');
      setErrorDetails(error.message || 'Unknown error');
    } finally {
      setLastChecked(new Date());
    }
  };
  
  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'bg-green-500';
      case 'disconnected':
        return 'bg-red-500';
      case 'checking':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };
  
  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'API Connected';
      case 'disconnected':
        return errorDetails ? `API Disconnected: ${errorDetails}` : 'API Disconnected';
      case 'checking':
        return 'Checking API...';
      default:
        return 'API Status Unknown';
    }
  };
  
  const getFormattedTime = () => {
    if (!lastChecked) return '';
    
    return lastChecked.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  return (
    <div className="fixed bottom-4 left-4 z-50">
      <div className="flex items-center space-x-2 bg-white p-2 rounded-md shadow-md">
        <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
        <span className="text-xs text-gray-600 max-w-[200px] truncate" title={getStatusText()}>
          {getStatusText()}
        </span>
        {lastChecked && (
          <span className="text-xs text-gray-400">
            Last checked: {getFormattedTime()}
          </span>
        )}
        <button 
          onClick={() => checkApiConnection()}
          className="text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
          disabled={status === 'checking'}
        >
          {status === 'checking' ? 'Checking...' : 'Check'}
        </button>
      </div>
    </div>
  );
};

export default NetworkStatusIndicator;