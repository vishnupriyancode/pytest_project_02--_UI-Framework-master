import React, { useState } from 'react';
import { uploadJsonFile } from '../services/apiService';

const FileUploader = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const validateJsonFile = (file) => {
    // Check if file is selected
    if (!file) return "Please select a JSON file";
    
    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) return "File size exceeds 5MB limit";
    
    // Check file extension
    if (!file.name.toLowerCase().endsWith('.json')) return "Selected file must be a JSON file (.json)";
    
    return null;
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError(null);
    setSuccess(null);
    
    // Validate file on selection
    if (selectedFile) {
      const validationError = validateJsonFile(selectedFile);
      if (validationError) {
        setError(validationError);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate file again before upload
    const validationError = validateJsonFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      const response = await uploadJsonFile(file);
      
      setLoading(false);
      setSuccess(`File "${file.name}" uploaded successfully!`);
      setFile(null);
      
      // Reset the file input
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) {
        fileInput.value = '';
      }
      
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
    } catch (err) {
      console.error('Upload error:', err);
      setLoading(false);
      
      // Extract error message from response if available
      let errorMessage = 'Failed to upload file. Please try again.';
      if (err.response && err.response.data && err.response.data.message) {
        errorMessage = `Error: ${err.response.data.message}`;
      } else if (err.message) {
        errorMessage = `Error: ${err.message}`;
      }
      
      setError(errorMessage);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Upload JSON File</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select JSON File
          </label>
          <input
            type="file"
            accept=".json"
            onChange={handleFileChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          {file && !error && (
            <div className="mt-2 text-sm text-gray-600">
              Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </div>
          )}
        </div>
        
        {error && (
          <div className="mb-4 p-2 bg-red-50 border-l-4 border-red-500 text-red-700">
            <p className="text-sm">{error}</p>
          </div>
        )}
        
        {success && (
          <div className="mb-4 p-2 bg-green-50 border-l-4 border-green-500 text-green-700">
            <p className="text-sm">{success}</p>
          </div>
        )}
        
        <button
          type="submit"
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
          disabled={loading || !file || error}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Uploading...
            </span>
          ) : (
            'Upload File'
          )}
        </button>
      </form>
    </div>
  );
};

export default FileUploader; 