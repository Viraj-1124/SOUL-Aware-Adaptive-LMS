import React, { useEffect, useState, useCallback } from 'react';
import { fetchStudentAlerts, acknowledgeAlert, type Alert } from '../api/alerts';
import { AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Alerts: React.FC = () => {
  const { user } = useAuth();
  const studentId = user?.id || 1;
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAlerts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchStudentAlerts(studentId);
      setAlerts(data);
      setError(null);
    } catch (err) {
      setError('Failed to load alerts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  const handleAcknowledge = async (alertId: number) => {
    try {
      await acknowledgeAlert(alertId, studentId);
      setAlerts(alerts.filter(a => a.id !== alertId));
    } catch (err) {
      setError('Failed to acknowledge alert');
      console.error(err);
    }
  };

  const getSeverityBadgeColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800';
      case 'LOW':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    if (severity === 'CRITICAL' || severity === 'HIGH') {
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
    return <CheckCircle className="w-5 h-5 text-blue-500" />;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Alerts & Notifications</h1>
          <p className="text-gray-600 mt-2">
            Stay informed about your learning progress and well-being
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader className="w-8 h-8 text-blue-500 animate-spin" />
            <span className="ml-3 text-gray-600">Loading alerts...</span>
          </div>
        ) : alerts.length === 0 ? (
          <div className="text-center py-12">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">All clear!</h3>
            <p className="text-gray-600 mt-2">You have no pending alerts</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Alerts List */}
            {alerts.map(alert => (
              <div
                key={alert.id}
                className="bg-white rounded-lg shadow p-6 border-l-4"
                style={{
                  borderLeftColor: alert.severity === 'CRITICAL' ? '#ef4444' : 
                                  alert.severity === 'HIGH' ? '#f97316' :
                                  alert.severity === 'MEDIUM' ? '#eab308' : '#3b82f6'
                }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    {getSeverityIcon(alert.severity)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {alert.title}
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityBadgeColor(alert.severity)}`}>
                          {alert.severity}
                        </span>
                      </div>
                      <p className="text-gray-700 mt-2">{alert.message}</p>
                      {alert.metric_value !== null && (
                        <div className="mt-3 p-3 bg-gray-50 rounded">
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Current Value:</span> {alert.metric_value.toFixed(2)}
                          </p>
                        </div>
                      )}
                      <p className="text-sm text-gray-500 mt-3">
                        {new Date(alert.created_at).toLocaleDateString()} at {new Date(alert.created_at).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleAcknowledge(alert.id)}
                    className="ml-4 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg transition-colors text-sm font-medium"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Info Box */}
        <div className="mt-12 p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-900">How Alerts Work</h3>
          <ul className="list-disc list-inside text-blue-800 mt-3 space-y-2">
            <li><strong>Moral Fatigue Alerts:</strong> Notifies you when fatigue signals are detected</li>
            <li><strong>Engagement Warnings:</strong> Helps you stay on track with consistent engagement</li>
            <li><strong>Performance Trends:</strong> Alerts about significant changes in your scores</li>
            <li><strong>Motivation Check-ins:</strong> Reminds you to reflect on your learning goals</li>
            <li><strong>Cognitive Load:</strong> Suggests taking breaks when workload is high</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Alerts;
