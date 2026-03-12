import { useState, useEffect } from 'react';
import { coursesApi } from '../api/courses';
import { topicsApi } from '../api/topics';
import { quizApi } from '../api/quiz';
import { CheckSquare, Plus, Layers, ChevronLeft } from 'lucide-react';

const QuizMgmt = () => {
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<any>(null);
  const [topics, setTopics] = useState<any[]>([]);
  
  const [selectedTopic, setSelectedTopic] = useState<any>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  
  const [showAddQuestion, setShowAddQuestion] = useState(false);
  const [newQuestion, setNewQuestion] = useState({
    question: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_option: 'A'
  });

  useEffect(() => {
    coursesApi.getCourses().then(setCourses).catch(console.error);
  }, []);

  const handleSelectCourse = async (course: any) => {
    setSelectedCourse(course);
    const data = await topicsApi.getTopics(course.id);
    setTopics(data);
  };

  const handleSelectTopic = async (topic: any) => {
    setSelectedTopic(topic);
    const data = await quizApi.getQuestions(topic.id);
    setQuestions(Array.isArray(data) ? data : []);
  };

  const handleAddQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTopic) return;
    try {
      await quizApi.addQuestion({ ...newQuestion, topic_id: selectedTopic.id });
      setNewQuestion({ question: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_option: 'A' });
      setShowAddQuestion(false);
      
      // Refresh questions
      const data = await quizApi.getQuestions(selectedTopic.id);
      setQuestions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    }
  };

  if (selectedTopic && selectedCourse) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10 w-full">
         <div className="flex items-center gap-4 mb-6">
          <button onClick={() => setSelectedTopic(null)} className="p-2 bg-dark-card hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-colors">
            <ChevronLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-purple-200">
              Quiz for: {selectedTopic.title}
            </h1>
            <p className="text-gray-400">Manage questions for this topic module.</p>
          </div>
        </div>

        <div className="flex justify-end mb-4">
          <button onClick={() => setShowAddQuestion(!showAddQuestion)} className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" /> Add Question
          </button>
        </div>

        {showAddQuestion && (
          <form onSubmit={handleAddQuestion} className="glass-card p-6 mb-8 animate-fade-in">
            <h2 className="text-xl font-semibold mb-4 text-white">New Question</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-300 mb-1">Question Text</label>
                <textarea className="input-field h-20" value={newQuestion.question} onChange={e => setNewQuestion({...newQuestion, question: e.target.value})} required />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div><label className="block text-sm text-gray-300 mb-1">Option A</label><input type="text" className="input-field" value={newQuestion.option_a} onChange={e => setNewQuestion({...newQuestion, option_a: e.target.value})} required /></div>
                <div><label className="block text-sm text-gray-300 mb-1">Option B</label><input type="text" className="input-field" value={newQuestion.option_b} onChange={e => setNewQuestion({...newQuestion, option_b: e.target.value})} required /></div>
                <div><label className="block text-sm text-gray-300 mb-1">Option C</label><input type="text" className="input-field" value={newQuestion.option_c} onChange={e => setNewQuestion({...newQuestion, option_c: e.target.value})} required /></div>
                <div><label className="block text-sm text-gray-300 mb-1">Option D</label><input type="text" className="input-field" value={newQuestion.option_d} onChange={e => setNewQuestion({...newQuestion, option_d: e.target.value})} required /></div>
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Correct Option</label>
                <select className="input-field" value={newQuestion.correct_option} onChange={e => setNewQuestion({...newQuestion, correct_option: e.target.value})}>
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                  <option value="D">D</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowAddQuestion(false)} className="px-4 py-2 hover:bg-white/5 text-gray-300 rounded-lg transition-colors">Cancel</button>
                <button type="submit" className="btn-primary">Add Question</button>
              </div>
            </div>
          </form>
        )}

        <div className="space-y-4">
           {questions.map((q, i) => (
             <div key={q.id || i} className="glass-card p-6 border-l-4 border-l-purple-500">
               <h3 className="text-lg font-medium text-white mb-4"><span className="text-purple-400 mr-2">Q{i+1}.</span> {q.question}</h3>
               <div className="grid grid-cols-2 gap-2 text-sm text-gray-300">
                  <div className={`p-2 rounded ${q.correct_option === 'A' ? 'bg-green-500/20 text-green-300 border border-green-500/30' : 'bg-dark-bg'}`}>A. {q.option_a}</div>
                  <div className={`p-2 rounded ${q.correct_option === 'B' ? 'bg-green-500/20 text-green-300 border border-green-500/30' : 'bg-dark-bg'}`}>B. {q.option_b}</div>
                  <div className={`p-2 rounded ${q.correct_option === 'C' ? 'bg-green-500/20 text-green-300 border border-green-500/30' : 'bg-dark-bg'}`}>C. {q.option_c}</div>
                  <div className={`p-2 rounded ${q.correct_option === 'D' ? 'bg-green-500/20 text-green-300 border border-green-500/30' : 'bg-dark-bg'}`}>D. {q.option_d}</div>
               </div>
             </div>
           ))}
           {questions.length === 0 && (
              <div className="py-16 text-center text-gray-500 border border-dashed border-dark-border rounded-xl">
                No quiz questions added yet.
              </div>
           )}
        </div>
      </div>
    );
  }

  if (selectedCourse && !selectedTopic) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10 w-full">
        <div className="flex items-center gap-4 mb-6">
          <button onClick={() => setSelectedCourse(null)} className="p-2 bg-dark-card hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-colors">
            <ChevronLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-purple-200">
              {selectedCourse.title} Topics
            </h1>
            <p className="text-gray-400">Select a topic to manage its quiz questions.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 mt-8">
          {topics.map((topic, idx) => (
             <button onClick={() => handleSelectTopic(topic)} key={topic.id} className="glass-card p-6 flex items-center border-l-4 border-transparent hover:border-purple-500 cursor-pointer text-left transition-all">
                <Layers className="h-6 w-6 text-purple-400 mr-4" />
                <div>
                   <div className="text-xs text-purple-400 uppercase tracking-widest mb-1">Module {idx + 1}</div>
                   <h3 className="text-lg font-bold text-white">{topic.title}</h3>
                </div>
             </button>
          ))}
          {topics.length === 0 && (
             <div className="p-8 text-center text-gray-500 glass-card">No topics exist in this course. Add topics first.</div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10 w-full">
      <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-purple-200">Quiz Management</h1>
      <p className="text-gray-400">Select a course to drill down into its Topics and manage Quizzes.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
        {courses.map(course => (
          <button onClick={() => handleSelectCourse(course)} key={course.id} className="glass-card p-6 hover:-translate-y-1 transition-transform border-t-4 border-t-purple-500 cursor-pointer text-left w-full flex flex-col">
            <CheckSquare className="h-8 w-8 text-purple-400 mb-4" />
            <h3 className="text-xl font-bold text-white">{course.title}</h3>
            <p className="text-gray-400 mt-2 text-sm">Select Course &rarr;</p>
          </button>
        ))}
      </div>
    </div>
  );
};
export default QuizMgmt;
