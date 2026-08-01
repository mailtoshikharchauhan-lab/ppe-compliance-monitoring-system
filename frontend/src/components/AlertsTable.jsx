import React, { useState } from 'react';
import { FaImage, FaExclamationTriangle } from 'react-icons/fa';
import apiService from '../services/api';
import ScreenshotModal from './ScreenshotModal';

const AlertsTable = ({ alerts }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState('');

  // Open modal with selected screenshot
  const handleImageClick = (screenshotPath) => {
    const imageUrl = apiService.getScreenshotUrl(screenshotPath);
    setSelectedImage(imageUrl);
    setModalOpen(true);
  };

  // Close modal
  const closeModal = () => {
    setModalOpen(false);
    setSelectedImage('');
  };

  // Get badge color based on violation type
  const getViolationBadge = (violation) => {
    const badges = {
      'No Helmet': 'bg-orange-100 text-orange-800',
      'No Vest': 'bg-yellow-100 text-yellow-800',
      'No Helmet + No Vest': 'bg-red-100 text-red-800',
    };
    return badges[violation] || 'bg-gray-100 text-gray-800';
  };

  if (alerts.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="text-center text-gray-500">
          <FaExclamationTriangle className="text-5xl mx-auto mb-3 text-gray-300" />
          <p className="text-lg font-medium">No alerts yet</p>
          <p className="text-sm mt-1">Upload and process a video to see violations</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">Alerts History</h2>
          <p className="text-sm text-gray-600 mt-1">
            {alerts.length} violation(s) detected
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Violation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Screenshot
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {alerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{alert.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {alert.timestamp}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${getViolationBadge(
                        alert.violation
                      )}`}
                    >
                      {alert.violation}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => handleImageClick(alert.screenshot)}
                      className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      <FaImage className="text-lg" />
                      <span className="text-sm font-medium">View</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Screenshot Modal */}
      <ScreenshotModal
        isOpen={modalOpen}
        imageUrl={selectedImage}
        onClose={closeModal}
      />
    </>
  );
};

export default AlertsTable;
