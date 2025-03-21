import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { STATUS_COLORS, CHART_COLORS } from '../../theme/colorScheme';

const StatusChart = ({ data }) => {
  if (!data) return null;
  
  const chartData = [
    { name: 'Success', value: data.success || 0, color: STATUS_COLORS.SUCCESS },
    { name: 'Failed', value: data.failed || 0, color: STATUS_COLORS.FAILED },
    { name: 'Pending', value: data.pending || 0, color: STATUS_COLORS.PENDING }
  ];

  // Filter out zero values for a cleaner chart
  const filteredData = chartData.filter(item => item.value > 0);
  
  // Use primary colors from our theme
  const COLORS = CHART_COLORS.PRIMARY;
  
  const RADIAN = Math.PI / 180;
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.6;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    
    // Only show percentage for segments that are large enough
    if (percent < 0.05) return null;
    
    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor="middle" 
        dominantBaseline="central"
        fontWeight="bold"
        fontSize="14"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  // Total number of requests for displaying in the center
  const totalRequests = filteredData.reduce((sum, item) => sum + item.value, 0);

  // Custom tooltip formatter to show actual numbers
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
            outerRadius={90}
            innerRadius={45}
            fill="#8884d8"
            dataKey="value"
            stroke="none"
            paddingAngle={1}
          >
            {filteredData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={COLORS[index % COLORS.length]}
                style={{ filter: 'drop-shadow(0px 2px 3px rgba(0, 0, 0, 0.1))' }}
              />
            ))}
          </Pie>
          <Tooltip content={customTooltip} />
          <Legend 
            layout="horizontal" 
            verticalAlign="bottom" 
            align="center" 
            iconType="circle"
            iconSize={10}
            wrapperStyle={{ paddingTop: 10 }}
          />
        </PieChart>
      </ResponsiveContainer>
      {totalRequests > 0 && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
          <div className="text-xl font-bold text-gray-700">{totalRequests}</div>
          <div className="text-xs text-gray-500">requests</div>
        </div>
      )}
    </div>
  );
};

export default StatusChart; 