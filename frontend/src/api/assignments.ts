import apiClient from './apiClient';

export const assignmentsApi = {
  createAssignment: async (data: { course_id: number; title: string; description: string; due_date: string }) => {
    const response = await apiClient.post('/assignments/', data);
    return response.data;
  },
  submitAssignment: async (data: { assignment_id: number; submission_text: string; reflection_text: string }) => {
    const response = await apiClient.post('/assignments/submit', data);
    return response.data;
  },
};
