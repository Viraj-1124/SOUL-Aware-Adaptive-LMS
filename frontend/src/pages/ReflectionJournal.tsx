import React, { useEffect, useState, useCallback } from 'react';
import { fetchStudentPrompts, submitReflection, type ReflectionPrompt } from '../api/alerts';
import { BookOpen, Send, CheckCircle, Loader } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const ReflectionJournal: React.FC = () => {
  const { user } = useAuth();
  const studentId = user?.id || 1;
  const [prompts, setPrompts] = useState<ReflectionPrompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [responses, setResponses] = useState<{ [key: number]: string }>({});
  const [submitting, setSubmitting] = useState(false);

  const loadPrompts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchStudentPrompts(studentId);
      setPrompts(data);
    } catch (err) {
      console.error('Failed to load prompts:', err);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    loadPrompts();
  }, [loadPrompts]);

  const handleResponseChange = (promptId: number, value: string) => {
    setResponses(prev => ({
      ...prev,
      [promptId]: value
    }));
  };

  const handleSubmitReflection = async (promptId: number) => {
    const response = responses[promptId];
    if (!response || response.trim().length === 0) {
      alert('Please write a reflection before submitting');
      return;
    }

    try {
      setSubmitting(true);
      await submitReflection(promptId, response);
      loadPrompts();
      setResponses(prev => ({ ...prev, [promptId]: '' }));
    } catch (err) {
      console.error('Failed to submit reflection:', err);
      alert('Failed to submit reflection');
    } finally {
      setSubmitting(false);
    }
  };

  const getContextColor = (context: string) => {
    switch (context) {
      case 'SKILL_GAP':
        return 'bg-blue-100 text-blue-800';
      case 'FATIGUE':
        return 'bg-red-100 text-red-800';
      case 'MOTIVATION':
        return 'bg-green-100 text-green-800';
      case 'PERFORMANCE':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader className="w-8 h-8 text-blue-500 animate-spin" />
        <span className="ml-3 text-gray-600">Loading prompts...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Reflection Journal</h1>
      <p className="text-gray-600 mb-8">
        Take a moment to reflect on your learning journey. These prompts help you develop deeper insights and self-awareness.
      </p>

      {prompts.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No reflection prompts yet</p>
        </div>
      ) : (
        <div className="space-y-6">
          {prompts.map(prompt => (
            <div key={prompt.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getContextColor(prompt.context)} mb-3`}>
                      {prompt.context}
                    </span>
                    <h3 className="text-lg font-semibold text-gray-900 mt-2">
                      {prompt.prompt_text}
                    </h3>
                  </div>
                  {prompt.response_submitted_at && (
                    <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                  )}
                </div>

                {prompt.response ? (
                  // Show submitted response
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <p className="text-sm text-gray-600 mb-2">Your Reflection:</p>
                    <p className="text-gray-900 text-sm leading-relaxed">{prompt.response}</p>
                    {prompt.reflection_depth_score !== null && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Reflection Quality Score:</span>
                          <span className="font-semibold text-blue-600">
                            {(prompt.reflection_depth_score * 100).toFixed(0)}/100
                          </span>
                        </div>
                      </div>
                    )}
                    {prompt.sentiment !== null && (
                      <div className="flex items-center justify-between text-sm mt-2">
                        <span className="text-gray-600">Sentiment:</span>
                        <span className="font-semibold text-gray-700">
                          {prompt.sentiment > 0 ? '😊 Positive' : prompt.sentiment < 0 ? '😔 Negative' : '😐 Neutral'}
                        </span>
                      </div>
                    )}
                  </div>
                ) : (
                  // Show response input
                  <div className="space-y-4">
                    <textarea
                      value={responses[prompt.id] || ''}
                      onChange={(e) => handleResponseChange(prompt.id, e.target.value)}
                      placeholder="Write your reflection here... (minimum 50 characters for better analysis)"
                      className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      rows={6}
                      disabled={submitting}
                    />
                    <button
                      onClick={() => handleSubmitReflection(prompt.id)}
                      disabled={submitting || !responses[prompt.id]}
                      className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      {submitting ? 'Submitting...' : 'Submit Reflection'}
                    </button>
                  </div>
                )}

                {/* Meta Information */}
                <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between text-sm text-gray-600">
                  <span>
                    Asked on {new Date(prompt.response_submitted_at || prompt.generated_at || new Date().toISOString()).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div className="mt-12 p-6 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-900">Benefits of Reflection</h3>
        <ul className="list-disc list-inside text-blue-800 mt-3 space-y-2">
          <li><strong>Deeper Learning:</strong> Reflecting helps consolidate knowledge</li>
          <li><strong>Self-Awareness:</strong> Understand your learning patterns</li>
          <li><strong>Goal Alignment:</strong> Connect learning to your purpose</li>
          <li><strong>Metacognition:</strong> Think about how you learn</li>
          <li><strong>Motivation:</strong> Find meaning in your studies</li>
        </ul>
      </div>
    </div>
  );
};

export default ReflectionJournal;
