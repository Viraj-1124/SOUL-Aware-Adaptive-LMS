import { useState, useEffect } from 'react';
import { coursesApi } from '../api/courses';
import { topicsApi } from '../api/topics';
import { BookOpen, Plus, Layers, ChevronLeft } from 'lucide-react';

const Topics = () => {  
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<any>(null);
  const [topics, setTopics] = useState<any[]>([]);
  const [loadingTopics, setLoadingTopics] = useState(false);
  
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');

  useEffect(() => {
    coursesApi.getCourses().then(setCourses).catch(console.error);
  }, []);

  const handleSelectCourse = async (course: any) => {
    setSelectedCourse(course);
    setLoadingTopics(true);
    try {
      const data = await topicsApi.getTopics(course.id);
      setTopics(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingTopics(false);
    }
  };

  const handleCreateTopic = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCourse) return;
    try {
      const data = await topicsApi.createTopic({ title, course_id: selectedCourse.id });
      setTopics([...topics, data]);
      setTitle('');
      setShowCreate(false);
    } catch (err) {
      console.error(err);
    }
  };

  if (selectedCourse) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10 w-full">
        <div className="flex items-center gap-4 mb-6">
          <button onClick={() => setSelectedCourse(null)} className="p-2 bg-dark-card hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-colors">
            <ChevronLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200">
              Manage Topics format {selectedCourse.title}
            </h1>
            <p className="text-gray-400">Add or view learning modules for this course.</p>
          </div>
        </div>

        <div className="flex justify-end mb-4">
          <button onClick={() => setShowCreate(!showCreate)} className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" /> Add Topic
          </button>
        </div>

        {showCreate && (
          <form onSubmit={handleCreateTopic} className="glass-card p-6 mb-8 max-w-2xl animate-fade-in">
            <h2 className="text-xl font-semibold mb-4 text-white">New Topic</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-300 mb-1">Topic Title</label>
                <input type="text" className="input-field" value={title} onChange={e => setTitle(e.target.value)} required />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 hover:bg-white/5 text-gray-300 rounded-lg transition-colors">Cancel</button>
                <button type="submit" className="btn-primary">Create</button>
              </div>
            </div>
          </form>
        )}

        {loadingTopics ? (
          <div className="animate-pulse space-y-4 max-w-4xl">
            {[1,2].map(i => <div key={i} className="glass-card h-20 bg-dark-card/50"></div>)}
          </div>
        ) : (
          <div className="space-y-4 max-w-4xl">
            {topics.map((topic, index) => (
               <div key={topic.id} className="glass-card p-6 flex flex-row items-center border-l-4 border-primary-500">
                  <div className="p-3 bg-primary-500/10 rounded-lg mr-4 text-primary-400">
                    <Layers className="h-6 w-6" />
                  </div>
                  <div>
                    <div className="text-xs text-primary-400 font-medium mb-1 tracking-wider uppercase">Module {index + 1}</div>
                    <h3 className="text-lg font-semibold text-white">{topic.title}</h3>
                  </div>
               </div>
            ))}
            {topics.length === 0 && (
              <div className="py-16 flex flex-col items-center justify-center text-gray-500 border border-dashed border-dark-border rounded-xl">
                <Layers className="h-12 w-12 text-dark-border mb-3" />
                <p>No topics organized in this course yet.</p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10 w-full">
      <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200">Topic Management</h1>
      <p className="text-gray-400">Select a course to manage its topics and learning modules.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
        {courses.map(course => (
          <button onClick={() => handleSelectCourse(course)} key={course.id} className="glass-card p-6 hover:-translate-y-1 text-left transition-transform border-t-4 border-t-primary-500 w-full flex flex-col cursor-pointer">
            <BookOpen className="h-8 w-8 text-primary-400 mb-4" />
            <h3 className="text-xl font-bold text-white">{course.title}</h3>
            <p className="text-gray-400 mt-2 text-sm">Organize Modules &rarr;</p>
          </button>
        ))}
      </div>
    </div>
  );
};
export default Topics;
