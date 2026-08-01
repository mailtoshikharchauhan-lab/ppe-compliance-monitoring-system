import React from 'react';

const Loader = ({ message = 'Processing...' }) => {
  return (
    <div className="flex flex-col items-center justify-center space-y-3">
      {/* Spinner */}
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      
      {/* Message */}
      <p className="text-gray-600 font-medium">{message}</p>
    </div>
  );
};

export default Loader;
