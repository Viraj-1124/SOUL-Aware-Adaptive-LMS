import apiClient from './apiClient';

export const attendanceApi = {
  markAttendance: async (data: { student_id: number; course_id: number; date: string; present: boolean }) => {
    const response = await apiClient.post('/attendance/mark', data);
    return response.data;
  },
  getStudentAttendance: async (studentId: number) => {
    const response = await apiClient.get(`/attendance/student/${studentId}`);
    return response.data;
  },
  getAttendanceRate: async (studentId: number, courseId: number) => {
    const response = await apiClient.get(`/attendance/rate/${studentId}/${courseId}`);
    return response.data;
  },
};
