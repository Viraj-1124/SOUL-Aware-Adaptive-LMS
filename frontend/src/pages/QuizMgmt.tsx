import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { coursesApi } from '../api/courses';
import { CheckSquare } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const QuizMgmt = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState<any[]>([]);

  useEffect(() => {
    coursesApi.getCourses().then(setCourses).catch(console.error);
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10 w-full">
      <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-purple-200">Quiz Management</h1>
      <p className="text-gray-400">Select a course to drill down into its Topics and manage Quizzes.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
        {courses.map(course => (
          <Link to={`/${user?.role.toLowerCase()}/courses/${course.id}`} key={course.id} className="glass-card p-6 hover:-translate-y-1 transition-transform border-t-4 border-t-purple-500">
            <CheckSquare className="h-8 w-8 text-purple-400 mb-4" />
            <h3 className="text-xl font-bold text-white">{course.title}</h3>
            <p className="text-gray-400 mt-2 text-sm">Navigate inside to edit Question Banks</p>
          </Link>
        ))}
      </div>
    </div>
  );
};
export default QuizMgmt;
