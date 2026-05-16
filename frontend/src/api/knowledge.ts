import axios from 'axios';

// Assuming base URL matches the rest of the application
const API_URL = 'http://localhost:8000';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    headers: {
      Authorization: `Bearer ${token}`
    }
  };
};

export const knowledgeApi = {
  getKnowledgeState: async (studentId: number) => {
    const response = await axios.get(`${API_URL}/knowledge/state/${studentId}`, getAuthHeaders());
    return response.data;
  },

  getPrediction: async (studentId: number) => {
    const response = await axios.get(`${API_URL}/knowledge/predict/${studentId}`, getAuthHeaders());
    return response.data;
  },

  getRecommendation: async (studentId: number, topicId: number) => {
    const response = await axios.get(`${API_URL}/knowledge/recommendation/${studentId}/${topicId}`, getAuthHeaders());
    return response.data;
  }
};
