import apiClient from './apiClient';

export const topicsApi = {
  getTopics: async (courseId: number) => {
    const response = await apiClient.get(`/topics/course/${courseId}`);
    return response.data;
  },
  createTopic: async (data: { title: string; course_id: number }) => {
    const response = await apiClient.post('/topics/', data);
    return response.data;
  },
};
