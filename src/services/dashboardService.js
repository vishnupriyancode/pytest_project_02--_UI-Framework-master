import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000'; // Replace with your API URL

// Get dashboard summary data
export const getDashboardSummary = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/dashboard/summary`);
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard summary:', error);
    // Return mock data for development
    return {
      totalRequests: 157,
      statusBreakdown: {
        success: 132,
        failed: 18,
        pending: 7
      },
      recentActivity: {
        today: 12,
        thisWeek: 47,
        thisMonth: 128
      }
    };
  }
};

// Get requests timeline data
export const getRequestsTimeline = async (period = 'week') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/dashboard/timeline?period=${period}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching timeline data:', error);
    // Return mock data for development
    const mockData = [];
    const today = new Date();
    
    if (period === 'week') {
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        mockData.push({
          date: date.toISOString().split('T')[0],
          success: Math.floor(Math.random() * 15) + 5,
          failed: Math.floor(Math.random() * 5)
        });
      }
    } else if (period === 'month') {
      for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        mockData.push({
          date: date.toISOString().split('T')[0],
          success: Math.floor(Math.random() * 15) + 5,
          failed: Math.floor(Math.random() * 5)
        });
      }
    }
    
    return mockData;
  }
};

// Get API response details
export const getApiResponseDetails = async (filters = {}) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/dashboard/responses`, { params: filters });
    return response.data;
  } catch (error) {
    console.error('Error fetching API response details:', error);
    // Return mock data for development
    let mockData = [];
    const today = new Date();
    const domains = ['api.example.com', 'dev.example.org', 'test.api.local'];
    
    for (let i = 0; i < 20; i++) {
      const date = new Date(today);
      date.setHours(date.getHours() - Math.floor(Math.random() * 48));
      
      const processingTime = Math.floor(Math.random() * 1500) + 200;
      const status = Math.random() > 0.15 ? 'Success' : 'Failed';
      const domain = domains[i % domains.length];
      
      mockData.push({
        id: `ED${100000 + i}`,
        fileName: `sample_data_${i + 1}.json`,
        timestamp: date.toISOString(),
        processingTime: processingTime,
        status: status,
        domain: domain,
        responseSize: Math.floor(Math.random() * 500) + 100,
        notes: i % 5 === 0 ? ['Needs review', 'Contains custom fields'] : []
      });
    }
    
    // Apply filters to mock data
    if (filters) {
      if (filters.status && filters.status !== 'all') {
        mockData = mockData.filter(item => 
          item.status.toLowerCase() === filters.status.toLowerCase()
        );
      }
      
      if (filters.dateRange && filters.dateRange !== 'all') {
        const now = new Date();
        let cutoffDate = new Date();
        
        if (filters.dateRange === 'today') {
          cutoffDate.setHours(0, 0, 0, 0);
        } else if (filters.dateRange === 'week') {
          cutoffDate.setDate(now.getDate() - 7);
        } else if (filters.dateRange === 'month') {
          cutoffDate.setMonth(now.getMonth() - 1);
        }
        
        mockData = mockData.filter(item => new Date(item.timestamp) >= cutoffDate);
      }
      
      if (filters.domain && filters.domain !== 'all') {
        mockData = mockData.filter(item => item.domain === filters.domain);
      }
      
      if (filters.search) {
        const searchTerm = filters.search.toLowerCase();
        mockData = mockData.filter(item => 
          item.id.toLowerCase().includes(searchTerm) || 
          item.fileName.toLowerCase().includes(searchTerm) ||
          item.domain.toLowerCase().includes(searchTerm)
        );
      }
    }
    
    return mockData;
  }
};

// Get chat history for an edit ID
export const getChatHistory = async (editId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/dashboard/chat/${editId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching chat history for ${editId}:`, error);
    // Return mock data for development
    return [
      {
        id: 1,
        timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
        user: 'John Doe',
        message: `Initial processing of ${editId} completed with warnings.`
      },
      {
        id: 2,
        timestamp: new Date(Date.now() - 43200000).toISOString(), // 12 hours ago
        user: 'Jane Smith',
        message: 'Fixed JSON structure issues in the file.'
      },
      {
        id: 3,
        timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
        user: 'John Doe',
        message: 'Reprocessed file successfully, all issues resolved.'
      }
    ];
  }
};

// Add a new chat message
export const addChatMessage = async (editId, message) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/dashboard/chat/${editId}`, {
      message
    });
    return response.data;
  } catch (error) {
    console.error(`Error adding chat message for ${editId}:`, error);
    throw error;
  }
};