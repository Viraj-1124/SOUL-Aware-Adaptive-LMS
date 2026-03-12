import apiClient from './apiClient';

export const healthApi = {
  getLearningHealth: async (studentId: number, courseId: number) => {
    const response = await apiClient.post(`/learning-health/${studentId}/${courseId}`);
    return response.data;
  },
};
