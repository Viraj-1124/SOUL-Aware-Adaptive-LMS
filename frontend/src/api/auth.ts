import apiClient from './apiClient';

export const authApi = {
  login: async (formData: FormData) => {
    const response = await apiClient.post('/users/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  register: async (data: any) => {
    const response = await apiClient.post('/users/register', data);
    return response.data;
  },
};
