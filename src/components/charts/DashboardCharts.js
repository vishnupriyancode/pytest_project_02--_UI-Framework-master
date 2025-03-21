import React from 'react';
import { 
  PieChart, Pie, Cell,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

const pieData = [
  { name: 'Success', value: 84 },
  { name: 'Failed', value: 11 },
  { name: 'Pending', value: 5 }
];

const barData = [
  { date: 'Mar 15', Success: 10, Failed: 1 },
  { date: 'Mar 16', Success: 5, Failed: 2 },
  { date: 'Mar 17', Success: 15, Failed: 4 },
  { date: 'Mar 18', Success: 10, Failed: 3 },
  { date: 'Mar 19', Success: 12, Failed: 1 },
  { date: 'Mar 20', Success: 16, Failed: 1 },
  { date: 'Mar 21', Success: 18, Failed: 3 }
];

// Updated color scheme with professional gray and silver combinations
const PIE_COLORS = {
  Success: '#4A4A4A', // Dark Gray
  Failed: '#808080',  // Medium Gray
  Pending: '#C0C0C0'  // Silver
};

const BAR_COLORS = {
  Success: '#2C3E50', // Dark Slate Gray
  Failed: '#95A5A6'   // Light Gray
};

export const DashboardCharts = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Pie Chart */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Status Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={PIE_COLORS[entry.name]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Bar Chart */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Daily Status Breakdown</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="Success" fill={BAR_COLORS.Success} />
            <Bar dataKey="Failed" fill={BAR_COLORS.Failed} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default DashboardCharts; 