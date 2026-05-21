import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { topicsApi } from '../api/topics';
import { useAuth } from '../context/AuthContext';
import { Layers, Plus, ChevronLeft, Sparkles, Brain } from 'lucide-react';
import { analyzeCurriculum } from '../api/alerts';

const CourseDetails = () => {
  const { courseId } = useParams();
  const { user } = useAuth();
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [adaptationInfo, setAdaptationInfo] = useState<{ reason: string; status: string } | null>(null);
  
  // For instructor to create topic
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');

  const fetchTopics = async () => {
    try {
      setLoading(true);
      if (courseId) {
        const data = await topicsApi.getTopics(Number(courseId));
        
        if (user?.role === 'STUDENT' && data.length > 0) {
          const studentId = user.id || 1;
          const originalIds = data.map((t: any) => t.id);
          const adaptation = await analyzeCurriculum(studentId, Number(courseId), originalIds);
          if (adaptation && (adaptation.status === 'created' || adaptation.status === 'using_existing') && adaptation.adapted_sequence) {
            setAdaptationInfo({ reason: adaptation.reason, status: adaptation.status });
            
            const adaptedSeq: number[] = adaptation.adapted_sequence;
            const mapped = adaptedSeq.map(id => {
              if (id === 999) {
                return { id: 999, title: "Reflection Break", isReflectionBreak: true };
              }
              return data.find((t: any) => t.id === id);
            }).filter(Boolean);
            
            // Append any missing topics just in case
            const missing = data.filter((t: any) => !adaptedSeq.includes(t.id));
            setTopics([...mapped, ...missing]);
          } else {
            setTopics(data);
          }
        } else {
          setTopics(data);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopics();
  }, [courseId, user]);

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

      {user?.role === 'STUDENT' && adaptationInfo && (
        <div className="glass-card p-6 mb-8 border-l-4 border-l-primary-500 bg-gradient-to-r from-primary-500/10 to-transparent flex gap-4 items-start animate-fade-in max-w-4xl">
          <div className="p-2 bg-primary-500/20 rounded-lg text-primary-400">
            <Brain className="h-6 w-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              Adaptive Curriculum Active
              <span className="text-xs bg-primary-500/20 text-primary-300 px-2 py-0.5 rounded-full font-normal border border-primary-500/30">
                AI Powered
              </span>
            </h3>
            <p className="text-gray-300 text-sm mt-1">
              {adaptationInfo.reason === 'SKILL_GAP' && "We've custom-tailored your module sequence to address specific skill gaps and optimize understanding."}
              {adaptationInfo.reason === 'FATIGUE' && "To prevent cognitive overload, we've structured your curriculum with pacing buffers."}
              {adaptationInfo.reason === 'PACE_ADJUSTMENT' && "Your learning speed has been analyzed, and modules have been re-arranged for optimal pacing."}
              {!['SKILL_GAP', 'FATIGUE', 'PACE_ADJUSTMENT'].includes(adaptationInfo.reason) && `Curriculum sequence adapted: ${adaptationInfo.reason}`}
            </p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="animate-pulse space-y-4 max-w-4xl">
          {[1,2,3].map(i => <div key={i} className="glass-card h-20 bg-dark-card/50"></div>)}
        </div>
      ) : (
        <div className="space-y-4 max-w-4xl">
          {topics.map((topic, index) => {
            if (topic.isReflectionBreak) {
              return (
                <Link
                  to="/student/reflection"
                  key="reflection-break"
                  className="block glass-card group hover:-translate-y-1 transition-transform duration-300 p-6 flex flex-row items-center border-l-4 border-l-purple-500 bg-gradient-to-r from-purple-500/10 to-transparent hover:border-l-purple-400 hover:shadow-purple-500/10 z-10"
                >
                  <div className="p-3 bg-purple-500/20 rounded-lg mr-4 text-purple-400 group-hover:bg-purple-500/30 transition-colors">
                    <Sparkles className="h-6 w-6 animate-pulse" />
                  </div>
                  <div className="flex-1">
                    <div className="text-xs text-purple-400 font-medium mb-1 tracking-wider uppercase">Adaptive Check-in</div>
                    <h3 className="text-lg font-semibold text-white">Interactive Reflection Break</h3>
                    <p className="text-sm text-gray-400 mt-1">Take a moment to write a brief journal response to consolidate your learning.</p>
                  </div>
                  <div className="text-purple-400 group-hover:translate-x-1 transition-transform">
                    <span aria-hidden="true">&rarr;</span>
                  </div>
                </Link>
              );
            }

            return (
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
            );
          })}
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
