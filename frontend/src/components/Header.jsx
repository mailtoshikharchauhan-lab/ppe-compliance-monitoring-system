import React, { useState, useEffect } from 'react';
import { FaCheckCircle, FaTimesCircle } from 'react-icons/fa';
import apiService from '../services/api';

const Header = () => {
  const [backendStatus, setBackendStatus] = useState({ connected: false, message: '' });

  useEffect(() => {
    // Check backend status on component mount
    checkStatus();
    
    // Check status every 30 seconds
    const interval = setInterval(checkStatus, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    const status = await apiService.checkBackendStatus();
    setBackendStatus(status);
  };

  return (
    <header className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex justify-between items-center">
          {/* Title */}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              PPE Compliance Monitoring System
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Real-time Personal Protective Equipment Detection
            </p>
          </div>

          {/* Backend Status */}
          <div className="flex items-center space-x-2">
            {backendStatus.connected ? (
              <>
                <FaCheckCircle className="text-green-500 text-xl" />
                <span className="text-sm font-medium text-green-600">
                  Backend Connected
                </span>
              </>
            ) : (
              <>
                <FaTimesCircle className="text-red-500 text-xl" />
                <span className="text-sm font-medium text-red-600">
                  Backend Disconnected
                </span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
