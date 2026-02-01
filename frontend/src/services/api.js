import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get resilience and price prediction for a postcode
 * @param {string} postcode - UK Postcode
 * @returns {Promise} API response with resilience data
 */
export const predictResilience = async (postcode) => {
  try {
    const response = await api.post('/api/predict_resilience', {
      postcode: postcode
    });
    return response.data;
  } catch (error) {
    console.error('Error predicting resilience:', error);
    throw error;
  }
};

/**
 * Health check for the API
 * @returns {Promise} API health status
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('API health check failed:', error);
    throw error;
  }
};

export default api;
