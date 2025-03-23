import React, { useState, useEffect, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender
} from '@tanstack/react-table';
import { getProcessedJsons, downloadExcelReport } from '../services/apiService';
import API_CONFIG from '../config/apiConfig';
import LocalJsonEdit from './LocalJsonEdit';

const ProcessedJsons = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sorting, setSorting] = useState([]);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    const fetchProcessedJsons = async () => {
      try {
        setLoading(true);
        const response = await getProcessedJsons();
        setData(response || []);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching Run JSONs:', err);
        setError('Failed to load Run JSON records');
        setLoading(false);
        // For development, set sample data
        setData([
          {
            id: '1',
            fileName: 'example1.json',
            timestamp: '2025-03-08T12:00:00Z',
            status: 'Success',
            response: { 
              message: "Process completed successfully", 
              recordCount: 42,
              details: { 
                processTime: "120ms", 
                validationErrors: [] 
              }
            }
          },
          {
            id: '2',
            fileName: 'example2.json',
            timestamp: '2025-03-08T12:30:00Z',
            status: 'Failed',
            response: { 
              message: "Validation error", 
              recordCount: 0,
              details: { 
                processTime: "45ms", 
                validationErrors: ["Invalid JSON structure at line 23"] 
              }
            }
          },
          {
            id: '3',
            fileName: 'example3.json',
            timestamp: '2025-03-08T13:00:00Z',
            status: 'Success',
            response: { 
              message: "Process completed successfully", 
              recordCount: 128,
              details: { 
                processTime: "350ms", 
                validationErrors: [] 
              }
            }
          }
        ]);
      }
    };

    fetchProcessedJsons();
  }, []);

  const handleViewDetails = (record) => {
    setSelectedRecord(record);
  };

  const handleDownloadExcel = async (id, event) => {
    try {
      // Disable the button to prevent multiple clicks
      const button = event && event.currentTarget ? event.currentTarget : document.querySelector(`button[data-id="${id}"]`);
      
      if (button) {
        button.disabled = true;
        button.innerHTML = `
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Downloading...
        `;
      }
      
      // First check API connection
      const { testApiConnection } = await import('../config/apiConfig');
      const apiStatus = await testApiConnection(5000);
      
      if (!apiStatus.success) {
        throw new Error(`API server is unreachable: ${apiStatus.error || 'Unknown error'}`);
      }
      
      // Initiate the download
      const result = await downloadExcelReport(id);
      console.log('Download initiated:', result);
      
      // Show success message
      setSuccess(`Download initiated for report ${id}`);
      
      // Reset button after successful download
      if (button) {
        setTimeout(() => {
          button.disabled = false;
          button.innerHTML = 'Download Excel';
        }, 3000);
      }
    } catch (err) {
      console.error('Error downloading Excel report:', err);
      
      // Reset the button but show as error state
      const button = event && event.currentTarget ? event.currentTarget : document.querySelector(`button[data-id="${id}"]`);
      
      if (button) {
        button.disabled = false;
        button.innerHTML = 'Retry Download';
        button.classList.add('bg-red-500');
        button.classList.add('hover:bg-red-600');
        
        // Provide more detailed error if available
        setError(`Download failed: ${err.message || 'Unknown error'}`);
        
        // Reset button styling after 3 seconds
        setTimeout(() => {
          button.classList.remove('bg-red-500');
          button.classList.remove('hover:bg-red-600');
        }, 3000);
      } else {
        // Fallback if button can't be found
        setError(`Download failed: ${err.message || 'Unknown error'}`);
      }
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (err) {
      return dateString;
    }
  };

  const columns = useMemo(
    () => [
      {
        accessorKey: 'fileName',
        header: 'File Name',
      },
      {
        accessorKey: 'timestamp',
        header: 'Timestamp',
        cell: ({ getValue }) => formatDate(getValue()),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ getValue }) => {
          const value = getValue();
          return (
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
              value === 'Success' 
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {value}
            </span>
          );
        },
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => (
          <div className="flex space-x-2">
            <button
              onClick={() => handleViewDetails(row.original)}
              className="text-blue-500 hover:text-blue-700"
            >
              View Response
            </button>
            <button
              onClick={(e) => handleDownloadExcel(row.original.id, e)}
              className="text-green-500 hover:text-green-700"
              data-id={row.original.id}
            >
              Download Excel
            </button>
          </div>
        ),
      },
    ],
    []
  );

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      pagination,
    },
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  // Add a new function to handle retry for all downloads
  const handleRetryAllDownloads = async (e) => {
    try {
      const button = e.currentTarget;
      button.disabled = true;
      button.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Checking API Connection...
      `;

      // Import testApiConnection function
      const { testApiConnection } = await import('../config/apiConfig');
      
      // Check API connection first
      try {
        button.innerHTML = `
          <svg class="animate-spin -ml-1 mr-2 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Testing API server...
        `;

        // Use a longer timeout for the API check
        const apiStatus = await testApiConnection(8000);
        
        if (!apiStatus.success) {
          console.error('API connection test failed:', apiStatus.error);
          button.innerHTML = 'API Server Unreachable';
          button.classList.add('bg-red-600');
          
          // Create an error toast with more details
          const toast = document.createElement('div');
          toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-md shadow-lg z-50';
          toast.innerHTML = `
            <div class="font-bold">API Connection Failed</div>
            <div class="text-sm">Could not connect to API server at ${API_CONFIG.BASE_URL}</div>
            <div class="text-xs mt-1">Check that your API server is running and accessible.</div>
          `;
          document.body.appendChild(toast);
          
          setTimeout(() => {
            document.body.removeChild(toast);
            button.disabled = false;
            button.innerHTML = 'Retry Download';
            button.classList.remove('bg-red-600');
          }, 5000);
          
          return;
        }
        
        // If API is reachable, show progress and attempt the download
        button.innerHTML = `
          <svg class="animate-spin -ml-1 mr-2 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Downloading Excel...
        `;
      } catch (error) {
        console.error('Error checking API connection:', error);
        button.innerHTML = 'Connection Error';
        button.classList.add('bg-red-600');
        
        setTimeout(() => {
          button.disabled = false;
          button.innerHTML = 'Retry Download';
          button.classList.remove('bg-red-600');
        }, 3000);
        
        return;
      }

      // If API is reachable, attempt the download
      try {
        await downloadExcelReport('all');
        button.innerHTML = 'Download Successful';
        button.classList.add('bg-green-600');
        
        setTimeout(() => {
          button.disabled = false;
          button.innerHTML = 'Retry Download';
          button.classList.remove('bg-green-600');
        }, 3000);
      } catch (err) {
        console.error('Download retry failed:', err);
        button.innerHTML = 'Download Failed';
        button.classList.add('bg-red-600');
        
        setTimeout(() => {
          button.disabled = false;
          button.innerHTML = 'Retry Download';
          button.classList.remove('bg-red-600');
        }, 3000);
      }
    } catch (err) {
      console.error('Error in retry function:', err);
      e.currentTarget.disabled = false;
      e.currentTarget.innerHTML = 'Retry Download';
    }
  };

  if (loading) return <div className="text-center py-4">Loading processed JSON records...</div>;
  if (error && data.length === 0) return <div className="text-center text-red-500 py-4">{error}</div>;

  return (
    <div>
      <LocalJsonEdit />
      
      <div className="p-6">
        <h2 className="text-2xl font-bold mb-6">Run JSON Files</h2>
        
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
            <p>{error}</p>
            <button 
              className="text-red-700 font-bold ml-2"
              onClick={() => setError(null)}
            >
              ×
            </button>
          </div>
        )}
        
        {success && (
          <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4" role="alert">
            <p>{success}</p>
            <button 
              className="text-green-700 font-bold ml-2"
              onClick={() => setSuccess(null)}
            >
              ×
            </button>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Run JSON Files</h2>
              <button
                onClick={(e) => handleRetryAllDownloads(e)}
                className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                Retry All Downloads
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  {table.getHeaderGroups().map(headerGroup => (
                    <tr key={headerGroup.id}>
                      {headerGroup.headers.map(header => (
                        <th
                          key={header.id}
                          onClick={header.column.getToggleSortingHandler()}
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                        >
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                          <span>
                            {{
                              asc: ' 🔼',
                              desc: ' 🔽',
                            }[header.column.getIsSorted()] ?? ''}
                          </span>
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {table.getRowModel().rows.map(row => (
                    <tr key={row.id}>
                      {row.getVisibleCells().map(cell => (
                        <td
                          key={cell.id}
                          className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                        >
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center space-x-2">
                <span>
                  Page{' '}
                  <strong>
                    {table.getState().pagination.pageIndex + 1} of{' '}
                    {table.getPageCount()}
                  </strong>
                </span>
                <select
                  value={table.getState().pagination.pageSize}
                  onChange={e => {
                    table.setPageSize(Number(e.target.value));
                  }}
                  className="border border-gray-300 rounded px-2 py-1"
                >
                  {[10, 20, 30, 40, 50].map(pageSize => (
                    <option key={pageSize} value={pageSize}>
                      Show {pageSize}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => table.setPageIndex(0)}
                  disabled={!table.getCanPreviousPage()}
                  className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
                >
                  {'<<'}
                </button>
                <button
                  onClick={() => table.previousPage()}
                  disabled={!table.getCanPreviousPage()}
                  className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
                >
                  {'<'}
                </button>
                <button
                  onClick={() => table.nextPage()}
                  disabled={!table.getCanNextPage()}
                  className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
                >
                  {'>'}
                </button>
                <button
                  onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                  disabled={!table.getCanNextPage()}
                  className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
                >
                  {'>>'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Response Details Modal */}
        {selectedRecord && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Response Details: {selectedRecord.fileName}</h2>
              <button 
                onClick={() => setSelectedRecord(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                Close
              </button>
            </div>
            <div className="mb-2">
              <span className="font-medium">File:</span> {selectedRecord.fileName}
            </div>
            <div className="mb-2">
              <span className="font-medium">Processed at:</span> {formatDate(selectedRecord.timestamp)}
            </div>
            <div className="mb-4">
              <span className="font-medium">Status:</span> 
              <span className={`ml-2 px-2.5 py-0.5 rounded-full text-xs font-medium ${
                selectedRecord.status === 'Success' 
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {selectedRecord.status}
              </span>
            </div>
            <div>
              <h3 className="font-medium mb-2">Response:</h3>
              <div className="bg-gray-100 p-4 rounded-md overflow-auto max-h-96">
                <pre className="text-sm whitespace-pre-wrap">
                  {JSON.stringify(selectedRecord.response, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessedJsons; 