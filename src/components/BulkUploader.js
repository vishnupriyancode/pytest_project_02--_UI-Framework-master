import React, { useState, useRef } from 'react';
import { uploadMultipleJsonFiles } from '../services/apiService';

const BulkUploader = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadResults, setUploadResults] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files).filter(file => file.type === 'application/json' || file.name.endsWith('.json'));
    setFiles(prevFiles => [...prevFiles, ...selectedFiles]);
    
    if (selectedFiles.length < e.target.files.length) {
      setError('Only JSON files are accepted. Some non-JSON files were excluded.');
    } else {
      setError(null);
    }
    
    // Reset file input so the same file can be selected again if needed
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    
    // Clear previous upload results
    setUploadResults(null);
    setUploadStatus(null);
  };

  const handleRemoveFile = (indexToRemove) => {
    setFiles(prevFiles => prevFiles.filter((_, index) => index !== indexToRemove));
    setError(null);
  };

  const handleRemoveAllFiles = () => {
    setFiles([]);
    setError(null);
    setUploadStatus(null);
    setUploadResults(null);
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      setError('Please select at least one JSON file');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setUploadStatus('Preparing files for upload...');
      setUploadResults(null);
      
      // Create a FormData instance
      const formData = new FormData();
      
      // Add each file individually with the same key name
      files.forEach(file => {
        formData.append('jsonFiles', file);
      });
      
      // Log number of files for debugging
      console.log(`Preparing to upload ${files.length} files`);
      
      // Set upload status to uploading
      setUploadStatus(`Uploading ${files.length} files...`);
      
      // Add a timeout to abort the request if it takes too long
      const timeoutDuration = 30000; // 30 seconds
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeoutDuration);
      
      try {
        // Upload the files
        const response = await uploadMultipleJsonFiles(formData);
        
        // Clear the timeout
        clearTimeout(timeoutId);
        
        // Update UI with results
        setLoading(false);
        setUploadStatus(`Successfully processed ${response.processedCount || 0} files. ${response.failedCount || 0} files failed.`);
        setUploadResults(response);
        
        // Keep files in the list if there were errors
        if (response.failedCount === 0) {
          setFiles([]);
        }
        
        // Call the onUploadSuccess callback if provided
        if (onUploadSuccess) {
          onUploadSuccess(response);
        }
      } catch (uploadError) {
        // Clear the timeout
        clearTimeout(timeoutId);
        throw uploadError;
      }
    } catch (err) {
      console.error('Bulk upload error:', err);
      setLoading(false);
      
      // Display a user-friendly error message
      let displayError = 'Failed to upload files. Please try again.';
      
      if (err.name === 'AbortError') {
        displayError = 'Upload timed out. The server took too long to respond.';
      } else if (err.message && err.message.includes('API server is not accessible')) {
        displayError = 'Cannot connect to the API server. Please ensure it is running.';
      } else if (err.message) {
        displayError = `Upload failed: ${err.message}`;
      }
      
      setError(displayError);
      setUploadStatus(null);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Bulk Process JSON Files</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Multiple JSON Files
          </label>
          
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            multiple
            onChange={handleFileChange}
            className="hidden"
          />
          
          {/* File selection list */}
          <div className="border border-gray-300 rounded-md p-3 mb-4 bg-gray-50 min-h-[100px] max-h-[200px] overflow-y-auto">
            {files.length > 0 ? (
              <ul className="divide-y divide-gray-200">
                {files.map((file, index) => (
                  <li key={index} className="py-2 flex justify-between items-center">
                    <div className="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-indigo-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm truncate" title={file.name}>
                        {file.name} <span className="text-xs text-gray-500">({(file.size / 1024).toFixed(2)} KB)</span>
                      </span>
                    </div>
                    <button 
                      type="button" 
                      onClick={() => handleRemoveFile(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="flex flex-col items-center justify-center h-full py-4 text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-sm">No files selected</p>
                <p className="text-xs mt-1">Click "Browse Files" to select JSON files</p>
              </div>
            )}
          </div>
          
          {/* File count indicator */}
          {files.length > 0 && (
            <p className="text-sm text-gray-600 mb-2">
              {files.length} file(s) selected
            </p>
          )}
          
          {/* Button group */}
          <div className="flex space-x-2 mb-4">
            <button
              type="button"
              onClick={triggerFileInput}
              className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 flex items-center transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
              Browse Files
            </button>
            
            {files.length > 0 && (
              <button
                type="button"
                onClick={handleRemoveAllFiles}
                className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 flex items-center transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Remove All
              </button>
            )}
          </div>
        </div>
        
        {/* Error message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border-l-4 border-red-500 text-red-700 rounded">
            <p className="text-sm">{error}</p>
          </div>
        )}
        
        {/* Success status */}
        {uploadStatus && !error && (
          <div className="mb-4 p-3 bg-green-50 border-l-4 border-green-500 text-green-700 rounded">
            <p className="text-sm">{uploadStatus}</p>
          </div>
        )}
        
        {/* Upload results */}
        {uploadResults && uploadResults.failed && uploadResults.failed.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Failed Files:</h3>
            <ul className="text-xs text-red-600 list-disc pl-5">
              {uploadResults.failed.map((file, index) => (
                <li key={index}>
                  {file.filename}: {file.reason}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <button
          type="submit"
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 transition-colors"
          disabled={loading || files.length === 0}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Uploading...
            </span>
          ) : (
            'Upload Files'
          )}
        </button>
      </form>
    </div>
  );
};

export default BulkUploader; 