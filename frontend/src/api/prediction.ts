import apiClient from './apiClient';

export const predictionApi = {
  predictBurnout: async (studentId: number, courseId: number) => {
    const response = await apiClient.post(`/prediction/predict/${studentId}/${courseId}`);
    return response.data;
  },
  runForAllStudents: async () => {
    const response = await apiClient.get('/prediction/run-for-all-students');
    return response.data;
  },
};
