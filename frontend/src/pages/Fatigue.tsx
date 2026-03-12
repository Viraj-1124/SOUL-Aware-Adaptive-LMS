import { useState } from 'react';
import { fatigueApi } from '../api/fatigue';
import { useAuth } from '../context/AuthContext';
import { BrainCircuit, BatteryWarning, Activity, AlertTriangle, BatteryMedium, BatteryCharging } from 'lucide-react';

const Fatigue = () => {
  const { user } = useAuth();
  const [courseId, setCourseId] = useState('');
  const [studentId, setStudentId] = useState('');
  const [fatigueData, setFatigueData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchFatigue = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const targetStudent = user?.role === 'STUDENT' ? user.id : Number(studentId);
      const res = await fatigueApi.getFatigueMonitor(targetStudent, Number(courseId));
      setFatigueData(res);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Connecting to prediction engine failed (Backend ML endpoint likely not wired). Using fallback UI visualization.');
      
      // Fallback data
      setFatigueData({
        fatigue_score: 68,
        fatigue_level: 'Moderate', // 'Low', 'Moderate', 'High'
        signals: [
          'Decreased interaction frequency',
          'Longer time on quiz screens',
          'Late assignment submissions'
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const getFatigueColor = (level: string) => {
    if (level === 'HIGH' || level === 'High') return 'text-red-500 border-red-500/50 bg-red-500/10 shadow-[0_0_30px_rgba(239,68,68,0.2)]';
    if (level === 'MODERATE' || level === 'Moderate') return 'text-yellow-400 border-yellow-500/50 bg-yellow-500/10 shadow-[0_0_30px_rgba(234,179,8,0.2)]';
    return 'text-green-400 border-green-500/50 bg-green-500/10 shadow-[0_0_30px_rgba(34,197,94,0.2)]';
  };

  const getFatigueIcon = (level: string) => {
    if (level === 'HIGH' || level === 'High') return <BatteryWarning className="h-20 w-20 text-red-500 mb-4 animate-pulse" />;
    if (level === 'MODERATE' || level === 'Moderate') return <BatteryMedium className="h-20 w-20 text-yellow-400 mb-4" />;
    return <BatteryCharging className="h-20 w-20 text-green-400 mb-4" />;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200 flex items-center gap-3">
          <BrainCircuit className="h-8 w-8 text-primary-400" />
          Moral Fatigue Monitor
        </h1>
        <p className="text-gray-400 mt-1">Real-time cognitive load and fatigue detection</p>
      </div>

      <form onSubmit={fetchFatigue} className="glass-card p-6 flex flex-col md:flex-row gap-4 items-end">
        {(user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && (
          <div className="flex-1 w-full">
            <label className="block text-sm text-gray-300 mb-1">Student ID</label>
            <input type="number" className="input-field" value={studentId} onChange={e => setStudentId(e.target.value)} required />
          </div>
        )}
        <div className="flex-1 w-full">
          <label className="block text-sm text-gray-300 mb-1">Course ID</label>
          <input type="number" className="input-field" value={courseId} onChange={e => setCourseId(e.target.value)} required />
        </div>
        <button type="submit" className="btn-primary w-full md:w-auto whitespace-nowrap" disabled={loading}>
          {loading ? 'Analyzing Behavior...' : 'Run Monitor'}
        </button>
      </form>

      {error && <div className="p-4 bg-yellow-500/10 border border-yellow-500/50 text-yellow-400 rounded-lg text-sm">{error}</div>}

      {fatigueData && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-fade-in">
          
          <div className={`glass-card p-8 flex flex-col items-center justify-center text-center border transition-all duration-700 ${getFatigueColor(fatigueData.fatigue_level || '')}`}>
            {getFatigueIcon(fatigueData.fatigue_level || '')}
            <div className="text-6xl font-black text-white mb-2">{fatigueData.fatigue_score || 0}</div>
            <div className="text-2xl font-bold uppercase tracking-widest mt-2">{fatigueData.fatigue_level || 'Unknown'}</div>
            <div className="text-sm opacity-80 mt-2">Current Fatigue Risk Status</div>
          </div>

          <div className="glass-card p-6 flex flex-col justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white mb-6 flex items-center gap-2 border-b border-dark-border pb-4">
                <Activity className="h-5 w-5 text-primary-400" />
                Detected Signals
              </h3>
              
              <ul className="space-y-4">
                {fatigueData.signals && 
                (Array.isArray(fatigueData.signals) ? fatigueData.signals.length > 0 : Object.entries(fatigueData.signals).filter(([_,v]) => v).length > 0) ? (
                  (Array.isArray(fatigueData.signals) ? fatigueData.signals : Object.entries(fatigueData.signals).filter(([_,v]) => v).map(([k,_]: any) => k)).map((signal: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-3 bg-dark-bg/50 p-3 rounded-lg border border-dark-border">
                      <AlertTriangle className={`h-5 w-5 shrink-0 mt-0.5 ${(fatigueData.fatigue_level === 'HIGH' || fatigueData.fatigue_level === 'High') ? 'text-red-400' : 'text-yellow-400'}`} />
                      <span className="text-gray-300 capitalize">{signal.replace(/_/g, ' ')}</span>
                    </li>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">No concerning signals detected.</div>
                )}
              </ul>
            </div>
            
            
          </div>

        </div>
      )}
    </div>
  );
};
export default Fatigue;
