import React, { useState, useEffect, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  flexRender
} from '@tanstack/react-table';
import axios from 'axios';
import { exportResponsesToExcel } from '../services/apiService';

const DataTable = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sorting, setSorting] = useState([]);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });
  const [selectedDomain, setSelectedDomain] = useState('all');
  const [uniqueDomains, setUniqueDomains] = useState(['all']);

  useEffect(() => {
    const fetchResponses = async () => {
      try {
        // This endpoint would need to be implemented to get all responses
        const response = await axios.get('http://localhost:5000/get-all-responses');
        
        // Process the responses to ensure domain information is available
        let responseData = response.data?.responses || [];
        
        // Add domain information if it doesn't exist
        responseData = responseData.map(item => {
          // If domain is already provided by the backend, use it
          if (item.domain) {
            return item;
          }
          
          // Otherwise, extract domain from api_response or input_json if available
          let domain = 'unknown';
          
          try {
            // Try to extract domain from api_response if it contains a URL
            if (item.api_response && typeof item.api_response === 'object') {
              const apiResponse = item.api_response;
              
              // Check common fields that might contain URLs
              if (apiResponse.url) {
                const url = new URL(apiResponse.url);
                domain = url.hostname;
              } else if (apiResponse.endpoint) {
                const url = new URL(apiResponse.endpoint);
                domain = url.hostname;
              }
            }
            
            // If still unknown, try input_json
            if (domain === 'unknown' && item.input_json) {
              try {
                const inputData = JSON.parse(item.input_json);
                if (inputData.url) {
                  const url = new URL(inputData.url);
                  domain = url.hostname;
                }
              } catch (e) {
                // Ignore parsing errors
              }
            }
          } catch (e) {
            console.warn('Error extracting domain:', e);
          }
          
          return { ...item, domain };
        });
        
        // Extract unique domains for the filter dropdown
        const domains = ['all', ...new Set(responseData.map(item => item.domain))];
        setUniqueDomains(domains);
        
        setData(responseData);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch responses');
        setLoading(false);
        // For development, use sample data
        const sampleData = [
          { domain: 'api.example.com', edit_id: 'E12345', timestamp: '2025-03-07T12:00:00', status: 'Success' },
          { domain: 'dev.example.org', edit_id: 'E12346', timestamp: '2025-03-07T12:15:00', status: 'Failed' },
          { domain: 'api.example.com', edit_id: 'E12347', timestamp: '2025-03-07T12:30:00', status: 'Success' },
        ];
        setData(sampleData);
        // Extract unique domains from sample data
        const domains = ['all', ...new Set(sampleData.map(item => item.domain))];
        setUniqueDomains(domains);
      }
    };

    fetchResponses();
  }, []);

  // Filter the data based on the selected domain
  const filteredData = useMemo(() => {
    if (selectedDomain === 'all') {
      return data;
    }
    return data.filter(item => item.domain === selectedDomain);
  }, [data, selectedDomain]);

  const columns = useMemo(
    () => [
      {
        accessorKey: 'domain',
        header: 'Domain',
      },
      {
        accessorKey: 'edit_id',
        header: 'Edit ID',
      },
      {
        accessorKey: 'timestamp',
        header: 'Timestamp',
      },
      {
        accessorKey: 'status',
        header: 'Status',
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => (
          <button
            onClick={() => alert(`View details for ${row.original.edit_id}`)}
            className="text-blue-500 hover:text-blue-700"
          >
            View Details
          </button>
        ),
      },
    ],
    []
  );

  const table = useReactTable({
    data: filteredData,
    columns,
    state: {
      sorting,
      pagination,
    },
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  if (loading) return <div className="text-center py-4">Loading responses...</div>;

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">API Responses</h2>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="appearance-none bg-white border border-gray-300 rounded-md pl-3 pr-8 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {uniqueDomains.map((domain) => (
                <option key={domain} value={domain}> 
                  {domain === 'all' ? 'All Domains' : domain}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          </div>
          <button
            onClick={() => {
              // Apply domain filter to the export when a specific domain is selected
              const exportParams = {};
              if (selectedDomain !== 'all') {
                exportParams.domain = selectedDomain;
              }
              
              // Ensure exportResponsesToExcel is called correctly with domain data
              exportResponsesToExcel(exportParams)
                .then(() => {
                  console.log('Export successful');
                  // Optional: Add success notification
                  const successToast = document.createElement('div');
                  successToast.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg z-50';
                  successToast.textContent = 'Export completed successfully';
                  document.body.appendChild(successToast);
                  setTimeout(() => {
                    document.body.removeChild(successToast);
                  }, 3000);
                })
                .catch(error => {
                  console.error('Export failed:', error);
                  // Optional: Add error notification
                  const errorToast = document.createElement('div');
                  errorToast.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-md shadow-lg z-50';
                  errorToast.textContent = 'Export failed. Please try again.';
                  document.body.appendChild(errorToast);
                  setTimeout(() => {
                    document.body.removeChild(errorToast);
                  }, 3000);
                });
            }}
            className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          >
            Export to Excel
          </button>
        </div>
      </div>

      {/* Add a summary of applied filters if any */}
      {selectedDomain !== 'all' && (
        <div className="mb-3 flex items-center text-sm text-gray-600">
          <span className="mr-2">Filtered by domain:</span>
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded flex items-center">
            {selectedDomain}
            <button 
              onClick={() => setSelectedDomain('all')} 
              className="ml-1 text-blue-600 hover:text-blue-800 focus:outline-none"
              title="Clear filter"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </span>
        </div>
      )}

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
  );
};

export default DataTable; 