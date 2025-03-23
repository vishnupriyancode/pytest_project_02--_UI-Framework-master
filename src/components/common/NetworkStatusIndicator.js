import React, { useState, useEffect, useRef } from 'react';
import API_CONFIG, { testApiConnection, checkServerStatus } from '../../config/apiConfig';

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
  const [serverStatus, setServerStatus] = useState('unknown'); // 'online', 'offline', 'unknown'
  const [showToast, setShowToast] = useState(false);
  const timeoutRef = useRef(null);
  const intervalRef = useRef(null);
  const retryCountRef = useRef(0);
  const dismissTimerRef = useRef(null);
  
  // Safely check network status on component mount
  useEffect(() => {
    // Initial check
    checkStatus();
    
    // Set up interval to check periodically
    intervalRef.current = setInterval(() => {
      checkStatus();
    }, API_CONFIG.HEALTH_CHECK.CHECK_INTERVAL);
    
    // Cleanup function to prevent memory leaks
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (dismissTimerRef.current) clearTimeout(dismissTimerRef.current);
    };
  }, []);
  
  const checkStatus = async () => {
    try {
      setStatus('checking');
      setErrorDetails(null);
      
      // Cancel any previous timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      // First check if the server is reachable
      const serverCheck = await checkServerStatus();
      setServerStatus(serverCheck.success ? 'online' : 'offline');
      
      if (!serverCheck.success) {
        setStatus('disconnected');
        setErrorDetails('Server is not reachable');
        setShowToast(true);
        handleRetry();
        return;
      }
      
      // Then check API connectivity
      const result = await testApiConnection(API_CONFIG.HEALTH_CHECK.TIMEOUT);
      
      if (result.success) {
        setStatus('connected');
        setErrorDetails(null);
        retryCountRef.current = 0; // Reset retry count on successful connection
        setShowToast(false);
      } else {
        setStatus('disconnected');
        setErrorDetails(result.error || 'API server unreachable');
        setShowToast(true);
        handleRetry();
      }
    } catch (error) {
      console.error('Status check error:', error);
      setStatus('disconnected');
      setErrorDetails(error.message || 'Unknown error');
      setShowToast(true);
      handleRetry();
    } finally {
      setLastChecked(new Date());
      
      // Auto-dismiss toast after 5 seconds if it's not a critical error
      if (status !== 'disconnected' && showToast) {
        if (dismissTimerRef.current) clearTimeout(dismissTimerRef.current);
        dismissTimerRef.current = setTimeout(() => {
          setShowToast(false);
        }, 5000);
      }
    }
  };
  
  const handleRetry = () => {
    if (retryCountRef.current < API_CONFIG.NETWORK.MAX_RETRIES) {
      retryCountRef.current += 1;
      const delay = Math.min(
        API_CONFIG.NETWORK.RETRY_DELAY * Math.pow(API_CONFIG.NETWORK.BACKOFF_FACTOR, retryCountRef.current - 1),
        API_CONFIG.NETWORK.MAX_BACKOFF
      );
      
      console.log(`Retrying connection (${retryCountRef.current}/${API_CONFIG.NETWORK.MAX_RETRIES}) after ${delay}ms...`);
      
      timeoutRef.current = setTimeout(() => {
        checkStatus();
      }, delay);
    }
  };
  
  const handleManualRetry = () => {
    retryCountRef.current = 0;
    checkStatus();
  };
  
  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'bg-green-500';
      case 'disconnected':
        return serverStatus === 'online' ? 'bg-yellow-500' : 'bg-red-500';
      case 'checking':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };
  
  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'API Connected';
      case 'disconnected':
        if (serverStatus === 'offline') {
          return 'Server Offline';
        }
        return errorDetails ? `API Disconnected: ${errorDetails}` : 'API Disconnected';
      case 'checking':
        return `Checking Status... (Attempt ${retryCountRef.current + 1}/${API_CONFIG.NETWORK.MAX_RETRIES})`;
      default:
        return 'Status Unknown';
    }
  };
  
  const getFormattedTime = () => {
    if (!lastChecked) return '';
    return lastChecked.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  if (!showToast) return null;
  
  return (
    <div className="fixed top-4 right-4 z-50 animate-fade-in">
      <div className={`
        flex items-center gap-2 px-3 py-2 rounded-lg shadow-lg
        ${status === 'disconnected' ? 'bg-red-50' : 'bg-gray-50'}
        border-l-4 ${status === 'disconnected' ? 'border-red-500' : 'border-gray-500'}
        max-w-sm w-full
      `}>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <div className={`w-1.5 h-1.5 rounded-full ${
              status === 'checking' ? 'bg-blue-500 animate-pulse' :
              status === 'connected' ? 'bg-green-500' :
              'bg-red-500'
            }`} />
            <h3 className={`font-medium text-sm truncate ${
              status === 'disconnected' ? 'text-red-800' : 'text-gray-800'
            }`}>
              {status === 'checking' ? 'Checking API Connection...' :
               status === 'connected' ? 'API Connected' :
               'API Connection Lost'}
            </h3>
          </div>
          {errorDetails && (
            <p className="mt-0.5 text-xs text-gray-600 truncate">
              {errorDetails}
            </p>
          )}
          <p className="mt-0.5 text-xs text-gray-500">
            Last checked: {getFormattedTime()}
          </p>
        </div>
        
        <div className="flex items-center gap-1.5 flex-shrink-0">
          {status === 'disconnected' && (
            <button
              onClick={handleManualRetry}
              className="px-2 py-1 text-xs font-medium text-red-700 bg-red-100 
                       rounded hover:bg-red-200 focus:outline-none focus:ring-2 
                       focus:ring-red-500 focus:ring-offset-1"
            >
              Retry
            </button>
          )}
          <button
            onClick={() => setShowToast(false)}
            className="text-gray-400 hover:text-gray-600 p-0.5"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default NetworkStatusIndicator;