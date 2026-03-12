import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { coursesApi } from '../api/courses';
import { CheckSquare, BookOpen } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const StudentQuizzes = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // For students, this ideally fetches their enrolled courses. 
    // Using the generic getCourses for MVP functionality
    coursesApi.getCourses().then(data => {
      setCourses(data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10 w-full">
      <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-purple-200 flex items-center gap-3">
        <CheckSquare className="h-8 w-8 text-purple-400" />
        Available Quizzes
      </h1>
      <p className="text-gray-400">Select a course to view and take active quizzes for your learning modules.</p>
      
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
          {courses.map(course => (
            <Link to={`/${user?.role.toLowerCase()}/courses/${course.id}`} key={course.id} className="glass-card p-6 hover:-translate-y-1 transition-transform border-t-4 border-t-purple-500">
              <BookOpen className="h-8 w-8 text-purple-400 mb-4" />
              <h3 className="text-xl font-bold text-white">{course.title}</h3>
              <p className="text-gray-400 mt-2 text-sm">Open course to view quiz modules &rarr;</p>
            </Link>
          ))}
          {courses.length === 0 && !loading && (
             <div className="col-span-full p-8 text-center text-gray-500 glass-card">
               You are not enrolled in any courses with active quizzes.
             </div>
          )}
        </div>
      )}
    </div>
  );
};
export default StudentQuizzes;
