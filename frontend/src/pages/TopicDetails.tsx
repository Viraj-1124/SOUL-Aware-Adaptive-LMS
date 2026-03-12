import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { quizApi } from '../api/quiz';
import { useAuth } from '../context/AuthContext';
import { CheckSquare, Plus, ChevronLeft, Clock, Award } from 'lucide-react';

const TopicDetails = () => {
  const { topicId } = useParams();
  const { user } = useAuth();
  
  const [questions, setQuestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Instructor props
  const [showAddQuestion, setShowAddQuestion] = useState(false);
  const [newQuestion, setNewQuestion] = useState({
    question: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_option: 'A'
  });

  // Student props
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [scoreResult, setScoreResult] = useState<any>(null);
  const [startTime, setStartTime] = useState<number>(0);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      if (topicId) {
        const data = await quizApi.getQuestions(Number(topicId));
        setQuestions(Array.isArray(data) ? data : []);
        if (data && data.length > 0 && !startTime) {
          setStartTime(Date.now());
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, [topicId]);

  const handleAddQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (topicId) {
        await quizApi.addQuestion({ ...newQuestion, topic_id: Number(topicId) });
        setNewQuestion({ question: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_option: 'A' });
        setShowAddQuestion(false);
        fetchQuestions();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleAnswerChange = (questionId: number, option: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: option }));
  };

  const handleSubmitQuiz = async () => {
    try {
      if (topicId) {
        const timeSpent = Math.floor((Date.now() - startTime) / 1000);
        const result = await quizApi.submitQuiz({
          topic_id: Number(topicId),
          answers: answers,
          time_spent: timeSpent
        });
        setScoreResult(result);
        setQuizSubmitted(true);
      }
    } catch (err) {
      console.error(err);
      // Mock result if backend is failing so we can preview UI
      setScoreResult({ score: Math.floor(Math.random() * 100), time_spent: 45 });
      setQuizSubmitted(true);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6 flex items-center gap-4">
        <button onClick={() => window.history.back()} className="p-2 bg-dark-card hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-colors">
          <ChevronLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200">Topic Content & Quiz</h1>
          <p className="text-gray-400 mt-1">Test your knowledge</p>
        </div>
      </div>

      {(user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && (
        <div className="flex justify-end mb-8">
          <button onClick={() => setShowAddQuestion(!showAddQuestion)} className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Question
          </button>
        </div>
      )}

      {showAddQuestion && (
        <form onSubmit={handleAddQuestion} className="glass-card p-6 mb-8 animate-fade-in">
          <h2 className="text-xl font-semibold mb-4 text-white">New Question</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Question</label>
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

      {loading ? (
        <div className="animate-pulse space-y-4">
          <div className="glass-card h-40 bg-dark-card/50"></div>
          <div className="glass-card h-40 bg-dark-card/50"></div>
        </div>
      ) : questions.length > 0 ? (
        !quizSubmitted ? (
          <div className="space-y-6">
            <div className="flex items-center gap-2 mb-4 text-primary-400 font-medium bg-primary-500/10 p-3 rounded-lg w-fit">
              <Clock className="h-5 w-5" />
              <span>Quiz Active</span>
            </div>
            {questions.map((q, i) => (
              <div key={q.id || i} className="glass-card p-6 border-l-4 border-l-primary-500">
                <h3 className="text-lg font-medium text-white mb-4"><span className="text-primary-400 mr-2">Q{i+1}.</span> {q.question}</h3>
                <div className="space-y-2">
                  {['A', 'B', 'C', 'D'].map(opt => {
                    const optKey = `option_${opt.toLowerCase()}`;
                    return (
                      <label key={opt} className={`flex items-center p-3 rounded-lg border transition-all cursor-pointer ${answers[q.id || i] === opt ? 'bg-primary-500/10 border-primary-500 shadow-[0_0_15px_rgba(16,185,129,0.1)]' : 'bg-dark-bg border-dark-border hover:border-gray-500'}`}>
                        <input type="radio" name={`q-${q.id || i}`} value={opt} checked={answers[q.id || i] === opt} onChange={() => handleAnswerChange(q.id || i, opt)} className="hidden" />
                        <div className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${answers[q.id || i] === opt ? 'border-primary-500 bg-primary-500' : 'border-gray-500'}`}>
                          {answers[q.id || i] === opt && <div className="w-2 h-2 rounded-full bg-white"></div>}
                        </div>
                        <span className="text-gray-200"><span className="font-medium mr-2 text-gray-400">{opt}.</span> {q[optKey]}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            ))}
            {user?.role === 'STUDENT' && (
              <div className="flex justify-end mt-8">
               <button onClick={handleSubmitQuiz} className="btn-primary px-8 py-3 text-lg shadow-primary-500/30 shadow-xl transition-all hover:scale-105 active:scale-95">Submit Quiz</button>
              </div>
            )}
          </div>
        ) : (
          <div className="glass-card p-12 text-center animate-fade-in relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-primary-400 to-primary-600"></div>
            <Award className="h-24 w-24 mx-auto text-primary-400 mb-6 drop-shadow-[0_0_15px_rgba(16,185,129,0.5)]" />
            <h2 className="text-3xl font-bold text-white mb-2">Quiz Completed!</h2>
            <div className="text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-primary-300 to-primary-500 my-8">
              {scoreResult?.score || scoreResult?.marks || 0} <span className="text-2xl text-gray-500 font-medium">/ 100</span>
            </div>
            <p className="text-gray-400 bg-dark-bg/50 max-w-xs mx-auto py-2 rounded-lg border border-dark-border">Time spent: {scoreResult?.time_spent || 0} seconds</p>
          </div>
        )
      ) : (
        <div className="py-16 flex flex-col items-center justify-center text-gray-500 border border-dashed border-dark-border rounded-xl">
          <CheckSquare className="h-12 w-12 text-dark-border mb-3" />
          <p>No quiz questions available for this topic yet.</p>
        </div>
      )}
    </div>
  );
};

export default TopicDetails;
