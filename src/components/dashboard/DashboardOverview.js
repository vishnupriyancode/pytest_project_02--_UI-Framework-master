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
  
  const [timelineData, setTimelineData] = useState([
    { date: '2025-03-01', success: 12, failed: 2 },
    { date: '2025-03-02', success: 15, failed: 3 },
    { date: '2025-03-03', success: 8, failed: 4 },
    { date: '2025-03-04', success: 16, failed: 0 },
    { date: '2025-03-05', success: 9, failed: 2 },
    { date: '2025-03-06', success: 11, failed: 1 },
    { date: '2025-03-07', success: 7, failed: 0 },
    { date: '2025-03-08', success: 9, failed: 3 },
  ]);
  
  const [selectedTimeRange, setSelectedTimeRange] = useState('week');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [filteredTimelineData, setFilteredTimelineData] = useState([]);
  
  // Filter data based on selected date and time range
  useEffect(() => {
    let filteredData = [...timelineData];
    
    // If a specific date is selected
    if (selectedDate) {
      const dateStr = selectedDate.toISOString().split('T')[0];
      filteredData = timelineData.filter(item => {
        // For exact date match
        return item.date === dateStr;
      });
      
      // If no data for the selected date, keep original data
      if (filteredData.length === 0) {
        filteredData = [];
      }
    } else {
      // No date selected, show all data for the selected time range
      filteredData = [...timelineData];
    }
    
    setFilteredTimelineData(filteredData);
  }, [selectedDate, timelineData]);
  
  // Handle date change
  const handleDateChange = (date) => {
    setSelectedDate(date);
  };
  
  // Clear the date filter
  const clearDateFilter = () => {
    setSelectedDate(null);
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
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Dashboard Overview</h1>
      
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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-card shadow-card p-5 border border-ui-border">
          <StatusChart data={statusData} />
        </div>
        
        <div className="bg-white rounded-card shadow-card p-5 border border-ui-border">
          <div className="flex justify-between items-center mb-2">
            <div className="text-xl font-bold">Request Timeline</div>
            <div className="flex items-center space-x-2">
              <button 
                className={`px-3 py-1 text-sm rounded-button ${
                  selectedTimeRange === 'week' 
                    ? 'bg-brand-accent text-white' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                onClick={() => setSelectedTimeRange('week')}
              >
                Week
              </button>
              <button 
                className={`px-3 py-1 text-sm rounded-button ${
                  selectedTimeRange === 'month' 
                    ? 'bg-brand-accent text-white' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                onClick={() => setSelectedTimeRange('month')}
              >
                Month
              </button>
              <div className="pl-2 border-l border-gray-200 ml-2">
                <div className="flex items-center">
                  <DatePicker
                    selected={selectedDate}
                    onChange={handleDateChange}
                    dateFormat="yyyy-MM-dd"
                    isClearable
                    placeholderText="Select a date"
                    className="px-3 py-1 text-sm rounded-button border border-gray-200 focus:outline-none focus:ring-2 focus:ring-brand-accent"
                  />
                  {selectedDate && (
                    <button
                      onClick={clearDateFilter}
                      className="ml-2 text-xs text-gray-500 hover:text-gray-700"
                      title="Clear date filter"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
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