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
  const timeoutRef = useRef(null);
  const intervalRef = useRef(null);
  const retryCountRef = useRef(0);
  
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
        setErrorDetails('Server is not reachable. Please check if the server is running.');
        handleRetry();
        return;
      }
      
      // Then check API connectivity
      const result = await testApiConnection(API_CONFIG.HEALTH_CHECK.TIMEOUT);
      
      if (result.success) {
        setStatus('connected');
        setErrorDetails(null);
        retryCountRef.current = 0; // Reset retry count on successful connection
      } else {
        setStatus('disconnected');
        setErrorDetails(result.error || 'API server unreachable');
        handleRetry();
      }
    } catch (error) {
      console.error('Status check error:', error);
      setStatus('disconnected');
      setErrorDetails(error.message || 'Unknown error');
      handleRetry();
    } finally {
      setLastChecked(new Date());
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
  
  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg shadow-lg ${getStatusColor()} text-white`}>
        <div className="w-2 h-2 rounded-full bg-white animate-pulse"></div>
        <span className="text-sm font-medium">{getStatusText()}</span>
        <span className="text-xs opacity-75">Last checked: {getFormattedTime()}</span>
      </div>
    </div>
  );
};

export default NetworkStatusIndicator;