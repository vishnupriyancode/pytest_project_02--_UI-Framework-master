import React, { useState } from 'react';
import { getResponseById } from '../services/apiService';

const ResponseViewer = () => {
  const [editId, setEditId] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchResponse = async (e) => {
    e.preventDefault();
    if (!editId.trim()) {
      setError('Please enter an Edit ID');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getResponseById(editId);
      setResponse(data);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      setError('Failed to fetch response. Please check the Edit ID and try again.');
      setResponse(null);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Fetch Response by Edit ID</h2>
      <form onSubmit={fetchResponse} className="mb-4">
        <div className="flex">
          <input
            type="text"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter Edit ID"
            value={editId}
            onChange={(e) => setEditId(e.target.value)}
          />
          <button
            type="submit"
            className="bg-blue-500 text-white py-2 px-4 rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Fetch'}
          </button>
        </div>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      </form>

      {response && (
        <div className="mt-4">
          <h3 className="text-lg font-medium mb-2">Response:</h3>
          <div className="bg-gray-100 p-4 rounded-md overflow-auto max-h-96">
            <pre className="text-sm whitespace-pre-wrap">{JSON.stringify(response, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResponseViewer; 