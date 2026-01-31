import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get property price prediction for a location
 * @param {Object} location - Location object with address, lat, lng
 * @returns {Promise} API response with prediction data
 */
export const getPrediction = async (location) => {
  try {
    const response = await api.post('/api/predict', {
      address: location.address,
      lat: location.lat,
      lng: location.lng,
    });
    return response.data;
  } catch (error) {
    console.error('Error getting prediction:', error);
    throw error;
  }
};

/**
 * Get area data for a specific location
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @returns {Promise} API response with area data
 */
export const getAreaData = async (lat, lng) => {
  try {
    const response = await api.get('/api/area-data', {
      params: { lat, lng },
    });
    return response.data;
  } catch (error) {
    console.error('Error getting area data:', error);
    throw error;
  }
};

/**
 * Health check for the API
 * @returns {Promise} API health status
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/api/health');
    return response.data;
  } catch (error) {
    console.error('API health check failed:', error);
    throw error;
  }
};

export default api;
