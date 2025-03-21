import React, { useState, useRef } from 'react';
import { processEditFromLocalJson } from '../services/apiService';

const LocalJsonEdit = () => {
  // State for basic form
  const [filePath, setFilePath] = useState('');
  const [editId, setEditId] = useState('Edit 1');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  // State for advanced Postman-like panel
  const [showAdvancedPanel, setShowAdvancedPanel] = useState(false);
  const [requestMethod, setRequestMethod] = useState('POST');
  const [requestUrl, setRequestUrl] = useState('http://localhost:5000/process-edit');
  const [requestBody, setRequestBody] = useState(JSON.stringify({
    file_path: "C:\\path\\to\\your\\sample.json",
    edit_id: "Edit 1"
  }, null, 2));
  const [requestHeaders, setRequestHeaders] = useState([
    { key: 'Content-Type', value: 'application/json', enabled: true }
  ]);
  const [response, setResponse] = useState(null);
  const [responseStatus, setResponseStatus] = useState(null);
  const [responseTime, setResponseTime] = useState(null);
  
  // State for multiple file paths
  const [filePaths, setFilePaths] = useState(['']);
  
  // Refs for tabs
  const bodyTabRef = useRef(null);
  const headersTabRef = useRef(null);
  const responseTabRef = useRef(null);
  
  // Track active tab
  const [activeTab, setActiveTab] = useState('body');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      // Validate input
      if (!filePath) {
        throw new Error('File path is required');
      }

      // Process the edit
      const response = await processEditFromLocalJson(filePath, editId);
      setResult(response);
    } catch (err) {
      console.error('Error processing edit:', err);
      setError(err.message || 'An error occurred while processing the edit');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle sending request from advanced panel
  const handleSendRequest = async () => {
    setLoading(true);
    setResponse(null);
    setResponseStatus(null);
    setResponseTime(null);
    
    const startTime = new Date();
    
    try {
      let requestBodyData;
      
      try {
        requestBodyData = JSON.parse(requestBody);
      } catch (err) {
        throw new Error('Invalid JSON in request body');
      }
      
      // If multiple file paths are specified in the UI, update the request body
      if (filePaths.length > 0 && filePaths[0]) {
        // Check if we're using the multiple files format
        if (filePaths.length === 1) {
          // Single file case
          requestBodyData.file_path = filePaths[0];
        } else {
          // Multiple files case
          requestBodyData.file_paths = filePaths.filter(path => path.trim() !== '');
        }
      }
      
      // Create headers object from enabled headers
      const headersObj = {};
      requestHeaders.forEach(header => {
        if (header.enabled && header.key.trim() !== '') {
          headersObj[header.key] = header.value;
        }
      });
      
      // Send the request
      const requestOptions = {
        method: requestMethod,
        headers: headersObj,
        body: JSON.stringify(requestBodyData)
      };
      
      const response = await fetch(requestUrl, requestOptions);
      const responseData = await response.json();
      const endTime = new Date();
      
      setResponse(responseData);
      setResponseStatus(response.status);
      setResponseTime(endTime - startTime);
      
      // Also update the result for the original form display
      setResult(responseData);
      
    } catch (err) {
      console.error('Request error:', err);
      setError(err.message || 'An error occurred while sending the request');
      setResponseStatus('Error');
      setResponse({ error: err.message || 'An error occurred while sending the request' });
    } finally {
      setLoading(false);
    }
  };
  
  // Handle adding a new file path
  const handleAddFilePath = () => {
    setFilePaths([...filePaths, '']);
  };
  
  // Handle removing a file path
  const handleRemoveFilePath = (index) => {
    const newFilePaths = [...filePaths];
    newFilePaths.splice(index, 1);
    
    // Ensure we always have at least one file path
    if (newFilePaths.length === 0) {
      newFilePaths.push('');
    }
    
    setFilePaths(newFilePaths);
  };
  
  // Handle changing a file path
  const handleFilePathChange = (index, value) => {
    const newFilePaths = [...filePaths];
    newFilePaths[index] = value;
    setFilePaths(newFilePaths);
    
    // Update the first file path in the simple form as well
    if (index === 0) {
      setFilePath(value);
    }
  };
  
  // Handle adding a new header
  const handleAddHeader = () => {
    setRequestHeaders([...requestHeaders, { key: '', value: '', enabled: true }]);
  };
  
  // Handle removing a header
  const handleRemoveHeader = (index) => {
    const newHeaders = [...requestHeaders];
    newHeaders.splice(index, 1);
    setRequestHeaders(newHeaders);
  };
  
  // Handle changing a header
  const handleHeaderChange = (index, field, value) => {
    const newHeaders = [...requestHeaders];
    newHeaders[index][field] = value;
    setRequestHeaders(newHeaders);
  };

  return (
    <div className="bg-white rounded-lg shadow-md mb-6">
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Process JSON Edit from Local File</h2>
          <button
            type="button"
            onClick={() => setShowAdvancedPanel(!showAdvancedPanel)}
            className="px-3 py-1 text-sm font-medium text-indigo-600 border border-indigo-600 rounded-md hover:bg-indigo-50"
          >
            {showAdvancedPanel ? 'Simple Mode' : 'Advanced Mode'}
          </button>
        </div>
        
        {!showAdvancedPanel ? (
          // Simple form
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Local JSON File Path
              </label>
              <input
                type="text"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder="C:\path\to\your\file.json"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Enter the full path to a JSON file on your local system
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Edit ID
              </label>
              <input
                type="text"
                value={editId}
                onChange={(e) => setEditId(e.target.value)}
                placeholder="Edit 1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
              <p className="mt-1 text-sm text-gray-500">
                Optional: Default is "Edit 1" for validation purposes
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`${
                loading
                  ? 'bg-indigo-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700'
              } text-white font-medium py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
            >
              {loading ? 'Processing...' : 'Process Edit'}
            </button>
          </form>
        ) : (
          // Advanced Postman-like panel
          <div>
            {/* Request URL bar */}
            <div className="flex mb-4">
              <select
                value={requestMethod}
                onChange={(e) => setRequestMethod(e.target.value)}
                className="px-2 py-2 border border-r-0 border-gray-300 rounded-l-md bg-gray-50 text-gray-700 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="POST">POST</option>
                <option value="GET">GET</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
              </select>
              <input
                type="text"
                value={requestUrl}
                onChange={(e) => setRequestUrl(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Enter request URL"
              />
              <button
                type="button"
                onClick={handleSendRequest}
                disabled={loading}
                className={`px-4 py-2 rounded-r-md text-white font-medium ${
                  loading ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
                }`}
              >
                {loading ? 'Sending...' : 'Send'}
              </button>
            </div>
            
            {/* Multiple File Paths Section */}
            <div className="mb-4 border border-gray-300 rounded-md p-4 bg-gray-50">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-medium text-gray-700">JSON File Paths</h3>
                <button
                  type="button"
                  onClick={handleAddFilePath}
                  className="text-xs px-2 py-1 bg-indigo-500 text-white rounded hover:bg-indigo-600"
                >
                  Add File
                </button>
              </div>
              
              {filePaths.map((path, index) => (
                <div key={index} className="flex items-center mb-2">
                  <input
                    type="text"
                    value={path}
                    onChange={(e) => handleFilePathChange(index, e.target.value)}
                    placeholder={`C:\\path\\to\\file${index + 1}.json`}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveFilePath(index)}
                    disabled={filePaths.length === 1}
                    className={`ml-2 text-red-500 ${filePaths.length === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:text-red-700'}`}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))}
              
              <p className="text-xs text-gray-500 mt-1">
                Enter the full paths to JSON files on your local system. These will be used to update the request body.
              </p>
            </div>
            
            {/* Tabs */}
            <div className="flex border-b border-gray-200 mb-4">
              <button
                className={`px-4 py-2 font-medium rounded-t-md ${activeTab === 'body' ? 'bg-indigo-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => setActiveTab('body')}
              >
                Body
              </button>
              <button
                className={`px-4 py-2 font-medium ml-2 rounded-t-md ${activeTab === 'headers' ? 'bg-indigo-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => setActiveTab('headers')}
              >
                Headers
              </button>
              <button
                className={`px-4 py-2 font-medium ml-2 rounded-t-md ${activeTab === 'response' ? 'bg-indigo-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => setActiveTab('response')}
              >
                Response
              </button>
            </div>
            
            {/* Body Tab */}
            <div id="bodyTab" className={activeTab === 'body' ? '' : 'hidden'}>
              <textarea
                value={requestBody}
                onChange={(e) => setRequestBody(e.target.value)}
                className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md font-mono text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Enter JSON request body"
              />
              <p className="text-xs text-gray-500 mt-1">
                The file paths specified above will be included in the request automatically.
              </p>
            </div>
            
            {/* Headers Tab */}
            <div id="headersTab" className={activeTab === 'headers' ? '' : 'hidden'}>
              <div className="mb-2">
                <button
                  type="button"
                  onClick={handleAddHeader}
                  className="text-xs px-2 py-1 bg-indigo-500 text-white rounded hover:bg-indigo-600"
                >
                  Add Header
                </button>
              </div>
              
              {requestHeaders.map((header, index) => (
                <div key={index} className="flex items-center mb-2">
                  <input
                    type="checkbox"
                    checked={header.enabled}
                    onChange={(e) => handleHeaderChange(index, 'enabled', e.target.checked)}
                    className="mr-2"
                  />
                  <input
                    type="text"
                    value={header.key}
                    onChange={(e) => handleHeaderChange(index, 'key', e.target.value)}
                    placeholder="Header key"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                  <input
                    type="text"
                    value={header.value}
                    onChange={(e) => handleHeaderChange(index, 'value', e.target.value)}
                    placeholder="Header value"
                    className="flex-1 ml-2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveHeader(index)}
                    className="ml-2 text-red-500 hover:text-red-700"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
            
            {/* Response Tab */}
            <div id="responseTab" className={activeTab === 'response' ? '' : 'hidden'}>
              {response ? (
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center">
                      <span className={`inline-block px-2 py-1 text-xs font-medium rounded-md ${
                        responseStatus >= 200 && responseStatus < 300 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        Status: {responseStatus}
                      </span>
                      {responseTime && (
                        <span className="ml-2 text-xs text-gray-500">
                          Time: {responseTime}ms
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="border border-gray-300 rounded-md p-4 bg-gray-50 font-mono text-sm overflow-auto h-60">
                    <pre>{JSON.stringify(response, null, 2)}</pre>
                  </div>
                </div>
              ) : (
                <div className="border border-gray-300 rounded-md p-4 bg-gray-50 text-gray-500 h-60 flex items-center justify-center">
                  Send a request to see the response
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Results display (always visible) */}
      {(result || error) && (
        <div className="px-6 pb-6">
          {result && (
            <div className="mt-4 p-4 border border-green-300 bg-green-50 rounded-md">
              <h3 className="text-lg font-medium text-green-800 mb-2">Success!</h3>
              <p className="text-green-700">{result.message}</p>
              <div className="mt-2 text-sm text-green-600">
                <p>Edit ID: {result.edit_id}</p>
                <p>The response has been saved to the Excel file in the "Processed JSON" tab.</p>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 border border-red-300 bg-red-50 rounded-md">
              <h3 className="text-lg font-medium text-red-800 mb-2">Error</h3>
              <p className="text-red-700">{error}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LocalJsonEdit; 