import apiClient from './apiClient';

export const fatigueApi = {
  getFatigueMonitor: async (studentId: number, courseId: number) => {
    const response = await apiClient.post(`/fatigue/${studentId}/${courseId}`);
    return response.data;
  },
};
