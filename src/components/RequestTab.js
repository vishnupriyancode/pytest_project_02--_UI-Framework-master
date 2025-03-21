import React, { useState } from 'react';
import FileUploader from './FileUploader';
import BulkUploader from './BulkUploader';
import ResponseViewer from './ResponseViewer';

const RequestTab = () => {
  const [uploadedResponse, setUploadedResponse] = useState(null);
  const [activeSection, setActiveSection] = useState('single');

  return (
    <div>
      <div className="mb-6">
        <div className="flex border-b border-gray-200 mb-4">
          <button
            className={`py-2 px-4 text-sm font-medium ${
              activeSection === 'single'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveSection('single')}
          >
            Single File Upload
          </button>
          <button
            className={`py-2 px-4 text-sm font-medium ${
              activeSection === 'bulk'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveSection('bulk')}
          >
            Bulk Processing
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {activeSection === 'single' ? (
            <FileUploader onUploadSuccess={setUploadedResponse} />
          ) : (
            <BulkUploader onUploadSuccess={setUploadedResponse} />
          )}
          <ResponseViewer />
        </div>
      </div>

      {uploadedResponse && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-xl font-semibold mb-4">Last Upload Result</h2>
          <div className="bg-gray-100 p-4 rounded-md overflow-auto max-h-96">
            <pre className="text-sm whitespace-pre-wrap">
              {JSON.stringify(uploadedResponse, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default RequestTab; 