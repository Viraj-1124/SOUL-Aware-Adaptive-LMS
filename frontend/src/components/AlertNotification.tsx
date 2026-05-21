import React, { useEffect, useState, useCallback } from 'react';
import { AlertCircle, CheckCircle, XCircle, Info } from 'lucide-react';
import { fetchStudentAlerts, acknowledgeAlert as apiAcknowledgeAlert, type Alert } from '../api/alerts';

interface AlertNotificationProps {
  studentId: number;
  onAlertUpdate?: (alerts: Alert[]) => void;
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'CRITICAL':
      return 'bg-red-50 border-l-4 border-red-500 text-red-900';
    case 'HIGH':
      return 'bg-orange-50 border-l-4 border-orange-500 text-orange-900';
    case 'MEDIUM':
      return 'bg-yellow-50 border-l-4 border-yellow-500 text-yellow-900';
    case 'LOW':
      return 'bg-blue-50 border-l-4 border-blue-500 text-blue-900';
    default:
      return 'bg-gray-50 border-l-4 border-gray-500 text-gray-900';
  }
};

const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case 'CRITICAL':
    case 'HIGH':
      return <AlertCircle className="w-5 h-5" />;
    case 'MEDIUM':
      return <Info className="w-5 h-5" />;
    case 'LOW':
      return <CheckCircle className="w-5 h-5" />;
    default:
      return <Info className="w-5 h-5" />;
  }
};

export const AlertNotification: React.FC<AlertNotificationProps> = ({ studentId, onAlertUpdate }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchAlerts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchStudentAlerts(studentId, true);
      setAlerts(data);
      onAlertUpdate?.(data);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  }, [studentId, onAlertUpdate]);

  useEffect(() => {
    fetchAlerts();
    // Poll every 30 seconds
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, [fetchAlerts]);

  const handleAcknowledge = async (alertId: number) => {
    try {
      const data = await apiAcknowledgeAlert(alertId, studentId);
      if (data) {
        setAlerts(alerts.filter(a => a.id !== alertId));
        onAlertUpdate?.(alerts.filter(a => a.id !== alertId));
      }
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  if (loading && alerts.length === 0) {
    return null;
  }

  if (alerts.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 space-y-2 max-w-md z-50">
      {alerts.map(alert => (
        <div
          key={alert.id}
          className={`p-4 rounded shadow-lg ${getSeverityColor(alert.severity)}`}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3 flex-1">
              <div className="flex-shrink-0 mt-0.5">
                {getSeverityIcon(alert.severity)}
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-sm">{alert.title}</h3>
                <p className="text-sm mt-1">{alert.message}</p>
                {alert.metric_value !== null && (
                  <p className="text-xs mt-2 opacity-75">
                    Current value: {alert.metric_value.toFixed(2)}
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={() => handleAcknowledge(alert.id)}
              className="flex-shrink-0 text-sm font-medium hover:opacity-75 transition-opacity"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AlertNotification;
