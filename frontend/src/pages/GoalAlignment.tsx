import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { alignmentApi } from '../api/model4_alignment';
import type { GoalAlignmentRequest, GoalAlignmentResponse, MasteryPrefillOut } from '../api/model4_alignment';
import {
  Target, BrainCircuit, AlertTriangle, CheckCircle,
  BookOpen, User as UserIcon, Compass, Layers, ChevronDown, ChevronUp,
  Zap, RotateCcw, History
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
  label, name, value, onChange
}: { label: string; name: string; value: number; onChange: (name: string, val: number) => void }) => (
  <div>
    <div className="flex justify-between text-sm mb-1">
      <span className="text-gray-300">{label}</span>
      <span className="text-white font-medium">{(value * 100).toFixed(0)}%</span>
    </div>
    <input
      type="range" min={0} max={1} step={0.05}
      value={value}
      onChange={e => onChange(name, parseFloat(e.target.value))}
      className="w-full accent-primary-500"
    />
  </div>
);

const GoalAlignment = () => {
  const { user } = useAuth();
  const [form, setForm] = useState<GoalAlignmentRequest>(defaultForm);
  const [studentId, setStudentId] = useState('');
  const [result, setResult] = useState<GoalAlignmentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [prefilling, setPrefilling] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [error, setError] = useState('');
  const [prefillInfo, setPrefillInfo] = useState<MasteryPrefillOut | null>(null);
  const [showDomainScores, setShowDomainScores] = useState(false);

  const targetStudentId = user?.role === 'STUDENT' ? user.id : Number(studentId);

  const handleSlider = (name: string, val: number) => {
    setForm(prev => ({ ...prev, [name]: val }));
  };

  // Auto-fill skill mastery from knowledge tracing
  const handlePrefill = async () => {
    if (!targetStudentId) { setError('Please enter a Student ID first.'); return; }
    setPrefilling(true);
    setError('');
    try {
      const data = await alignmentApi.getMasteryPrefill(targetStudentId);
      if (!data.has_data) {
        setError('No knowledge tracing data found yet. Complete some quizzes first, or set skills manually.');
        return;
      }
      setForm(prev => ({
        ...prev,
        html_mastery:   data.html_mastery,
        css_mastery:    data.css_mastery,
        js_mastery:     data.js_mastery,
        react_mastery:  data.react_mastery,
        python_mastery: data.python_mastery,
        ml_mastery:     data.ml_mastery,
        dsa_mastery:    data.dsa_mastery,
      }));
      setPrefillInfo(data);
    } catch {
      setError('Could not load knowledge tracing data.');
    } finally {
      setPrefilling(false);
    }
  };

  // Load previously saved profile back into the form
  const handleLoadProfile = async () => {
    if (!targetStudentId) { setError('Please enter a Student ID first.'); return; }
    setLoadingProfile(true);
    setError('');
    try {
      const profile = await alignmentApi.getProfile(targetStudentId);
      setForm({
        goal_text:         profile.goal_text,
        html_mastery:      0.5,
        css_mastery:       0.5,
        js_mastery:        0.5,
        react_mastery:     0.3,
        python_mastery:    0.4,
        ml_mastery:        0.2,
        dsa_mastery:       0.3,
        environment:       'online',
        engagement_score:  0.7,
        consistency_score: 0.6,
        integrity_score:   0.9,
        anomaly_score:     0.05,
      });
      // Show the saved result directly
      if (profile.alignment_score !== null) {
        setResult({
          student_id:               profile.student_id,
          goal_text:                profile.goal_text,
          goal_type:                profile.goal_type ?? '',
          goal_specificity_score:   profile.goal_specificity_score ?? 0,
          collaboration_score:      0,
          alignment_score:          profile.alignment_score ?? 0,
          predicted_domain:         profile.predicted_domain ?? '',
          all_domain_scores:        {},
          skill_gap:                profile.skill_gap ?? 0,
          skill_gap_vector:         {},
          weakest_topics:           profile.weakest_topics ?? [],
          context_adjustment_score: 0,
          learning_mode_hint:       profile.learning_mode_hint ?? '',
          integrity_flag:           profile.integrity_flag ?? false,
          scaffold_level:           profile.scaffold_level ?? '',
          behavior_summary:         profile.behavior_summary ?? '',
          recommendation:           profile.recommendation ?? '',
          learning_path:            profile.learning_path ?? [],
          resources:                profile.resources ?? [],
          explanation:              profile.explanation ?? '',
          confidence_score:         profile.confidence_score ?? 0,
        });
      }
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('No saved profile found. Run an analysis first.');
      } else {
        setError(err.response?.data?.detail || 'Could not load saved profile.');
      }
    } finally {
      setLoadingProfile(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetStudentId) { setError('Please enter a Student ID.'); return; }
    setLoading(true);
    setError('');
    setResult(null);
    setPrefillInfo(null);
    try {
      const res = await alignmentApi.analyzeGoal(targetStudentId, form);
      setResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run goal alignment analysis.');
    } finally {
      setLoading(false);
    }
  };

  // Radar chart data from skill gap vector
  const radarData = result
    ? Object.entries(result.skill_gap_vector).map(([key, gap]) => ({
        skill: key.replace('_mastery', '').replace('_', ' ').toUpperCase(),
        gap: Math.round(gap * 100),
        mastery: Math.round((1 - gap) * 100),
      }))
    : [];

  // Domain scores bar data
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
            <label className="block text-sm text-gray-300 mb-1">Student ID</label>
            <div className="relative">
              <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="number" className="input-field pl-9" value={studentId}
                onChange={e => setStudentId(e.target.value)} required
                placeholder="Enter student ID"
              />
            </div>
          </div>
        )}

        {/* Quick action buttons */}
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handlePrefill}
            disabled={prefilling || (!targetStudentId)}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400 hover:bg-blue-500/20 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Zap className="h-4 w-4" />
            {prefilling ? 'Loading...' : 'Auto-fill from Knowledge Tracing'}
          </button>
          <button
            type="button"
            onClick={handleLoadProfile}
            disabled={loadingProfile || (!targetStudentId)}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-400 hover:bg-purple-500/20 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <History className="h-4 w-4" />
            {loadingProfile ? 'Loading...' : 'Load Saved Profile'}
          </button>
          <button
            type="button"
            onClick={() => { setForm(defaultForm); setResult(null); setError(''); setPrefillInfo(null); }}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-gray-500/10 border border-gray-500/30 text-gray-400 hover:bg-gray-500/20 transition-colors"
          >
            <RotateCcw className="h-4 w-4" /> Reset
          </button>
        </div>

        {/* Prefill info banner */}
        {prefillInfo?.has_data && (
          <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg text-xs text-blue-300 flex items-start gap-2">
            <Zap className="h-4 w-4 shrink-0 mt-0.5 text-blue-400" />
            <div>
              <span className="font-semibold">Skills auto-filled from your quiz history.</span>
              {' '}Adjust any values before running the analysis.
            </div>
          </div>
        )}

        {/* Goal text */}
        <div>
          <label className="block text-sm text-gray-300 mb-1">Your Learning Goal</label>
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
          <h3 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wider flex items-center gap-2">
            <Layers className="h-4 w-4 text-primary-400" /> Skill Mastery Levels
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SliderField label="HTML"           name="html_mastery"    value={form.html_mastery}    onChange={handleSlider} />
            <SliderField label="CSS"            name="css_mastery"     value={form.css_mastery}     onChange={handleSlider} />
            <SliderField label="JavaScript"     name="js_mastery"      value={form.js_mastery}      onChange={handleSlider} />
            <SliderField label="React"          name="react_mastery"   value={form.react_mastery}   onChange={handleSlider} />
            <SliderField label="Python"         name="python_mastery"  value={form.python_mastery}  onChange={handleSlider} />
            <SliderField label="Machine Learning" name="ml_mastery"    value={form.ml_mastery}      onChange={handleSlider} />
            <SliderField label="DSA"            name="dsa_mastery"     value={form.dsa_mastery}     onChange={handleSlider} />
          </div>
        </div>

        {/* Context */}
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wider flex items-center gap-2">
            <BrainCircuit className="h-4 w-4 text-primary-400" /> Learning Context
          </h3>
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
            <SliderField label="Engagement Score"  name="engagement_score"  value={form.engagement_score}  onChange={handleSlider} />
            <SliderField label="Consistency Score" name="consistency_score" value={form.consistency_score} onChange={handleSlider} />
            <SliderField label="Integrity Score"   name="integrity_score"   value={form.integrity_score}   onChange={handleSlider} />
            <SliderField label="Anomaly Score (lower is better)" name="anomaly_score" value={form.anomaly_score} onChange={handleSlider} />
          </div>
        </div>

        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? 'Analyzing Goal...' : 'Run Goal Alignment Analysis'}
        </button>
      </form>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/50 text-red-400 rounded-lg text-sm flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 shrink-0" /> {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 animate-fade-in">

          {/* Top metrics row */}
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

          {/* Skill gap radar chart */}
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
                      <Radar name="Gap" dataKey="gap" stroke="#ef4444" fill="#ef4444" fillOpacity={0.3} />
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

          {/* Domain scores (collapsible) */}
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
                      <div
                        className="h-2 rounded-full bg-primary-500"
                        style={{ width: `${score}%` }}
                      />
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
