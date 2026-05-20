import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { alignmentApi } from '../api/model4_alignment';
import type { GoalAlignmentRequest, GoalAlignmentResponse, ContextPrefillOut } from '../api/model4_alignment';
import {
  Target, BrainCircuit, AlertTriangle, CheckCircle,
  BookOpen, User as UserIcon, Compass, Layers, ChevronDown, ChevronUp,
  RotateCcw, RefreshCw, Info
} from 'lucide-react';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts';

const ENVIRONMENTS = ['online', 'lab', 'project', 'self-study'];

const DOMAIN_COLORS: Record<string, string> = {
  frontend:      'text-blue-400',
  backend:       'text-green-400',
  ml:            'text-purple-400',
  data_science:  'text-yellow-400',
  devops:        'text-orange-400',
  mobile:        'text-pink-400',
  cybersecurity: 'text-red-400',
};

const SCAFFOLD_COLORS: Record<string, string> = {
  low:    'text-green-400 bg-green-500/10 border-green-500/40',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/40',
  high:   'text-red-400 bg-red-500/10 border-red-500/40',
};

const defaultForm: GoalAlignmentRequest = {
  goal_text: '',
  html_mastery: 0.5,
  css_mastery: 0.5,
  js_mastery: 0.5,
  react_mastery: 0.3,
  python_mastery: 0.4,
  ml_mastery: 0.2,
  dsa_mastery: 0.3,
  environment: 'online',
  engagement_score: 0.7,
  consistency_score: 0.6,
  integrity_score: 0.9,
  anomaly_score: 0.05,
};

const SliderField = ({
  label, name, value, onChange, readOnly = false
}: {
  label: string; name: string; value: number;
  onChange: (name: string, val: number) => void; readOnly?: boolean;
}) => (
  <div>
    <div className="flex justify-between text-sm mb-1">
      <span className="text-gray-300">{label}</span>
      <span className="text-white font-medium">{(value * 100).toFixed(0)}%</span>
    </div>
    <input
      type="range" min={0} max={1} step={0.05}
      value={value}
      onChange={e => onChange(name, parseFloat(e.target.value))}
      disabled={readOnly}
      className={`w-full accent-primary-500 ${readOnly ? 'opacity-60 cursor-not-allowed' : ''}`}
    />
  </div>
);

const GoalAlignment = () => {
  const { user } = useAuth();
  const [form, setForm] = useState<GoalAlignmentRequest>(defaultForm);
  const [studentId, setStudentId] = useState('');
  const [result, setResult] = useState<GoalAlignmentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoLoading, setAutoLoading] = useState(false);
  const [error, setError] = useState('');
  const [prefillMeta, setPrefillMeta] = useState<ContextPrefillOut | null>(null);
  const [showDomainScores, setShowDomainScores] = useState(false);

  const targetStudentId = user?.role === 'STUDENT' ? user.id : Number(studentId);

  const handleSlider = (name: string, val: number) => {
    setForm(prev => ({ ...prev, [name]: val }));
  };

  // Auto-fetch everything from DB for a student
  const autoFetchAll = useCallback(async (sid: number) => {
    if (!sid) return;
    setAutoLoading(true);
    setError('');
    try {
      const data = await alignmentApi.getContextPrefill(sid);
      setPrefillMeta(data);
      setForm(prev => ({
        ...prev,
        // Skill mastery from knowledge tracing
        html_mastery:      data.html_mastery,
        css_mastery:       data.css_mastery,
        js_mastery:        data.js_mastery,
        react_mastery:     data.react_mastery,
        python_mastery:    data.python_mastery,
        ml_mastery:        data.ml_mastery,
        dsa_mastery:       data.dsa_mastery,
        // Learning context from activity/reflection DB
        environment:       data.environment,
        engagement_score:  data.engagement_score,
        consistency_score: data.consistency_score,
        integrity_score:   data.integrity_score,
        anomaly_score:     data.anomaly_score,
        // Goal text from saved profile (keep existing if no saved goal)
        goal_text: data.has_saved_goal ? data.goal_text : prev.goal_text,
      }));
    } catch {
      // Silently fail — student may have no data yet, defaults remain
    } finally {
      setAutoLoading(false);
    }
  }, []);

  // Students: auto-fetch on page load
  useEffect(() => {
    if (user?.role === 'STUDENT' && user.id) {
      autoFetchAll(user.id);
    }
  }, [user, autoFetchAll]);

  // Instructor/Admin: auto-fetch when student ID is entered (debounced)
  useEffect(() => {
    if ((user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && Number(studentId) > 0) {
      const timer = setTimeout(() => autoFetchAll(Number(studentId)), 600);
      return () => clearTimeout(timer);
    }
  }, [studentId, user, autoFetchAll]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetStudentId) { setError('Please enter a Student ID.'); return; }
    if (!form.goal_text.trim()) { setError('Please enter a learning goal.'); return; }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await alignmentApi.analyzeGoal(targetStudentId, form);
      setResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run goal alignment analysis.');
    } finally {
      setLoading(false);
    }
  };

  const radarData = result
    ? Object.entries(result.skill_gap_vector).map(([key, gap]) => ({
        skill: key.replace('_mastery', '').replace('_', ' ').toUpperCase(),
        gap: Math.round(gap * 100),
        mastery: Math.round((1 - gap) * 100),
      }))
    : [];

  const domainData = result
    ? Object.entries(result.all_domain_scores)
        .sort((a, b) => b[1] - a[1])
        .map(([domain, score]) => ({ domain, score: Math.round(score * 100) }))
    : [];

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200 flex items-center gap-3">
          <Compass className="h-8 w-8 text-primary-400" />
          Goal & Skill Alignment
        </h1>
        <p className="text-gray-400 mt-1">
          AI-powered purpose alignment — maps your goal to a career domain, identifies skill gaps, and generates a personalised learning path.
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="glass-card p-6 space-y-6">

        {/* Instructor/Admin: student ID input */}
        {(user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && (
          <div>
            <label className="block text-sm text-gray-300 mb-1">
              Student ID
              <span className="ml-2 text-xs text-gray-500">— all fields auto-populate from student data</span>
            </label>
            <div className="relative">
              <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="number" className="input-field pl-9" value={studentId}
                onChange={e => setStudentId(e.target.value)}
                placeholder="Enter student ID to auto-load their data"
              />
              {autoLoading && (
                <RefreshCw className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-primary-400 animate-spin" />
              )}
            </div>
          </div>
        )}

        {/* Auto-load status banner */}
        {prefillMeta && (
          <div className="p-3 rounded-lg border text-xs flex items-start gap-2 bg-primary-500/5 border-primary-500/20 text-primary-300">
            <Info className="h-4 w-4 shrink-0 mt-0.5 text-primary-400" />
            <div className="space-y-0.5">
              <span className="font-semibold">Data auto-loaded from student records.</span>
              <div className="text-gray-400 flex flex-wrap gap-3 mt-1">
                <span className={prefillMeta.has_mastery_data ? 'text-green-400' : 'text-yellow-400'}>
                  {prefillMeta.has_mastery_data ? '✓ Skill mastery from quiz history' : '⚠ No quiz history — using defaults'}
                </span>
                <span className={prefillMeta.has_activity_data ? 'text-green-400' : 'text-yellow-400'}>
                  {prefillMeta.has_activity_data ? '✓ Context from activity logs' : '⚠ No activity data — using defaults'}
                </span>
                <span className={prefillMeta.has_saved_goal ? 'text-green-400' : 'text-yellow-400'}>
                  {prefillMeta.has_saved_goal ? '✓ Goal loaded from saved profile' : '⚠ No saved goal — please enter one'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Student loading indicator */}
        {user?.role === 'STUDENT' && autoLoading && (
          <div className="flex items-center gap-2 text-sm text-primary-400">
            <RefreshCw className="h-4 w-4 animate-spin" />
            Loading your data from quiz history and activity logs...
          </div>
        )}

        {/* Goal text */}
        <div>
          <label className="block text-sm text-gray-300 mb-1">
            Learning Goal
            {prefillMeta?.has_saved_goal && (
              <span className="ml-2 text-xs text-green-400">✓ loaded from saved profile</span>
            )}
          </label>
          <textarea
            className="input-field resize-none h-20"
            placeholder='e.g. "I want to become a frontend developer within 6 months"'
            value={form.goal_text}
            onChange={e => setForm(prev => ({ ...prev, goal_text: e.target.value }))}
            required
          />
        </div>

        {/* Skill mastery sliders */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-2">
              <Layers className="h-4 w-4 text-primary-400" /> Skill Mastery Levels
            </h3>
            {prefillMeta?.has_mastery_data && (
              <span className="text-xs text-green-400">✓ auto-filled from quiz history</span>
            )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SliderField label="HTML"             name="html_mastery"    value={form.html_mastery}    onChange={handleSlider} />
            <SliderField label="CSS"              name="css_mastery"     value={form.css_mastery}     onChange={handleSlider} />
            <SliderField label="JavaScript"       name="js_mastery"      value={form.js_mastery}      onChange={handleSlider} />
            <SliderField label="React"            name="react_mastery"   value={form.react_mastery}   onChange={handleSlider} />
            <SliderField label="Python"           name="python_mastery"  value={form.python_mastery}  onChange={handleSlider} />
            <SliderField label="Machine Learning" name="ml_mastery"      value={form.ml_mastery}      onChange={handleSlider} />
            <SliderField label="DSA"              name="dsa_mastery"     value={form.dsa_mastery}     onChange={handleSlider} />
          </div>
        </div>

        {/* Context */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-2">
              <BrainCircuit className="h-4 w-4 text-primary-400" /> Learning Context
            </h3>
            {prefillMeta?.has_activity_data && (
              <span className="text-xs text-green-400">✓ auto-filled from activity & reflection data</span>
            )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Environment</label>
              <select
                className="input-field"
                value={form.environment}
                onChange={e => setForm(prev => ({ ...prev, environment: e.target.value }))}
              >
                {ENVIRONMENTS.map(env => (
                  <option key={env} value={env}>{env.charAt(0).toUpperCase() + env.slice(1)}</option>
                ))}
              </select>
            </div>
            <SliderField label="Engagement Score"               name="engagement_score"  value={form.engagement_score}  onChange={handleSlider} />
            <SliderField label="Consistency Score"              name="consistency_score" value={form.consistency_score} onChange={handleSlider} />
            <SliderField label="Integrity Score"                name="integrity_score"   value={form.integrity_score}   onChange={handleSlider} />
            <SliderField label="Anomaly Score (lower is better)" name="anomaly_score"   value={form.anomaly_score}     onChange={handleSlider} />
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap gap-3 pt-2">
          <button type="submit" className="btn-primary flex-1" disabled={loading || autoLoading}>
            {loading ? 'Analyzing...' : 'Run Goal Alignment Analysis'}
          </button>
          <button
            type="button"
            onClick={() => autoFetchAll(targetStudentId)}
            disabled={autoLoading || !targetStudentId}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-primary-500/10 border border-primary-500/30 text-primary-400 hover:bg-primary-500/20 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`h-4 w-4 ${autoLoading ? 'animate-spin' : ''}`} />
            Refresh Data
          </button>
          <button
            type="button"
            onClick={() => { setForm(defaultForm); setResult(null); setError(''); setPrefillMeta(null); }}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-gray-500/10 border border-gray-500/30 text-gray-400 hover:bg-gray-500/20 transition-colors"
          >
            <RotateCcw className="h-4 w-4" /> Reset
          </button>
        </div>
      </form>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/50 text-red-400 rounded-lg text-sm flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 shrink-0" /> {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 animate-fade-in">

          {/* Top metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass-card p-4 text-center border-t-4 border-t-primary-500">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Alignment Score</p>
              <p className="text-2xl font-bold text-white">{(result.alignment_score * 100).toFixed(1)}%</p>
            </div>
            <div className="glass-card p-4 text-center border-t-4 border-t-blue-500">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Skill Gap</p>
              <p className="text-2xl font-bold text-white">{(result.skill_gap * 100).toFixed(1)}%</p>
            </div>
            <div className="glass-card p-4 text-center border-t-4 border-t-purple-500">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Confidence</p>
              <p className="text-2xl font-bold text-white">{(result.confidence_score * 100).toFixed(1)}%</p>
            </div>
            <div className="glass-card p-4 text-center border-t-4 border-t-yellow-500">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Collaboration</p>
              <p className="text-2xl font-bold text-white">{(result.collaboration_score * 100).toFixed(1)}%</p>
            </div>
          </div>

          {/* Domain + Scaffold + Goal type */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card p-5">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">Predicted Domain</p>
              <p className={`text-xl font-bold capitalize ${DOMAIN_COLORS[result.predicted_domain] || 'text-white'}`}>
                {result.predicted_domain.replace('_', ' ')}
              </p>
            </div>
            <div className={`glass-card p-5 border ${SCAFFOLD_COLORS[result.scaffold_level]}`}>
              <p className="text-xs uppercase tracking-wider mb-2 opacity-70">Scaffold Level</p>
              <p className="text-xl font-bold capitalize">{result.scaffold_level}</p>
              <p className="text-xs mt-1 opacity-60">
                {result.scaffold_level === 'low' ? 'Advanced — less guidance needed'
                  : result.scaffold_level === 'high' ? 'Beginner — more guidance needed'
                  : 'Intermediate — standard guidance'}
              </p>
            </div>
            <div className="glass-card p-5">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">Goal Type</p>
              <p className="text-xl font-bold text-white capitalize">{result.goal_type}</p>
              <p className="text-xs text-gray-400 mt-1">Specificity: {(result.goal_specificity_score * 100).toFixed(0)}%</p>
            </div>
          </div>

          {/* Recommendation */}
          <div className={`glass-card p-5 border ${result.integrity_flag ? 'border-yellow-500/50 bg-yellow-500/5' : 'border-primary-500/30 bg-primary-500/5'}`}>
            <div className="flex items-start gap-3">
              {result.integrity_flag
                ? <AlertTriangle className="h-5 w-5 text-yellow-400 shrink-0 mt-0.5" />
                : <CheckCircle className="h-5 w-5 text-primary-400 shrink-0 mt-0.5" />
              }
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">AI Recommendation</p>
                <p className="text-white font-semibold text-lg">{result.recommendation}</p>
                {result.integrity_flag && (
                  <p className="text-yellow-400 text-xs mt-1">⚠️ Confidence reduced due to anomalous activity detected</p>
                )}
              </div>
            </div>
          </div>

          {/* Learning path + Resources */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2 uppercase tracking-wider">
                <Target className="h-4 w-4 text-primary-400" /> Learning Path
              </h3>
              <ol className="space-y-2">
                {result.learning_path.map((step, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-gray-300">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-500/20 text-primary-400 text-xs flex items-center justify-center font-bold">
                      {i + 1}
                    </span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2 uppercase tracking-wider">
                <BookOpen className="h-4 w-4 text-blue-400" /> Suggested Resources
              </h3>
              <ul className="space-y-2">
                {result.resources.map((res, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                    <span className="text-blue-400 mt-0.5">→</span> {res}
                  </li>
                ))}
              </ul>
              <p className="text-xs text-gray-500 mt-3">
                Mode: <span className="text-gray-300 capitalize">{result.learning_mode_hint}</span>
              </p>
            </div>
          </div>

          {/* Skill gap radar */}
          {radarData.length > 0 && (
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider flex items-center gap-2">
                <Layers className="h-4 w-4 text-purple-400" /> Skill Gap Breakdown
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="#374151" />
                      <PolarAngleAxis dataKey="skill" tick={{ fill: '#9CA3AF', fontSize: 11 }} />
                      <Radar name="Gap"     dataKey="gap"     stroke="#ef4444" fill="#ef4444" fillOpacity={0.3} />
                      <Radar name="Mastery" dataKey="mastery" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff', borderRadius: '0.5rem' }}
                        formatter={(val: any, name: any) => [`${val}%`, name]}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-3">
                  {Object.entries(result.skill_gap_vector)
                    .sort((a, b) => b[1] - a[1])
                    .map(([skill, gap]) => (
                      <div key={skill}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-gray-300">{skill.replace('_mastery', '').replace('_', ' ')}</span>
                          <span className={gap > 0.5 ? 'text-red-400' : gap > 0.25 ? 'text-yellow-400' : 'text-green-400'}>
                            {(gap * 100).toFixed(0)}% gap
                          </span>
                        </div>
                        <div className="w-full bg-dark-bg rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full ${gap > 0.5 ? 'bg-red-500' : gap > 0.25 ? 'bg-yellow-500' : 'bg-green-500'}`}
                            style={{ width: `${gap * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* Domain scores */}
          <div className="glass-card p-5">
            <button
              className="w-full flex items-center justify-between text-sm font-semibold text-white uppercase tracking-wider"
              onClick={() => setShowDomainScores(v => !v)}
            >
              <span className="flex items-center gap-2">
                <Compass className="h-4 w-4 text-yellow-400" /> All Domain Alignment Scores
              </span>
              {showDomainScores ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
            {showDomainScores && (
              <div className="mt-4 space-y-2">
                {domainData.map(({ domain, score }) => (
                  <div key={domain}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className={`capitalize font-medium ${DOMAIN_COLORS[domain] || 'text-gray-300'}`}>
                        {domain.replace('_', ' ')}
                      </span>
                      <span className="text-white">{score}%</span>
                    </div>
                    <div className="w-full bg-dark-bg rounded-full h-2">
                      <div className="h-2 rounded-full bg-primary-500" style={{ width: `${score}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Behavior summary + explanation */}
          <div className="glass-card p-5 space-y-3">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Behavior Summary</h3>
            <p className="text-sm text-gray-300 font-mono bg-dark-bg/50 p-3 rounded-lg">{result.behavior_summary}</p>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider pt-2">Full Explanation</h3>
            <p className="text-sm text-gray-300 font-mono bg-dark-bg/50 p-3 rounded-lg">{result.explanation}</p>
          </div>

        </div>
      )}
    </div>
  );
};

export default GoalAlignment;
