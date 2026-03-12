import apiClient from './apiClient';

export interface ActivityPayload {
  course_id: number;
  activity_type: string;
  duration_seconds: number;
}

export const activityApi = {
  logActivity: async (data: ActivityPayload) => {
    const response = await apiClient.post('/activity/log', data);
    return response.data;
  },
};
