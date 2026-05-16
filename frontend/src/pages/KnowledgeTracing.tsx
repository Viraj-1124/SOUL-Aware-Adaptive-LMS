import { useState } from 'react';
import { knowledgeApi } from '../api/knowledge';
import { useAuth } from '../context/AuthContext';
import { Target, TrendingUp, Award, AlertTriangle, BookOpen, User as UserIcon, BrainCircuit } from 'lucide-react';

const KnowledgeTracing = () => {
  const { user } = useAuth();
  const [topicId, setTopicId] = useState('');
  const [studentId, setStudentId] = useState('');
  
  const [stateData, setStateData] = useState<any>(null);
  const [predictionData, setPredictionData] = useState<any>(null);
  const [recommendationData, setRecommendationData] = useState<any>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchKnowledge = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const targetStudent = user?.role === 'STUDENT' ? user.id : Number(studentId);
      const targetTopic = Number(topicId);

      const [stateRes, predRes, recRes] = await Promise.all([
        knowledgeApi.getKnowledgeState(targetStudent),
        knowledgeApi.getPrediction(targetStudent),
        knowledgeApi.getRecommendation(targetStudent, targetTopic)
      ]);

      // State and pred return arrays for all topics, let's filter for the selected topic
      const specificState = stateRes.find((s: any) => s.topic_id === targetTopic);
      const specificPred = predRes.find((p: any) => p.topic_id === targetTopic);

      setStateData(specificState || {
        bkt_probability: 0,
        lstm_probability: 0,
        mastery_level: 'No Data'
      });
      setPredictionData(specificPred || {
        prediction_correct: false
      });
      setRecommendationData(recRes);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to fetch Knowledge Tracing data.');
      
      // Fallback data
      setStateData({
        bkt_probability: 0.65,
        lstm_probability: 0.70,
        mastery_level: 'Intermediate'
      });
      setPredictionData({ prediction_correct: true });
      setRecommendationData({
        recommendation: 'Normal',
        action_item: 'Continue with standard curriculum progression. Fallback data shown.'
      });
    } finally {
      setLoading(false);
    }
  };

  const getMasteryColor = (level: string) => {
    if (level === 'Mastered') return 'text-green-400 border-green-500/50 bg-green-500/10 shadow-[0_0_30px_rgba(34,197,94,0.2)]';
    if (level === 'Intermediate') return 'text-yellow-400 border-yellow-500/50 bg-yellow-500/10 shadow-[0_0_30px_rgba(234,179,8,0.2)]';
    return 'text-red-400 border-red-500/50 bg-red-500/10 shadow-[0_0_30px_rgba(239,68,68,0.2)]';
  };

  const getRecColor = (rec: string) => {
    if (rec === 'Advanced') return 'text-green-400';
    if (rec === 'Normal') return 'text-blue-400';
    return 'text-red-400';
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200 flex items-center gap-3">
          <Target className="h-8 w-8 text-primary-400" />
          Knowledge Tracing Engine
        </h1>
        <p className="text-gray-400 mt-1">AI-powered concept mastery tracking and adaptive path recommendation.</p>
      </div>

      <form onSubmit={fetchKnowledge} className="glass-card p-6 flex flex-col md:flex-row gap-4 items-end">
        {(user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && (
          <div className="flex-1 w-full">
            <label className="block text-sm text-gray-300 mb-1">Student ID</label>
            <div className="relative">
              <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input type="number" className="input-field pl-9" value={studentId} onChange={e => setStudentId(e.target.value)} required />
            </div>
          </div>
        )}
        <div className="flex-1 w-full">
          <label className="block text-sm text-gray-300 mb-1">Topic ID</label>
          <div className="relative">
            <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input type="number" className="input-field pl-9" value={topicId} onChange={e => setTopicId(e.target.value)} required />
          </div>
        </div>
        <button type="submit" className="btn-primary w-full md:w-auto whitespace-nowrap" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze Mastery'}
        </button>
      </form>

      {error && <div className="p-4 bg-yellow-500/10 border border-yellow-500/50 text-yellow-400 rounded-lg text-sm">{error}</div>}

      {stateData && recommendationData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in">
          
          {/* Mastery Card */}
          <div className={`glass-card p-8 flex flex-col items-center justify-center text-center border transition-all duration-700 ${getMasteryColor(stateData.mastery_level)}`}>
            <Award className="h-16 w-16 mb-4" />
            <div className="text-3xl font-black text-white mb-2">{stateData.mastery_level}</div>
            <div className="text-sm opacity-80 mt-1 uppercase tracking-wider font-semibold">Current Mastery Level</div>
          </div>

          {/* Probabilities Card */}
          <div className="glass-card p-6 flex flex-col justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2 border-b border-dark-border pb-3">
                <TrendingUp className="h-5 w-5 text-primary-400" />
                Model Probabilities
              </h3>
              
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300 font-medium">BKT Probability</span>
                    <span className="text-white">{(stateData.bkt_probability * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-dark-bg rounded-full h-2">
                    <div className="bg-primary-500 h-2 rounded-full" style={{ width: `${stateData.bkt_probability * 100}%` }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300 font-medium">LSTM Probability</span>
                    <span className="text-white">{(stateData.lstm_probability * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-dark-bg rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${stateData.lstm_probability * 100}%` }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendation Card */}
          <div className="glass-card p-6 flex flex-col justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2 border-b border-dark-border pb-3">
                <Target className="h-5 w-5 text-primary-400" />
                Adaptive AI Path
              </h3>
              
              <div className="space-y-4">
                <div className="bg-dark-bg/50 p-4 rounded-xl border border-dark-border">
                  <span className="text-xs text-gray-400 uppercase tracking-wider font-bold mb-1 block">Recommendation</span>
                  <span className={`text-lg font-bold ${getRecColor(recommendationData.recommendation)}`}>
                    {recommendationData.recommendation}
                  </span>
                </div>
                
                <div className="bg-dark-bg/50 p-4 rounded-xl border border-dark-border flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5 text-primary-400" />
                  <span className="text-sm text-gray-300 leading-relaxed">
                    {recommendationData.action_item}
                  </span>
                </div>
              </div>
            </div>
          </div>

        </div>
      )}

      {predictionData && stateData && (
        <div className="glass-card p-6 animate-fade-in mt-6">
           <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <BrainCircuit className="h-5 w-5 text-primary-400" />
              Next-Answer Correctness Prediction
           </h3>
           <p className="text-gray-300 mb-4">
             Based on the student's historical sequence, the AI models predict whether they will answer the next question in this topic correctly.
           </p>
           <div className={`p-4 rounded-xl border flex items-center gap-4 ${predictionData.prediction_correct ? 'bg-green-500/10 border-green-500/50 text-green-400' : 'bg-red-500/10 border-red-500/50 text-red-400'}`}>
              <div className="font-bold text-lg">
                {predictionData.prediction_correct ? "✓ Likely to Answer Correctly" : "✗ Likely to Struggle"}
              </div>
           </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeTracing;
