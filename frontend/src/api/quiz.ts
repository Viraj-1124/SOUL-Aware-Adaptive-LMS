import apiClient from './apiClient';

export const quizApi = {
  getQuestions: async (topicId: number) => {
    const response = await apiClient.get(`/quiz/topic/${topicId}`);
    return response.data;
  },
  addQuestion: async (data: any) => {
    const response = await apiClient.post('/quiz/question', data);
    return response.data;
  },
  submitQuiz: async (data: { topic_id: number; answers: any; time_spent: number }) => {
    const response = await apiClient.post('/quiz/submit', data);
    return response.data;
  },
};
