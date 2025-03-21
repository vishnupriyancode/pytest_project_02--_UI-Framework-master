import React, { useState, useEffect } from 'react';
import StatusChart from './StatusChart';
import TimelineChart from './TimelineChart';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { UI_COLORS } from '../../theme/colorScheme';

const DashboardOverview = () => {
  const [statusData, setStatusData] = useState({
    success: 132,
    failed: 18,
    pending: 6
  });
  
  // Extended timeline data for month view
  const [timelineData, setTimelineData] = useState([
    { date: '2025-03-01', success: 12, failed: 2 },
    { date: '2025-03-02', success: 15, failed: 3 },
    { date: '2025-03-03', success: 8, failed: 4 },
    { date: '2025-03-04', success: 16, failed: 0 },
    { date: '2025-03-05', success: 9, failed: 2 },
    { date: '2025-03-06', success: 11, failed: 1 },
    { date: '2025-03-07', success: 7, failed: 0 },
    { date: '2025-03-08', success: 9, failed: 3 },
    { date: '2025-03-09', success: 13, failed: 1 },
    { date: '2025-03-10', success: 14, failed: 2 },
    { date: '2025-03-11', success: 10, failed: 1 },
    { date: '2025-03-12', success: 12, failed: 2 },
    { date: '2025-03-13', success: 15, failed: 0 },
    { date: '2025-03-14', success: 11, failed: 1 },
    { date: '2025-03-15', success: 13, failed: 2 },
    { date: '2025-03-16', success: 14, failed: 1 },
    { date: '2025-03-17', success: 12, failed: 0 },
    { date: '2025-03-18', success: 10, failed: 2 },
    { date: '2025-03-19', success: 11, failed: 1 },
    { date: '2025-03-20', success: 13, failed: 2 },
    { date: '2025-03-21', success: 15, failed: 0 },
    { date: '2025-03-22', success: 12, failed: 1 },
    { date: '2025-03-23', success: 14, failed: 2 },
    { date: '2025-03-24', success: 11, failed: 1 },
    { date: '2025-03-25', success: 13, failed: 0 },
    { date: '2025-03-26', success: 12, failed: 2 },
    { date: '2025-03-27', success: 10, failed: 1 },
    { date: '2025-03-28', success: 14, failed: 2 },
    { date: '2025-03-29', success: 15, failed: 1 },
    { date: '2025-03-30', success: 13, failed: 2 },
    { date: '2025-03-31', success: 12, failed: 1 }
  ]);
  
  const [selectedTimeRange, setSelectedTimeRange] = useState('week');
  const [dateRange, setDateRange] = useState({
    startDate: null,
    endDate: null
  });
  const [filteredTimelineData, setFilteredTimelineData] = useState([]);
  
  // Filter data based on selected date range and time range
  useEffect(() => {
    let filteredData = [...timelineData];
    
    if (dateRange.startDate && dateRange.endDate) {
      // If date range is selected, filter data between the dates
      filteredData = timelineData.filter(item => {
        const itemDate = new Date(item.date);
        return itemDate >= dateRange.startDate && itemDate <= dateRange.endDate;
      });
    } else {
      // Get current date for reference
      const today = new Date('2025-03-31'); // Using the last date in our dataset as reference
      
      if (selectedTimeRange === 'week') {
        // Get data for the last 7 days
        const weekAgo = new Date(today);
        weekAgo.setDate(today.getDate() - 6);
        
        filteredData = timelineData.filter(item => {
          const itemDate = new Date(item.date);
          return itemDate >= weekAgo && itemDate <= today;
        });
      } else if (selectedTimeRange === 'month') {
        // Get data for the current month
        const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
        const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        
        filteredData = timelineData.filter(item => {
          const itemDate = new Date(item.date);
          return itemDate >= startOfMonth && itemDate <= endOfMonth;
        });
      }
    }

    // Sort the filtered data by date
    filteredData.sort((a, b) => new Date(a.date) - new Date(b.date));
    setFilteredTimelineData(filteredData);
  }, [dateRange, selectedTimeRange, timelineData]);
  
  // Clear the date range
  const clearDateRange = () => {
    setDateRange({ startDate: null, endDate: null });
    setSelectedTimeRange('week'); // Reset to week view
  };
  
  // Summary metrics
  const summaryMetrics = [
    {
      title: 'Total Requests',
      value: statusData.success + statusData.failed + statusData.pending,
      change: '+12%',
      changeType: 'positive'
    },
    {
      title: 'Success Rate',
      value: `${Math.round((statusData.success / (statusData.success + statusData.failed + statusData.pending)) * 100)}%`,
      change: '+3%',
      changeType: 'positive'
    },
    {
      title: 'Avg. Response Time',
      value: '240ms',
      change: '-18ms',
      changeType: 'positive'
    },
    {
      title: 'Failed Requests',
      value: statusData.failed,
      change: '-4%',
      changeType: 'positive'
    }
  ];
  
  return (
    <div className="space-y-6">
      {/* Summary metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {summaryMetrics.map((metric, index) => (
          <div 
            key={index} 
            className="bg-white rounded-card shadow-card p-5 border border-ui-border hover:shadow-popup transition-shadow"
          >
            <h3 className="text-sm font-medium text-gray-500">{metric.title}</h3>
            <div className="mt-2 flex items-end justify-between">
              <div className="text-3xl font-semibold text-gray-800">{metric.value}</div>
              <div className={`text-sm font-medium ${
                metric.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
              }`}>
                {metric.change}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Chart sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <StatusChart data={statusData} />
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="mb-6">
            <div className="flex items-center justify-end space-x-4">
              <div className="flex items-center bg-white rounded-lg border shadow-sm">
                <button 
                  className={`px-4 py-2 text-sm font-medium rounded-l-lg ${
                    selectedTimeRange === 'week' && !dateRange.startDate
                      ? 'bg-blue-500 text-white' 
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                  onClick={() => {
                    setSelectedTimeRange('week');
                    setDateRange({ startDate: null, endDate: null });
                  }}
                >
                  Week
                </button>
                <button 
                  className={`px-4 py-2 text-sm font-medium border-l ${
                    selectedTimeRange === 'month' && !dateRange.startDate
                      ? 'bg-blue-500 text-white' 
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                  onClick={() => {
                    setSelectedTimeRange('month');
                    setDateRange({ startDate: null, endDate: null });
                  }}
                >
                  Month
                </button>
              </div>
              
              <div className="flex items-center space-x-2 bg-white rounded-lg border shadow-sm p-1">
                <div className="flex items-center space-x-2">
                  <div className="relative">
                    <DatePicker
                      selected={dateRange.startDate}
                      onChange={(date) => {
                        setDateRange(prev => ({ ...prev, startDate: date }));
                        setSelectedTimeRange('');
                      }}
                      selectsStart
                      startDate={dateRange.startDate}
                      endDate={dateRange.endDate}
                      dateFormat="MMM dd, yyyy"
                      className="px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholderText="From date"
                      isClearable
                      showPopperArrow={false}
                      minDate={new Date('2025-03-01')}
                      maxDate={new Date('2025-03-31')}
                      customInput={
                        <button className="flex items-center space-x-2 px-4 py-2 hover:bg-gray-50 rounded-lg">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                          </svg>
                          <span className="text-gray-700">{dateRange.startDate ? dateRange.startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'From date'}</span>
                        </button>
                      }
                    />
                  </div>
                  <span className="text-gray-400">|</span>
                  <div className="relative">
                    <DatePicker
                      selected={dateRange.endDate}
                      onChange={(date) => {
                        setDateRange(prev => ({ ...prev, endDate: date }));
                        setSelectedTimeRange('');
                      }}
                      selectsEnd
                      startDate={dateRange.startDate}
                      endDate={dateRange.endDate}
                      minDate={dateRange.startDate}
                      dateFormat="MMM dd, yyyy"
                      className="px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholderText="To date"
                      isClearable
                      showPopperArrow={false}
                      maxDate={new Date('2025-03-31')}
                      customInput={
                        <button className="flex items-center space-x-2 px-4 py-2 hover:bg-gray-50 rounded-lg">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                          </svg>
                          <span className="text-gray-700">{dateRange.endDate ? dateRange.endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'To date'}</span>
                        </button>
                      }
                    />
                  </div>
                </div>
                {(dateRange.startDate || dateRange.endDate) && (
                  <button
                    onClick={clearDateRange}
                    className="ml-2 p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md flex-shrink-0"
                    title="Clear date range"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          </div>
          <TimelineChart data={filteredTimelineData} />
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview; 