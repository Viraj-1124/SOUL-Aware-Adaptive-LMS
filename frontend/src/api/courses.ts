import apiClient from './apiClient';

export const coursesApi = {
  getCourses: async () => {
    const response = await apiClient.get('/courses/');
    return response.data;
  },
  createCourse: async (data: { title: string; description: string }) => {
    const response = await apiClient.post('/courses/', data);
    return response.data;
  },
};
