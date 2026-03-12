import { useState, useEffect } from 'react';
import { predictionApi } from '../api/prediction';
import { useAuth } from '../context/AuthContext';
import { Network, Search, AlertOctagon, UserCheck, ShieldAlert, Cpu } from 'lucide-react';

const Predictions = () => {
  const { user } = useAuth();
  
  // Student props
  const [courseId, setCourseId] = useState('');
  const [studentResult, setStudentResult] = useState<any>(null);
  
  // Instructor props
  const [allStudents, setAllStudents] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchStudentPrediction = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (user) {
        const res = await predictionApi.predictBurnout(user.id, Number(courseId));
        setStudentResult(res);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Prediction engine error. Providing mock data.');
      // Mock data
      setStudentResult({ risk_level: Math.floor(Math.random() * 3), features_used: { engagement: 0.8, attendance: 0.9, trend: "stable" } });
    } finally {
      setLoading(false);
    }
  };

  const fetchAllPredictions = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await predictionApi.runForAllStudents();
      setSummary(res.summary ? res.summary : null);
      setAllStudents(res.results ? res.results : (Array.isArray(res) ? res : []));
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to run batch predictions. Loading mock dataset.');
      // Mock dataset
      setSummary({ low_risk: 30, medium_risk: 12, high_risk: 3 });
      setAllStudents([
        { student_id: 101, risk_level: 'low_risk' },
        { student_id: 102, risk_level: 'medium_risk' },
        { student_id: 103, risk_level: 'high_risk' },
        { student_id: 104, risk_level: 'low_risk' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') {
      fetchAllPredictions();
    }
  }, [user]);

  const getRiskLabel = (level: number | string) => {
    switch (level) {
      case 0:
      case 'low_risk': return { label: 'Healthy', color: 'text-green-400 bg-green-500/10 border-green-500/30' };
      case 1:
      case 'medium_risk': return { label: 'Disengaged', color: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30' };
      case 2:
      case 'high_risk': return { label: 'Burnout', color: 'text-red-400 bg-red-500/10 border-red-500/30' };
      default: return { label: 'Unknown', color: 'text-gray-400 bg-gray-500/10 border-gray-500/30' };
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200 flex items-center gap-3">
            <Network className="h-8 w-8 text-primary-400" />
            Burnout Prediction Engine
          </h1>
          <p className="text-gray-400 mt-1">Deep Learning based early warning system</p>
        </div>
        {(user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && (
          <button onClick={fetchAllPredictions} className="btn-primary flex items-center gap-2" disabled={loading}>
            <Cpu className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Run Batch Analysis
          </button>
        )}
      </div>

      {error && <div className="p-4 bg-yellow-500/10 border border-yellow-500/50 text-yellow-400 rounded-lg text-sm">{error}</div>}

      {/* STUDENT UI */}
      {user?.role === 'STUDENT' && (
        <div className="space-y-6">
          <form onSubmit={fetchStudentPrediction} className="glass-card p-6 flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1 w-full">
              <label className="block text-sm text-gray-300 mb-1">Enter Course ID to predict your risk:</label>
              <input type="number" className="input-field" value={courseId} onChange={e => setCourseId(e.target.value)} required />
            </div>
            <button type="submit" className="btn-primary w-full sm:w-auto" disabled={loading}>
              <Search className="h-4 w-4" />
            </button>
          </form>

          {studentResult && (
            <div className="glass-card p-8 animate-fade-in relative overflow-hidden">
              <div className="absolute top-0 right-0 p-8 opacity-10">
                <Network className="h-64 w-64" />
              </div>
              <div className="relative z-10 flex flex-col md:flex-row gap-8 items-center">
                <div className={`p-8 rounded-full border-4 flex items-center justify-center h-48 w-48 shrink-0 ${studentResult.risk_level === 2 ? 'border-red-500/50 bg-red-500/10' : studentResult.risk_level === 1 ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-green-500/50 bg-green-500/10'}`}>
                  <div className="text-center">
                    {studentResult.risk_level === 2 ? <AlertOctagon className="h-12 w-12 text-red-400 mx-auto mb-2" /> : studentResult.risk_level === 1 ? <ShieldAlert className="h-12 w-12 text-yellow-400 mx-auto mb-2" /> : <UserCheck className="h-12 w-12 text-green-400 mx-auto mb-2" />}
                    <div className="font-bold text-xl text-white">{getRiskLabel(studentResult.risk_level || 0).label}</div>
                  </div>
                </div>
                
                <div className="flex-1 w-full">
                  <h3 className="text-2xl font-bold text-white mb-4">AI Diagnosis</h3>
                  <div className="p-4 bg-dark-bg/80 rounded-lg border border-dark-border mb-4">
                    <p className="text-gray-300">
                      {studentResult.risk_level === 2 
                        ? "High probability of burnout detected. Consider taking a break or reaching out to your instructor for a flexible deadline."
                        : studentResult.risk_level === 1 
                        ? "Signs of disengagement noticed. Try to improve your course interaction frequency."
                        : "Your learning patterns are healthy. Keep up the good work!"}
                    </p>
                  </div>
                  <div className="mt-4">
                    <span className="text-sm font-medium text-gray-400 uppercase tracking-wide">Key Features Analyzed Base</span>
                    <div className="flex gap-2 mt-2 flex-wrap">
                      {studentResult.features_used && Object.entries(studentResult.features_used).map(([k, v]) => (
                        <div key={k} className="px-3 py-1 bg-white/5 border border-white/10 rounded-md text-xs text-primary-200 uppercase">
                          {k}: {String(v)}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* INSTRUCTOR / ADMIN UI */}
      {(user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && (
        <div className="space-y-6">
          {summary && (
            <div className="grid grid-cols-3 gap-6 animate-fade-in">
              <div className="glass-card p-6 border-t-4 border-t-green-500 text-center">
                <div className="text-sm text-gray-400 uppercase tracking-wide mb-2">Low Risk Students</div>
                <div className="text-4xl font-bold text-white">{summary.low_risk || 0}</div>
              </div>
              <div className="glass-card p-6 border-t-4 border-t-yellow-500 text-center">
                <div className="text-sm text-gray-400 uppercase tracking-wide mb-2">Medium Risk Students</div>
                <div className="text-4xl font-bold text-white">{summary.medium_risk || 0}</div>
              </div>
              <div className="glass-card p-6 border-t-4 border-t-red-500 text-center">
                <div className="text-sm text-gray-400 uppercase tracking-wide mb-2">High Risk Students</div>
                <div className="text-4xl font-bold text-white">{summary.high_risk || 0}</div>
              </div>
            </div>
          )}
          
          <div className="glass-card overflow-hidden">
            <div className="overflow-x-auto">
            {loading ? (
              <div className="p-12 text-center text-gray-500 flex flex-col items-center">
                <Cpu className="h-12 w-12 animate-pulse text-primary-500/50 mb-4" />
                <p className="animate-pulse">Running machine learning models on student data...</p>
              </div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-dark-border/50 text-gray-400 text-sm uppercase tracking-wider">
                    <th className="p-4 font-medium">Student ID</th>
                    <th className="p-4 font-medium">Course ID</th>
                    <th className="p-4 font-medium text-right">Predicted Risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-dark-border text-gray-300">
                  {allStudents.map((student, idx) => {
                    const risk = getRiskLabel(student.risk_level);
                    return (
                      <tr key={idx} className="hover:bg-white/5 transition-colors">
                        <td className="p-4 font-medium text-white">#{student.student_id}</td>
                        <td className="p-4 font-medium text-gray-300">#{student.course_id || 'N/A'}</td>
                        <td className="p-4 text-right">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${risk.color}`}>
                            {risk.label}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                  {allStudents.length === 0 && (
                    <tr>
                      <td colSpan={5} className="p-8 text-center text-gray-500">No predictions available. Click Run Batch Analysis.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>
        </div>
      )}

    </div>
  );
};
export default Predictions;
