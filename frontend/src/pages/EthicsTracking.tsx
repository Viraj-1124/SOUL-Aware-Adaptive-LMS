import React, { useEffect, useState, useCallback } from 'react';
import { fetchEthicalProfile, type EthicalProfile } from '../api/alerts';
import { Award, AlertTriangle, TrendingUp, Loader } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const EthicsTracking: React.FC = () => {
  const { user } = useAuth();
  const studentId = user?.id || 1;
  const [profile, setProfile] = useState<EthicalProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const loadProfile = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchEthicalProfile(studentId);
      setProfile(data);
    } catch (err) {
      console.error('Failed to load ethical profile:', err);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader className="w-8 h-8 text-blue-500 animate-spin" />
        <span className="ml-3 text-gray-600">Loading profile...</span>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Failed to load ethical profile</p>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getProgressBarColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Responsible Learning Profile</h1>
      <p className="text-gray-600 mb-8">
        Track your commitment to ethical learning practices and academic integrity
      </p>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Academic Integrity */}
        <div className={`rounded-lg border-2 p-6 ${getScoreBg(profile.academic_integrity_score)}`}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-900">Academic Integrity</h3>
            <Award className="w-5 h-5 text-gray-600" />
          </div>
          <div className={`text-3xl font-bold ${getScoreColor(profile.academic_integrity_score)} mb-3`}>
            {profile.academic_integrity_score.toFixed(0)}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getProgressBarColor(profile.academic_integrity_score)}`}
              style={{ width: `${profile.academic_integrity_score}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-3">
            {profile.integrity_flags > 0
              ? `${profile.integrity_flags} flagged item(s)`
              : 'No flags'}
          </p>
        </div>

        {/* Collaboration Fairness */}
        <div className={`rounded-lg border-2 p-6 ${getScoreBg(profile.collaboration_fairness_score)}`}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-900">Collaboration Fairness</h3>
            <TrendingUp className="w-5 h-5 text-gray-600" />
          </div>
          <div className={`text-3xl font-bold ${getScoreColor(profile.collaboration_fairness_score)} mb-3`}>
            {profile.collaboration_fairness_score.toFixed(0)}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getProgressBarColor(profile.collaboration_fairness_score)}`}
              style={{ width: `${profile.collaboration_fairness_score}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-3">
            {profile.collaboration_violations > 0
              ? `${profile.collaboration_violations} violation(s)`
              : 'Compliant'}
          </p>
        </div>

        {/* Self-Regulation */}
        <div className={`rounded-lg border-2 p-6 ${getScoreBg(profile.self_regulation_score)}`}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-900">Self-Regulation</h3>
            <Award className="w-5 h-5 text-gray-600" />
          </div>
          <div className={`text-3xl font-bold ${getScoreColor(profile.self_regulation_score)} mb-3`}>
            {profile.self_regulation_score.toFixed(0)}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getProgressBarColor(profile.self_regulation_score)}`}
              style={{ width: `${profile.self_regulation_score}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-3">
            {profile.self_plagiarism_detected ? 'Plagiarism detected' : 'Original work'}
          </p>
        </div>

        {/* Overall Responsibility */}
        <div className={`rounded-lg border-2 p-6 ${getScoreBg(profile.responsibility_index)}`}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-900">Responsibility Index</h3>
            <Award className="w-5 h-5 text-gray-600" />
          </div>
          <div className={`text-3xl font-bold ${getScoreColor(profile.responsibility_index)} mb-3`}>
            {profile.responsibility_index.toFixed(0)}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getProgressBarColor(profile.responsibility_index)}`}
              style={{ width: `${profile.responsibility_index}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-3">Overall ethical learning index</p>
        </div>
      </div>

      {/* Violations Section */}
      {(profile.integrity_flags > 0 || profile.collaboration_violations > 0 || profile.self_plagiarism_detected) && (
        <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg mb-8">
          <div className="flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-red-900">Attention Required</h3>
              <ul className="list-disc list-inside text-red-800 mt-3 space-y-2">
                {profile.integrity_flags > 0 && (
                  <li>You have {profile.integrity_flags} academic integrity flag(s)</li>
                )}
                {profile.collaboration_violations > 0 && (
                  <li>You have {profile.collaboration_violations} collaboration violation(s)</li>
                )}
                {profile.self_plagiarism_detected && (
                  <li>Self-plagiarism was detected in your submissions</li>
                )}
              </ul>
              <p className="text-red-800 mt-4">
                Please review the Ethical Learning Guidelines and take corrective action. Your educator may reach out to discuss.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Guidelines */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Ethical Learning Standards</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-lg text-gray-900 mb-3">✓ Best Practices</h3>
            <ul className="space-y-2 text-gray-700">
              <li>• Complete your own work unless collaboration is explicitly allowed</li>
              <li>• Cite all sources and references properly</li>
              <li>• Ask for help when needed</li>
              <li>• Attend sessions regularly and engage authentically</li>
              <li>• Report technical difficulties or concerns to educators</li>
              <li>• Respect others' intellectual property</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-lg text-gray-900 mb-3">✗ Behaviors to Avoid</h3>
            <ul className="space-y-2 text-gray-700">
              <li>• Submitting others' work as your own</li>
              <li>• Reusing past assignments without permission</li>
              <li>• Unauthorized collaboration</li>
              <li>• Using unauthorized resources during assessments</li>
              <li>• Fabricating citations or data</li>
              <li>• Misrepresenting your understanding</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Last Violation */}
      {profile.last_violation_at && (
        <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-600">
            <span className="font-semibold">Last Violation:</span> {new Date(profile.last_violation_at).toLocaleDateString()}
          </p>
          {profile.intervention_sent && (
            <p className="text-sm text-blue-600 mt-2">
              ℹ️ An intervention message was sent regarding this matter.
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default EthicsTracking;
