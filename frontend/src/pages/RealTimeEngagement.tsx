import React, { useEffect, useState, useCallback } from 'react';
import { fetchEngagementSnapshots, fetchEngagementTrend, type EngagementSnapshot } from '../api/alerts';
import { Activity, TrendingUp, Loader, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { coursesApi } from '../api/courses';

const RealTimeEngagement: React.FC = () => {
  const { user } = useAuth();
  const studentId = user?.id || 1;
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<number>(1);
  const [snapshots, setSnapshots] = useState<EngagementSnapshot[]>([]);
  const [trend, setTrend] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isAutoRefresh, setIsAutoRefresh] = useState(true);

  useEffect(() => {
    const loadCourses = async () => {
      try {
        const data = await coursesApi.getCourses();
        setCourses(data);
        if (data.length > 0) {
          setSelectedCourseId(data[0].id);
        }
      } catch (err) {
        console.error('Failed to load courses:', err);
      }
    };
    loadCourses();
  }, []);

  const loadEngagementData = useCallback(async () => {
    if (!selectedCourseId) return;
    try {
      setLoading(true);
      const snapshotsData = await fetchEngagementSnapshots(studentId, selectedCourseId, 24);
      const trendData = await fetchEngagementTrend(studentId, selectedCourseId, 7);
      
      setSnapshots(snapshotsData);
      setTrend(trendData);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to load engagement data:', err);
    } finally {
      setLoading(false);
    }
  }, [studentId, selectedCourseId]);

  useEffect(() => {
    loadEngagementData();
  }, [loadEngagementData]);

  useEffect(() => {
    if (!isAutoRefresh) return;

    const interval = setInterval(() => {
      loadEngagementData();
    }, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, [isAutoRefresh, loadEngagementData]);

  const getTrendIcon = (trend: string) => {
    if (trend === 'INCREASING') {
      return <TrendingUp className="w-5 h-5 text-green-500" />;
    } else if (trend === 'DECREASING') {
      return <TrendingUp className="w-5 h-5 text-red-500 transform rotate-180" />;
    }
    return <Activity className="w-5 h-5 text-blue-500" />;
  };

  const getTrendColor = (trend: string) => {
    if (trend === 'INCREASING') return 'text-green-600';
    if (trend === 'DECREASING') return 'text-red-600';
    return 'text-blue-600';
  };

  const getTrendBgColor = (trend: string) => {
    if (trend === 'INCREASING') return 'bg-green-50';
    if (trend === 'DECREASING') return 'bg-red-50';
    return 'bg-blue-50';
  };

  const currentSnapshot = snapshots[0];
  const avgEngagement = trend?.average_engagement || 0;

  const getEngagementColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    if (score >= 40) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  if (loading && snapshots.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader className="w-8 h-8 text-blue-500 animate-spin" />
        <span className="ml-3 text-gray-600">Loading engagement metrics...</span>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Real-Time Engagement Dashboard</h1>
          <p className="text-gray-400 mt-2">Monitor your learning engagement</p>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          {courses.length > 0 && (
            <div className="flex items-center gap-2">
              <label htmlFor="course-select" className="text-sm font-medium text-gray-300">Course:</label>
              <select
                id="course-select"
                value={selectedCourseId}
                onChange={(e) => setSelectedCourseId(Number(e.target.value))}
                className="bg-dark-card border border-dark-border text-white rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-primary-500"
              >
                {courses.map(course => (
                  <option key={course.id} value={course.id}>
                    {course.title}
                  </option>
                ))}
              </select>
            </div>
          )}
          <button
            onClick={() => loadEngagementData()}
            className="p-2 hover:bg-white/5 rounded-lg transition-colors"
            title="Refresh data"
          >
            <RefreshCw className={`w-5 h-5 text-gray-400 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <label className="flex items-center gap-2 text-sm text-gray-300">
            <input
              type="checkbox"
              checked={isAutoRefresh}
              onChange={(e) => setIsAutoRefresh(e.target.checked)}
              className="rounded bg-dark-card border-dark-border text-primary-500 focus:ring-0 focus:ring-offset-0"
            />
            Auto-refresh
          </label>
          {lastUpdate && (
            <span className="text-xs text-gray-400">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Current Engagement */}
      {currentSnapshot && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* Current Engagement Score */}
          <div className={`rounded-lg border-2 p-6 ${getEngagementColor(currentSnapshot.engagement_score)}`}>
            <p className="text-sm font-medium text-gray-600 mb-2">Current Engagement Score</p>
            <div className="text-4xl font-bold mb-2">{currentSnapshot.engagement_score.toFixed(1)}</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${currentSnapshot.engagement_score}%` }}
              ></div>
            </div>
          </div>

          {/* Activity Count */}
          <div className="rounded-lg border-2 border-blue-200 bg-blue-50 p-6">
            <p className="text-sm font-medium text-gray-600 mb-2">Recent Activities</p>
            <div className="text-4xl font-bold text-blue-600 mb-2">{currentSnapshot.activity_count}</div>
            <p className="text-sm text-gray-600">Last hour</p>
          </div>

          {/* Response Time */}
          <div className="rounded-lg border-2 border-purple-200 bg-purple-50 p-6">
            <p className="text-sm font-medium text-gray-600 mb-2">Avg Response Time</p>
            <div className="text-4xl font-bold text-purple-600 mb-2">
              {currentSnapshot.engagement_score > 0 ? (100 - currentSnapshot.engagement_score).toFixed(1) : '0'}
            </div>
            <p className="text-sm text-gray-600">seconds</p>
          </div>

          {/* Trend */}
          <div className={`rounded-lg border-2 p-6 ${getTrendBgColor(currentSnapshot.engagement_trend)}`}>
            <p className="text-sm font-medium text-gray-600 mb-2">Trend</p>
            <div className="flex items-center gap-2 mb-2">
              {getTrendIcon(currentSnapshot.engagement_trend)}
              <span className={`text-lg font-bold ${getTrendColor(currentSnapshot.engagement_trend)}`}>
                {currentSnapshot.engagement_trend}
              </span>
            </div>
            <p className="text-sm text-gray-600">7-day trend</p>
          </div>
        </div>
      )}

      {/* Average Engagement */}
      {trend && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">7-Day Average</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-2">Average Engagement Score</p>
              <div className="text-3xl font-bold text-blue-600 mb-3">{avgEngagement.toFixed(1)}/100</div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-500 h-3 rounded-full"
                  style={{ width: `${avgEngagement}%` }}
                ></div>
              </div>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-2">Engagement Quality</p>
              <div className="text-3xl font-bold mb-3">
                {avgEngagement >= 80 ? '🌟 Excellent' :
                 avgEngagement >= 60 ? '👍 Good' :
                 avgEngagement >= 40 ? '⚠️ Fair' : '❌ Needs Improvement'}
              </div>
              <p className="text-sm text-gray-600">
                {avgEngagement >= 80
                  ? 'Keep up the excellent engagement!'
                  : avgEngagement >= 60
                  ? 'Good progress! Try to increase engagement.'
                  : avgEngagement >= 40
                  ? 'Your engagement is declining. Consider reaching out for support.'
                  : 'Your engagement needs immediate attention. Contact your educator.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Engagement Timeline */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">24-Hour Timeline</h2>
        {snapshots.length === 0 ? (
          <p className="text-gray-600 text-center py-8">No engagement data available</p>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {snapshots.map((snapshot) => (
              <div key={snapshot.id} className="flex items-center gap-4 pb-3 border-b border-gray-100 last:border-0">
                <div className="w-32 text-sm text-gray-600 flex-shrink-0">
                  {new Date(snapshot.timestamp).toLocaleTimeString()}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      Engagement: {snapshot.engagement_score.toFixed(1)}
                    </span>
                    <span className="text-xs text-gray-500">
                      {snapshot.activity_count} activities
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${snapshot.engagement_score}%` }}
                    ></div>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    {getTrendIcon(snapshot.engagement_trend)}
                    <span className={`text-xs font-medium ${getTrendColor(snapshot.engagement_trend)}`}>
                      {snapshot.engagement_trend}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recommendations */}
      <div className="mt-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-900">📊 Engagement Tips</h3>
        <ul className="list-disc list-inside text-blue-800 mt-3 space-y-2">
          <li>Try to maintain consistent daily engagement for better learning outcomes</li>
          <li>Shorter, regular sessions are more effective than marathon study sessions</li>
          <li>Take breaks every 25-30 minutes to maintain focus (Pomodoro technique)</li>
          <li>Track when you're most engaged and schedule important activities then</li>
          <li>If engagement is dropping, reach out to your educator or support team</li>
        </ul>
      </div>
    </div>
  );
};

export default RealTimeEngagement;
