import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { topicsApi } from '../api/topics';
import { useAuth } from '../context/AuthContext';
import { Layers, Plus, ChevronLeft } from 'lucide-react';

const CourseDetails = () => {
  const { courseId } = useParams();
  const { user } = useAuth();
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // For instructor to create topic
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');

  const fetchTopics = async () => {
    try {
      setLoading(true);
      if (courseId) {
        const data = await topicsApi.getTopics(Number(courseId));
        setTopics(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopics();
  }, [courseId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (courseId) {
        await topicsApi.createTopic({ title, course_id: Number(courseId) });
        setTitle('');
        setShowCreate(false);
        fetchTopics();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const backLink = `/${user?.role.toLowerCase()}/courses`;

  return (
    <div>
      <div className="mb-6 flex items-center gap-4">
        <Link to={backLink} className="p-2 bg-dark-card hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-colors">
          <ChevronLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200">Course Topics</h1>
          <p className="text-gray-400 mt-1">Modules within this course</p>
        </div>
      </div>

      <div className="flex justify-end mb-8">
        {(user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && (
          <button onClick={() => setShowCreate(!showCreate)} className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Topic
          </button>
        )}
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="glass-card p-6 mb-8 max-w-2xl animate-fade-in">
          <h2 className="text-xl font-semibold mb-4 text-white">New Topic</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Title</label>
              <input type="text" className="input-field" value={title} onChange={e => setTitle(e.target.value)} required />
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 hover:bg-white/5 text-gray-300 rounded-lg transition-colors">Cancel</button>
              <button type="submit" className="btn-primary">Create</button>
            </div>
          </div>
        </form>
      )}

      {loading ? (
        <div className="animate-pulse space-y-4 max-w-4xl">
          {[1,2,3].map(i => <div key={i} className="glass-card h-20 bg-dark-card/50"></div>)}
        </div>
      ) : (
        <div className="space-y-4 max-w-4xl">
          {topics.map((topic, index) => (
            <Link to={`/${user?.role.toLowerCase()}/topics/${topic.id}`} key={topic.id} className="block glass-card group hover:-translate-y-1 transition-transform duration-300 p-6 flex flex-row items-center border-l-4 border-l-transparent hover:border-l-primary-500 hover:shadow-primary-500/10 z-10">
              <div className="p-3 bg-primary-500/10 rounded-lg mr-4 text-primary-400 group-hover:bg-primary-500/20 transition-colors">
                <Layers className="h-6 w-6" />
              </div>
              <div className="flex-1">
                <div className="text-xs text-primary-400 font-medium mb-1 tracking-wider uppercase">Module {index + 1}</div>
                <h3 className="text-lg font-semibold text-white">{topic.title}</h3>
              </div>
              <div className="text-gray-500 group-hover:text-primary-400 transition-colors">
                <span aria-hidden="true">&rarr;</span>
              </div>
            </Link>
          ))}
          {topics.length === 0 && (
            <div className="py-16 flex flex-col items-center justify-center text-gray-500 border border-dashed border-dark-border rounded-xl">
              <Layers className="h-12 w-12 text-dark-border mb-3" />
              <p>No topics added to this course yet.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CourseDetails;
