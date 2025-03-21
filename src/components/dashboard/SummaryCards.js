import React from 'react';

const SummaryCards = ({ data }) => {
  if (!data) return null;
  
  return (
    <>
      {/* Total Requests Card */}
      <div className="bg-white p-4 rounded-lg shadow-md">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-blue-100 text-blue-500">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div className="ml-4">
            <h2 className="font-semibold text-gray-600">Total Requests</h2>
            <p className="text-2xl font-bold">{data.totalRequests}</p>
          </div>
        </div>
      </div>

      {/* Status Card */}
      <div className="bg-white p-4 rounded-lg shadow-md">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-green-100 text-green-500">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="ml-4">
            <h2 className="font-semibold text-gray-600">Success Rate</h2>
            <p className="text-2xl font-bold">
              {Math.round((data.statusBreakdown.success / data.totalRequests) * 100)}%
            </p>
            <p className="text-sm text-gray-500">
              {data.statusBreakdown.success} successful / {data.statusBreakdown.failed} failed
            </p>
          </div>
        </div>
      </div>

      {/* Recent Activity Card */}
      <div className="bg-white p-4 rounded-lg shadow-md">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-purple-100 text-purple-500">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="ml-4">
            <h2 className="font-semibold text-gray-600">Recent Activity</h2>
            <p className="text-2xl font-bold">{data.recentActivity.today}</p>
            <p className="text-sm text-gray-500">
              {data.recentActivity.thisWeek} this week / {data.recentActivity.thisMonth} this month
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default SummaryCards; 