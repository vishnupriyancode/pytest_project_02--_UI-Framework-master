import React from 'react';

function CreationTab() {
  return (
    <div className="p-6 bg-gray-100 rounded-lg shadow-md">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <button className="w-80 h-40 py-3 px-6 bg-gray-200 text-gray-700 text-lg font-semibold rounded-xl shadow-md hover:bg-gray-300 hover:shadow-lg transition-shadow flex flex-col justify-center items-center text-center">
          <h3 className="text-lg font-bold">Case Creation</h3>
          <p className="text-sm text-gray-600">Create and manage cases efficiently.</p>
        </button>
        <button className="w-80 h-40 py-3 px-6 bg-gray-200 text-gray-700 text-lg font-semibold rounded-xl shadow-md hover:bg-gray-300 hover:shadow-lg transition-shadow flex flex-col justify-center items-center text-center">
          <h3 className="text-lg font-bold">JSON Creation</h3>
          <p className="text-sm text-gray-600">Easily create JSON files.</p>
        </button>
        <button className="w-80 h-40 py-3 px-6 bg-gray-200 text-gray-700 text-lg font-semibold rounded-xl shadow-md hover:bg-gray-300 hover:shadow-lg transition-shadow flex flex-col justify-center items-center text-center">
          <h3 className="text-lg font-bold">File Comparison</h3>
          <p className="text-sm text-gray-600">Compare files with ease.</p>
        </button>
      </div>
    </div>
  );
}

export default CreationTab; 