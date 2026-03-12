import { useState, useEffect } from 'react';
import { coursesApi } from '../api/courses';
import { useAuth } from '../context/AuthContext';
import { BookOpen, Plus } from 'lucide-react';
import { Link } from 'react-router-dom';

const Courses = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // For instructor to create course
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const data = await coursesApi.getCourses();
      setCourses(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await coursesApi.createCourse({ title, description });
      setTitle('');
      setDescription('');
      setShowCreate(false);
      fetchCourses();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200">Courses</h1>
          <p className="text-gray-400 mt-1">Explore your learning modules</p>
        </div>
        {(user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && (
          <button onClick={() => setShowCreate(!showCreate)} className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Create Course
          </button>
        )}
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="glass-card p-6 mb-8 max-w-2xl animate-fade-in">
          <h2 className="text-xl font-semibold mb-4 text-white">New Course</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Title</label>
              <input type="text" className="input-field" value={title} onChange={e => setTitle(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">Description</label>
              <textarea className="input-field h-24" value={description} onChange={e => setDescription(e.target.value)} required />
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 hover:bg-white/5 text-gray-300 rounded-lg transition-colors">Cancel</button>
              <button type="submit" className="btn-primary">Create</button>
            </div>
          </div>
        </form>
      )}

      {loading ? (
        <div className="animate-pulse grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1,2,3,4].map(i => <div key={i} className="glass-card h-48 bg-dark-card/50"></div>)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {courses.map(course => (
            <Link to={`/${user?.role.toLowerCase()}/courses/${course.id}`} key={course.id} className="block glass-card group hover:-translate-y-1 transition-transform duration-300 p-6 flex flex-col cursor-pointer border-t-2 border-t-transparent hover:border-t-primary-500 hover:shadow-primary-500/10 z-10">
              <div className="p-3 bg-primary-500/10 w-fit rounded-lg mb-4 text-primary-400 transition-colors group-hover:bg-primary-500/20">
                <BookOpen className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{course.title}</h3>
              <p className="text-sm text-gray-400 line-clamp-3 mb-4 flex-1">{course.description}</p>
              <div className="text-primary-400 text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all">
                View Details <span aria-hidden="true">&rarr;</span>
              </div>
            </Link>
          ))}
          {courses.length === 0 && (
            <div className="col-span-full py-16 flex flex-col items-center justify-center text-gray-500 border border-dashed border-dark-border rounded-xl">
              <BookOpen className="h-12 w-12 text-dark-border mb-3" />
              <p>No courses available yet.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Courses;
