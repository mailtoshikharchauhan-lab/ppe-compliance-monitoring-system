import React, { useState, useEffect } from 'react';
import UploadCard from '../components/UploadCard';
import StatsCards from '../components/StatsCards';
import AlertsTable from '../components/AlertsTable';
import apiService from '../services/api';

const Dashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch alerts on component mount
  useEffect(() => {
    fetchAlerts();
  }, []);

  // Fetch alerts from backend
  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const alertsData = await apiService.getAlerts();
      // Sort alerts by ID descending (newest first)
      const sortedAlerts = alertsData.sort((a, b) => b.id - a.id);
      setAlerts(sortedAlerts);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Callback when video processing is complete
  const handleProcessComplete = () => {
    fetchAlerts();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-600 mt-1">
            Upload videos and monitor PPE compliance violations
          </p>
        </div>

        {/* Upload Section */}
        <div className="mb-8">
          <UploadCard onProcessComplete={handleProcessComplete} />
        </div>

        {/* Statistics Cards */}
        <div className="mb-8">
          <StatsCards alerts={alerts} />
        </div>

        {/* Alerts Table */}
        <div>
          {isLoading ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading alerts...</p>
            </div>
          ) : (
            <AlertsTable alerts={alerts} />
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
