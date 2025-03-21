import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { STATUS_COLORS } from '../../theme/colorScheme';

const StatusChart = ({ data }) => {
  if (!data) return null;
  
  const chartData = [
    { name: 'Success', value: data.success || 0, color: STATUS_COLORS.SUCCESS },
    { name: 'Failed', value: data.failed || 0, color: STATUS_COLORS.FAILED },
    { name: 'Pending', value: data.pending || 0, color: STATUS_COLORS.PENDING }
  ];

  // Filter out zero values for a cleaner chart
  const filteredData = chartData.filter(item => item.value > 0);
  
  // Total number of requests for calculating percentages
  const totalRequests = filteredData.reduce((sum, item) => sum + item.value, 0);
  
  const RADIAN = Math.PI / 180;
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index, value, name }) => {
    // Increase the radius to position labels further outside the pie
    const radius = outerRadius * 1.4;
    
    // Calculate the position for the label
    const sin = Math.sin(-midAngle * RADIAN);
    const cos = Math.cos(-midAngle * RADIAN);
    
    // Position the text further from the pie
    const x = cx + radius * cos;
    const y = cy + radius * sin;
    
    // Calculate anchor point on the pie for the line
    const mx1 = cx + (outerRadius * 0.95) * cos;
    const my1 = cy + (outerRadius * 0.95) * sin;
    
    // Add a middle point for the line to create an elbow
    const mx2 = cx + (outerRadius * 1.2) * cos;
    const my2 = cy + (outerRadius * 1.2) * sin;
    
    // Calculate the text anchor based on position
    const textAnchor = cos >= 0 ? 'start' : 'end';
    
    return (
      <g>
        {/* Connecting line with elbow */}
        <path
          d={`M${mx1},${my1}L${mx2},${my2}L${x},${y}`}
          stroke={filteredData[index].color}
          fill="none"
          strokeWidth={1}
        />
        
        {/* Label background for better readability */}
        <rect
          x={x + (cos >= 0 ? 5 : -105)}
          y={y - 20}
          width="100"
          height="40"
          fill="white"
          fillOpacity="0.9"
          rx="4"
        />
        
        {/* Status name */}
        <text
          x={x + (cos >= 0 ? 10 : -10)}
          y={y - 8}
          textAnchor={textAnchor}
          fill="#374151"
          fontSize="12"
          fontWeight="500"
        >
          {name}
        </text>
        
        {/* Value and percentage on second line */}
        <text
          x={x + (cos >= 0 ? 10 : -10)}
          y={y + 8}
          textAnchor={textAnchor}
          fill="#374151"
          fontSize="13"
        >
          <tspan fontWeight="600">{value}</tspan>
          <tspan fill="#6B7280"> ({(percent * 100).toFixed(0)}%)</tspan>
        </text>
      </g>
    );
  };

  // Custom tooltip component
  const customTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 shadow-md rounded border border-gray-200">
          <p className="font-semibold text-gray-800">{data.name}</p>
          <p className="text-sm text-gray-600">
            <span className="font-medium">{data.value}</span> requests
          </p>
          <p className="text-xs text-gray-500">
            {`${(data.value / totalRequests * 100).toFixed(1)}% of total`}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="relative h-80">
      <h2 className="text-xl font-bold mb-2">Status Breakdown</h2>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={filteredData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomizedLabel}
            outerRadius={70}
            fill="#8884d8"
            dataKey="value"
          >
            {filteredData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={customTooltip} />
          <Legend
            verticalAlign="bottom"
            align="center"
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ paddingTop: 20 }}
          />
        </PieChart>
      </ResponsiveContainer>
      {totalRequests > 0 && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
          <div className="text-base font-semibold text-white">{totalRequests} Requests</div>
        </div>
      )}
    </div>
  );
};

export default StatusChart; 