import React, { useState } from 'react';
import { FaUpload, FaPlay, FaCheckCircle } from 'react-icons/fa';
import apiService from '../services/api';
import Loader from './Loader';

const UploadCard = ({ onProcessComplete }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [message, setMessage] = useState('');

  // Handle file selection
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setUploadSuccess(false);
      setMessage('');
      setUploadedFileName('');
    }
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage('Please select a video file first');
      return;
    }

    setIsUploading(true);
    setMessage('');

    try {
      const response = await apiService.uploadVideo(selectedFile);
      setUploadedFileName(response.file_name);
      setUploadSuccess(true);
      setMessage(response.message);
    } catch (error) {
      setMessage('Upload failed. Please try again.');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  // Handle video processing
  const handleProcess = async () => {
    if (!uploadedFileName) {
      setMessage('Please upload a video first');
      return;
    }

    setIsProcessing(true);
    setMessage('Processing video... This may take a few minutes.');

    try {
      const result = await apiService.processVideo(uploadedFileName);
      setMessage(`Processing complete! ${result.alerts_count} alert(s) detected.`);
      
      // Notify parent component to refresh alerts
      if (onProcessComplete) {
        onProcessComplete();
      }
      
      // Reset form
      setTimeout(() => {
        setSelectedFile(null);
        setUploadedFileName('');
        setUploadSuccess(false);
        setMessage('');
      }, 3000);
    } catch (error) {
      setMessage('Processing failed. Please try again.');
      console.error('Processing error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Video</h2>

      {/* File Input */}
      <div className="space-y-4">
        <div>
          <label
            htmlFor="video-upload"
            className="flex items-center justify-center w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors"
          >
            <FaUpload className="text-gray-400 mr-2" />
            <span className="text-gray-600">
              {selectedFile ? selectedFile.name : 'Choose video file'}
            </span>
          </label>
          <input
            id="video-upload"
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
            disabled={isUploading || isProcessing}
          />
        </div>

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!selectedFile || isUploading || isProcessing || uploadSuccess}
          className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
        >
          {isUploading ? (
            <Loader message="" />
          ) : uploadSuccess ? (
            <>
              <FaCheckCircle className="mr-2" />
              Uploaded
            </>
          ) : (
            <>
              <FaUpload className="mr-2" />
              Upload Video
            </>
          )}
        </button>

        {/* Process Button */}
        <button
          onClick={handleProcess}
          disabled={!uploadSuccess || isProcessing}
          className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
        >
          {isProcessing ? (
            <Loader message="" />
          ) : (
            <>
              <FaPlay className="mr-2" />
              Process Video
            </>
          )}
        </button>

        {/* Status Message */}
        {message && (
          <div
            className={`p-3 rounded-lg text-sm ${
              message.includes('failed') || message.includes('Please')
                ? 'bg-red-100 text-red-700'
                : message.includes('complete')
                ? 'bg-green-100 text-green-700'
                : 'bg-blue-100 text-blue-700'
            }`}
          >
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadCard;
