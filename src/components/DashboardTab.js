import React, { useState, useEffect } from 'react';
import { 
  getDashboardSummary, 
  getRequestsTimeline, 
  getApiResponseDetails 
} from '../services/dashboardService';
import SummaryCards from './dashboard/SummaryCards';
import StatusChart from './dashboard/StatusChart';
import TimelineChart from './dashboard/TimelineChart';
import ResponseTable from './dashboard/ResponseTable';
import ChatPanel from './dashboard/ChatPanel';
import DashboardOverview from './dashboard/DashboardOverview';
import { STATUS_COLORS, UI_COLORS } from '../theme/colorScheme';

const DashboardTab = () => {
  const [summaryData, setSummaryData] = useState(null);
  const [timelineData, setTimelineData] = useState([]);
  const [responseData, setResponseData] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [loading, setLoading] = useState(true);
  const [selectedEditId, setSelectedEditId] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' or 'details'
  const [filters, setFilters] = useState({
    dateRange: 'all',
    status: 'all',
    domain: 'all',
    search: ''
  });
  const [availableDomains, setAvailableDomains] = useState(['all', 'api.example.com', 'dev.example.org', 'test.api.local']);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // Fetch all data in parallel
        const [summary, timeline, responses] = await Promise.all([
          getDashboardSummary(),
          getRequestsTimeline(selectedPeriod),
          getApiResponseDetails(filters)
        ]);
        
        setSummaryData(summary);
        setTimelineData(timeline);
        setResponseData(responses);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
      setLoading(false);
    };

    fetchDashboardData();
  }, [selectedPeriod, filters]);

  // Extract unique domains from response data
  useEffect(() => {
    if (responseData && responseData.length > 0) {
      const domains = ['all', ...new Set(responseData.map(item => item.domain))];
      setAvailableDomains(domains);
    }
  }, [responseData]);

  // Handle search input including domain detection
  const handleSearchInput = (searchTerm) => {
    // Check if the search term looks like a domain
    const isDomainPattern = /^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;
    
    if (isDomainPattern.test(searchTerm)) {
      // If the search term is a domain, set both domain and search filters
      // Check if this domain exists in our available domains
      const matchedDomain = availableDomains.find(d => 
        d !== 'all' && searchTerm.includes(d)
      );
      
      if (matchedDomain) {
        setFilters(prev => ({ 
          ...prev, 
          domain: matchedDomain,
          search: searchTerm 
        }));
      } else {
        // Just set the search term, as we don't have this domain in our filter list
        setFilters(prev => ({ ...prev, search: searchTerm }));
      }
    } else {
      // For non-domain searches, just update the search filter
      setFilters(prev => ({ ...prev, search: searchTerm }));
    }
  };

  const handlePeriodChange = (period) => {
    setSelectedPeriod(period);
  };

  const handleFilterChange = (newFilters) => {
    // Special handling for search field to detect domain patterns
    if ('search' in newFilters) {
      handleSearchInput(newFilters.search);
    } else {
      setFilters({ ...filters, ...newFilters });
    }
  };

  const handleRowClick = (editId) => {
    setSelectedEditId(editId);
  };

  if (loading && !summaryData) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
      </div>
    );
  }

  return (
    <div className="bg-ui-background min-h-screen pb-8">
      {/* Dashboard Navigation Tabs */}
      <div className="bg-white border-b border-ui-border mb-6">
        <div className="container mx-auto px-4">
          <div className="flex space-x-6">
            <button
              className={`py-4 px-2 relative ${
                activeTab === 'overview'
                  ? 'text-brand-primary font-medium'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
              {activeTab === 'overview' && (
                <div className="absolute bottom-0 left-0 w-full h-0.5 bg-brand-primary"></div>
              )}
            </button>
            <button
              className={`py-4 px-2 relative ${
                activeTab === 'details'
                  ? 'text-brand-primary font-medium'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab('details')}
            >
              Detailed Analysis
              {activeTab === 'details' && (
                <div className="absolute bottom-0 left-0 w-full h-0.5 bg-brand-primary"></div>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4">
        {activeTab === 'overview' ? (
          <DashboardOverview />
        ) : (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <SummaryCards data={summaryData} />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-5 rounded-card shadow-card border border-ui-border">
                <StatusChart data={summaryData?.statusBreakdown} />
              </div>
              
              <div className="bg-white p-5 rounded-card shadow-card border border-ui-border">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-bold">Request Timeline</h3>
                  <div className="flex space-x-2">
                    <button 
                      onClick={() => handlePeriodChange('week')}
                      className={`px-3 py-1 text-sm rounded-button ${
                        selectedPeriod === 'week' 
                          ? 'bg-brand-accent text-white' 
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      Week
                    </button>
                    <button 
                      onClick={() => handlePeriodChange('month')}
                      className={`px-3 py-1 text-sm rounded-button ${
                        selectedPeriod === 'month' 
                          ? 'bg-brand-accent text-white' 
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      Month
                    </button>
                  </div>
                </div>
                <TimelineChart data={timelineData} />
              </div>
            </div>

            {/* Response Table and Chat Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 bg-white p-5 rounded-card shadow-card border border-ui-border">
                <h3 className="text-xl font-bold mb-4">API Response Analysis</h3>
                <div className="mb-4 flex flex-wrap gap-2">
                  <select 
                    className="px-3 py-2 border border-ui-border rounded-button focus:outline-none focus:ring-2 focus:ring-brand-accent"
                    value={filters.dateRange}
                    onChange={(e) => handleFilterChange({ dateRange: e.target.value })}
                  >
                    <option value="all">All Time</option>
                    <option value="today">Today</option>
                    <option value="week">This Week</option>
                    <option value="month">This Month</option>
                  </select>
                  
                  <select 
                    className="px-3 py-2 border border-ui-border rounded-button focus:outline-none focus:ring-2 focus:ring-brand-accent"
                    value={filters.status}
                    onChange={(e) => handleFilterChange({ status: e.target.value })}
                  >
                    <option value="all">All Status</option>
                    <option value="success">Success</option>
                    <option value="failed">Failed</option>
                    <option value="pending">Pending</option>
                  </select>
                  
                  <select 
                    className="px-3 py-2 border border-ui-border rounded-button focus:outline-none focus:ring-2 focus:ring-brand-accent"
                    value={filters.domain}
                    onChange={(e) => handleFilterChange({ domain: e.target.value })}
                  >
                    {availableDomains.map(domain => (
                      <option key={domain} value={domain}>
                        {domain === 'all' ? 'All Domains' : domain}
                      </option>
                    ))}
                  </select>
                  
                  <div className="relative flex-grow">
                    <input 
                      type="text" 
                      placeholder="Search by ID or filename" 
                      value={filters.search}
                      className={`px-3 py-2 border rounded-button w-full focus:outline-none focus:ring-2 focus:ring-brand-accent ${
                        filters.domain !== 'all' && filters.search.includes(filters.domain) 
                          ? 'border-indigo-300 bg-indigo-50' 
                          : 'border-ui-border'
                      }`}
                      onChange={(e) => handleFilterChange({ search: e.target.value })}
                    />
                    {filters.domain !== 'all' && filters.search.includes(filters.domain) && (
                      <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-indigo-500 bg-indigo-100 px-1.5 py-0.5 rounded">
                        Domain detected
                      </div>
                    )}
                  </div>
                </div>
                
                <ResponseTable 
                  data={responseData} 
                  onRowClick={handleRowClick} 
                  selectedEditId={selectedEditId}
                />
              </div>
              
              <div className="bg-white p-5 rounded-card shadow-card border border-ui-border">
                <h3 className="text-xl font-bold mb-4">Chat & Notes</h3>
                {selectedEditId ? (
                  <ChatPanel editId={selectedEditId} />
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    Select a request to view and add notes
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardTab; 