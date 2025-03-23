import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import RequestTab from './components/RequestTab';
import DataTable from './components/DataTable';
import ProcessedJsons from './components/ProcessedJsons';
import DashboardTab from './components/DashboardTab';
import TabNavigation from './components/TabNavigation';
import NetworkStatusIndicator from './components/common/NetworkStatusIndicator';
import { processAllJsons } from './services/apiService';
import CreationTab from './components/CreationTab';
import CaseCreation from './components/CaseCreation';
import { configureToasts } from './utils/downloadHelper';
import './index.css';

// Global configuration
const APP_CONFIG = {
  showProcessingStatus: false,
  showNetworkStatus: false,
  showToasts: false
};

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [processingStatus, setProcessingStatus] = useState({ loading: false, message: '' });

  // Configure toast notifications
  useEffect(() => {
    configureToasts({ enabled: APP_CONFIG.showToasts });
  }, []);

  // Automatically process JSON files on application startup
  useEffect(() => {
    const autoProcessJsons = async () => {
      try {
        if (APP_CONFIG.showProcessingStatus) {
          setProcessingStatus({ loading: true, message: 'Processing JSON files...' });
        }
        const result = await processAllJsons();
        if (APP_CONFIG.showProcessingStatus) {
          setProcessingStatus({ 
            loading: false, 
            message: `Successfully processed ${result.processedCount} JSON files. Excel report generated.` 
          });
        }
      } catch (error) {
        console.error('Auto-processing error:', error);
        if (APP_CONFIG.showProcessingStatus) {
          setProcessingStatus({ 
            loading: false, 
            message: 'Error processing JSON files. See console for details.' 
          });
        }
      }
    };

    autoProcessJsons();
  }, []);

  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'request', label: 'Request' },
    { id: 'responses', label: 'Responses' },
    { id: 'processed', label: 'Processed' },
    { id: 'creation', label: 'Creation' }
  ];

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Header />
        <div className="container mx-auto py-6 px-4">
          {APP_CONFIG.showProcessingStatus && processingStatus.message && (
            <div className={`mb-4 p-4 rounded-md ${processingStatus.loading ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}`}>
              {processingStatus.message}
            </div>
          )}

          <Routes>
            <Route path="/case-creation" element={<CaseCreation />} />
            <Route path="/json-creation" element={<div className="p-6 bg-white rounded-lg shadow-md"><h1 className="text-2xl font-bold mb-4">JSON Creation</h1><p>Create and edit JSON files here.</p></div>} />
            <Route path="/file-comparison" element={<div className="p-6 bg-white rounded-lg shadow-md"><h1 className="text-2xl font-bold mb-4">File Comparison</h1><p>Compare files here.</p></div>} />
            <Route path="/" element={
              <>
                <TabNavigation tabs={tabs} activeTab={activeTab} setActiveTab={setActiveTab} />
                {activeTab === 'dashboard' && <DashboardTab />}
                {activeTab === 'request' && <RequestTab />}
                {activeTab === 'responses' && <DataTable />}
                {activeTab === 'processed' && <ProcessedJsons />}
                {activeTab === 'creation' && <CreationTab />}
              </>
            } />
          </Routes>
        </div>
        {APP_CONFIG.showNetworkStatus && <NetworkStatusIndicator />}
      </div>
    </Router>
  );
}

export default App; 