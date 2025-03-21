import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LabelList
} from 'recharts';
import { STATUS_COLORS, CHART_COLORS } from '../../theme/colorScheme';

const TimelineChart = ({ data }) => {
  // Handle case when no data is available
  if (!data || data.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className="h-12 w-12 mx-auto mb-2 text-gray-400"
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-lg font-medium">No data available for selected date</p>
          <p className="text-sm">Try selecting a different date or time range</p>
        </div>
      </div>
    );
  }

  // Format the dates for display
  const formatData = data.map(item => ({
    ...item,
    formattedDate: formatDate(item.date)
  }));

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  // Custom tooltip component for better styling
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const total = payload.reduce((sum, entry) => sum + entry.value, 0);
      
      return (
        <div className="bg-white p-3 shadow-md rounded border border-gray-200">
          <p className="font-semibold text-gray-800">{label}</p>
          <div className="space-y-1 mt-1">
            {payload.map((entry, index) => (
              <div key={index} className="flex items-center">
                <div 
                  className="w-3 h-3 rounded-full mr-2" 
                  style={{ backgroundColor: entry.color }}
                />
                <p className="text-sm text-gray-600">
                  <span className="font-medium">{entry.name}: </span>
                  {entry.value} requests
                </p>
              </div>
            ))}
          </div>
          <div className="mt-1 pt-1 border-t border-gray-100">
            <p className="text-xs text-gray-500">Total: {total} requests</p>
          </div>
        </div>
      );
    }
    
    return null;
  };

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={formatData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 5
          }}
          barGap={0}
          barCategoryGap={8}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            dataKey="formattedDate" 
            tick={{ fill: '#6B7280', fontSize: 12 }}
            axisLine={{ stroke: '#D1D5DB' }}
          />
          <YAxis 
            tick={{ fill: '#6B7280', fontSize: 12 }}
            axisLine={{ stroke: '#D1D5DB' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ paddingTop: 10 }}
          />
          <Bar 
            dataKey="success" 
            name="Success" 
            fill={STATUS_COLORS.SUCCESS}
            radius={[4, 4, 0, 0]}
          />
          <Bar 
            dataKey="failed" 
            name="Failed" 
            fill={STATUS_COLORS.FAILED}
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TimelineChart; 