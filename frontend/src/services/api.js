import axios from 'axios';

// Base URL for the backend API
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service methods
export const apiService = {
  /**
   * Check if backend is running
   */
  checkBackendStatus: async () => {
    try {
      const response = await api.get('/');
      return { connected: true, message: response.data.message };
    } catch (error) {
      return { connected: false, message: 'Backend not connected' };
    }
  },

  /**
   * Upload video file
   * @param {File} file - Video file to upload
   */
  uploadVideo: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Process uploaded video
   * @param {string} fileName - Name of the uploaded file
   */
  processVideo: async (fileName) => {
    const response = await api.post('/process', null, {
      params: { file_name: fileName },
    });
    return response.data;
  },

  /**
   * Get all alerts from database
   */
  getAlerts: async () => {
    const response = await api.get('/alerts');
    return response.data.alerts;
  },

  /**
   * Get screenshot URL
   * @param {string} screenshotPath - Path to screenshot (just filename)
   */
  getScreenshotUrl: (screenshotPath) => {
    // If path already includes 'screenshots/', use as is
    if (screenshotPath.startsWith('screenshots/')) {
      return `${API_BASE_URL}/${screenshotPath}`;
    }
    // Otherwise, add 'screenshots/' prefix
    return `${API_BASE_URL}/screenshots/${screenshotPath}`;
  },
};

export default apiService;
