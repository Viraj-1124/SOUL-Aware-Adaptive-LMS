
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import { useAuth } from '../context/AuthContext';

import Login from '../pages/Login';
import Register from '../pages/Register';
import DashboardLayout from '../layouts/DashboardLayout';
import Courses from '../pages/Courses';
import CourseDetails from '../pages/CourseDetails';
import TopicDetails from '../pages/TopicDetails';
import Assignments from '../pages/Assignments';
import Attendance from '../pages/Attendance';

import Fatigue from '../pages/Fatigue';
import Predictions from '../pages/Predictions';
import Dashboard from '../pages/Dashboard';
import KnowledgeTracing from '../pages/KnowledgeTracing';
import Topics from '../pages/Topics';
import QuizMgmt from '../pages/QuizMgmt';
import StudentQuizzes from '../pages/StudentQuizzes';
import GoalAlignment from '../pages/GoalAlignment';


const RootRedirect = () => {
  const { user, isAuthenticated } = useAuth();
  if (!isAuthenticated || !user) return <Navigate to="/login" replace />;
  return <Navigate to={`/${user.role.toLowerCase()}/dashboard`} replace />;
};

const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RootRedirect />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes */}
        <Route element={<ProtectedRoute allowedRoles={['STUDENT']} />}>
          <Route path="/student/dashboard" element={<DashboardLayout><Dashboard /></DashboardLayout>} />
          <Route path="/student/courses" element={<DashboardLayout><Courses /></DashboardLayout>} />
          <Route path="/student/courses/:courseId" element={<DashboardLayout><CourseDetails /></DashboardLayout>} />
          <Route path="/student/topics/:topicId" element={<DashboardLayout><TopicDetails /></DashboardLayout>} />
          <Route path="/student/assignments" element={<DashboardLayout><Assignments /></DashboardLayout>} />
          <Route path="/student/quizzes" element={<DashboardLayout><StudentQuizzes /></DashboardLayout>} />
          <Route path="/student/attendance" element={<DashboardLayout><Attendance /></DashboardLayout>} />
          <Route path="/student/knowledge" element={<DashboardLayout><KnowledgeTracing /></DashboardLayout>} />
          <Route path="/student/goal-alignment" element={<DashboardLayout><GoalAlignment /></DashboardLayout>} />
        </Route>

        <Route element={<ProtectedRoute allowedRoles={['INSTRUCTOR']} />}>
          <Route path="/instructor/dashboard" element={<DashboardLayout><Dashboard /></DashboardLayout>} />
          <Route path="/instructor/courses" element={<DashboardLayout><Courses /></DashboardLayout>} />
          <Route path="/instructor/topics" element={<DashboardLayout><Topics /></DashboardLayout>} />
          <Route path="/instructor/quiz" element={<DashboardLayout><QuizMgmt /></DashboardLayout>} />
          <Route path="/instructor/courses/:courseId" element={<DashboardLayout><CourseDetails /></DashboardLayout>} />
          <Route path="/instructor/topics/:topicId" element={<DashboardLayout><TopicDetails /></DashboardLayout>} />
          <Route path="/instructor/assignments" element={<DashboardLayout><Assignments /></DashboardLayout>} />
          <Route path="/instructor/attendance" element={<DashboardLayout><Attendance /></DashboardLayout>} />
          <Route path="/instructor/predictions" element={<DashboardLayout><Predictions /></DashboardLayout>} />
          <Route path="/instructor/fatigue" element={<DashboardLayout><Fatigue /></DashboardLayout>} />
          <Route path="/instructor/knowledge" element={<DashboardLayout><KnowledgeTracing /></DashboardLayout>} />
          <Route path="/instructor/goal-alignment" element={<DashboardLayout><GoalAlignment /></DashboardLayout>} />
        </Route>

        <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
          <Route path="/admin/dashboard" element={<DashboardLayout><Dashboard /></DashboardLayout>} />
          <Route path="/admin/courses" element={<DashboardLayout><Courses /></DashboardLayout>} />
          <Route path="/admin/topics" element={<DashboardLayout><Topics /></DashboardLayout>} />
          <Route path="/admin/quiz" element={<DashboardLayout><QuizMgmt /></DashboardLayout>} />
          <Route path="/admin/courses/:courseId" element={<DashboardLayout><CourseDetails /></DashboardLayout>} />
          <Route path="/admin/topics/:topicId" element={<DashboardLayout><TopicDetails /></DashboardLayout>} />
          <Route path="/admin/assignments" element={<DashboardLayout><Assignments /></DashboardLayout>} />
          <Route path="/admin/attendance" element={<DashboardLayout><Attendance /></DashboardLayout>} />
          <Route path="/admin/predictions" element={<DashboardLayout><Predictions /></DashboardLayout>} />
          <Route path="/admin/fatigue" element={<DashboardLayout><Fatigue /></DashboardLayout>} />
          <Route path="/admin/knowledge" element={<DashboardLayout><KnowledgeTracing /></DashboardLayout>} />
          <Route path="/admin/goal-alignment" element={<DashboardLayout><GoalAlignment /></DashboardLayout>} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;
