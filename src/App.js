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
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [processingStatus, setProcessingStatus] = useState({ loading: false, message: '', error: false });

  // Automatically process JSON files on application startup
  useEffect(() => {
    const autoProcessJsons = async () => {
      try {
        setProcessingStatus({ loading: true, message: 'Processing JSON files...', error: false });
        const result = await processAllJsons();
        if (result && result.processedCount > 0) {
          setProcessingStatus({ 
            loading: false, 
            message: `Successfully processed ${result.processedCount} JSON files. Excel report generated.`,
            error: false
          });
          // Clear success message after 5 seconds
          setTimeout(() => {
            setProcessingStatus({ loading: false, message: '', error: false });
          }, 5000);
        } else {
          // If no files were processed, don't show any message
          setProcessingStatus({ loading: false, message: '', error: false });
        }
      } catch (error) {
        console.error('Auto-processing error:', error);
        // Don't show error message to user, just log to console
        setProcessingStatus({ loading: false, message: '', error: true });
      }
    };

    autoProcessJsons();
  }, []);

  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'creation', label: 'Creation' },
    { id: 'processed', label: 'Run JSONs' },
    { id: 'request', label: 'Request' },
    { id: 'responses', label: 'API Responses' }
  ];

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Header />
        <div className="container mx-auto py-6 px-4">
          {processingStatus.message && !processingStatus.error && (
            <div className={`mb-4 p-4 rounded-md ${
              processingStatus.loading 
                ? 'bg-blue-100 text-blue-700' 
                : 'bg-green-100 text-green-700'
            }`}>
              {processingStatus.message}
            </div>
          )}

          <Routes>
            <Route path="/case-creation" element={<CaseCreation />} />
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
        <NetworkStatusIndicator />
      </div>
    </Router>
  );
}

export default App; 