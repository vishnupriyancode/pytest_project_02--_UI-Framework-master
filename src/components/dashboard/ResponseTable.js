import React, { useState } from 'react';
import { exportResponsesToExcel } from '../../services/apiService';

const ResponseTable = ({ data, onRowClick, selectedEditId }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [expandedRow, setExpandedRow] = useState(null);
  const itemsPerPage = 5;

  if (!data || data.length === 0) {
    return <div className="text-center py-4 text-gray-500">No response data available</div>;
  }

  // Format date for display
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (err) {
      return dateString;
    }
  };

  // Format processing time for display
  const formatProcessingTime = (time) => {
    if (time < 1000) {
      return `${time}ms`;
    }
    return `${(time / 1000).toFixed(2)}s`;
  };

  // Handle row click
  const handleRowClick = (id) => {
    onRowClick(id);
    if (expandedRow === id) {
      setExpandedRow(null);
    } else {
      setExpandedRow(id);
    }
  };

  // Handle export to Excel
  const handleExport = async (event) => {
    try {
      const exportButton = event && event.currentTarget ? 
        event.currentTarget : document.getElementById('export-button');
        
      if (exportButton) {
        // Disable button and show loading state
        exportButton.disabled = true;
        exportButton.innerHTML = `
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Exporting...
        `;
      }

      await exportResponsesToExcel();
      
      if (exportButton) {
        // Reset button state after successful export
        setTimeout(() => {
          exportButton.disabled = false;
          exportButton.innerHTML = 'Export to Excel';
        }, 3000);
      }
    } catch (err) {
      console.error('Export error:', err);
      
      const exportButton = event && event.currentTarget ? 
        event.currentTarget : document.getElementById('export-button');
        
      if (exportButton) {
        // Reset button but show error state
        exportButton.disabled = false;
        exportButton.innerHTML = 'Export to Excel';
        exportButton.classList.add('bg-red-600');
        exportButton.classList.add('hover:bg-red-700');
        
        // Reset button after 2 seconds
        setTimeout(() => {
          exportButton.classList.remove('bg-red-600');
          exportButton.classList.remove('hover:bg-red-700');
        }, 2000);
      }
    }
  };

  // Calculate pagination
  const totalPages = Math.ceil(data.length / itemsPerPage);
  const currentData = data.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Domain
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Edit ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                File Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Processing Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {currentData.map((row) => (
              <React.Fragment key={row.id}>
                <tr 
                  className={`hover:bg-gray-50 cursor-pointer ${selectedEditId === row.id ? 'bg-blue-50' : ''}`}
                  onClick={() => handleRowClick(row.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {row.domain}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {row.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {row.fileName}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(row.timestamp)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      row.status === 'Success' 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {row.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatProcessingTime(row.processingTime)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button 
                      className="text-blue-500 hover:text-blue-700 mr-2"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRowClick(row.id);
                      }}
                    >
                      Details
                    </button>
                  </td>
                </tr>
                {expandedRow === row.id && (
                  <tr>
                    <td colSpan="7" className="px-6 py-4 bg-gray-50">
                      <div>
                        <h4 className="font-medium mb-2">Response Details:</h4>
                        <div className="space-y-2">
                          <div>
                            <span className="font-medium">Response Size:</span> {row.responseSize} bytes
                          </div>
                          {row.notes && row.notes.length > 0 && (
                            <div>
                              <span className="font-medium">Notes:</span>
                              <ul className="list-disc pl-5 mt-1">
                                {row.notes.map((note, index) => (
                                  <li key={index} className="text-sm">{note}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4">
        <div>
          <p className="text-sm text-gray-700">
            Showing <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> to{' '}
            <span className="font-medium">
              {Math.min(currentPage * itemsPerPage, data.length)}
            </span>{' '}
            of <span className="font-medium">{data.length}</span> results
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
            className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>

      {/* Export Button */}
      <div className="mt-4">
        <button
          id="export-button"
          onClick={(e) => handleExport(e)}
          className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
        >
          Export to Excel
        </button>
      </div>
    </div>
  );
};

export default ResponseTable; 