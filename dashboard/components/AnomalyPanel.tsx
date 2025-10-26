'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { getAnomalies } from '@/lib/api';

export default function AnomalyPanel() {
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnomalies();
    const interval = setInterval(loadAnomalies, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadAnomalies = async () => {
    try {
      const data = await getAnomalies(60);
      setAnomalies(data.slice(0, 5)); // Top 5
      setLoading(false);
    } catch (error) {
      console.error('Error loading anomalies:', error);
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-purple-100 text-purple-800 border-purple-200',
      high: 'bg-red-100 text-red-800 border-red-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      low: 'bg-blue-100 text-blue-800 border-blue-200',
    };
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Detected Anomalies</h3>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-orange-500" />
          Detected Anomalies
        </h3>
        <span className="text-xs text-gray-500">Last 60 minutes</span>
      </div>

      {anomalies.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p className="text-sm">No anomalies detected</p>
          <p className="text-xs mt-1">System operating normally ✓</p>
        </div>
      ) : (
        <div className="space-y-3">
          {anomalies.map((anomaly, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getSeverityColor(anomaly.severity)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {anomaly.anomaly_type === 'spike' ? (
                      <TrendingUp className="w-4 h-4" />
                    ) : (
                      <TrendingDown className="w-4 h-4" />
                    )}
                    <span className="font-medium text-sm capitalize">
                      {anomaly.anomaly_type}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-white bg-opacity-50">
                      {anomaly.severity}
                    </span>
                  </div>
                  <p className="text-sm">{anomaly.description}</p>
                  <div className="flex items-center gap-4 mt-2 text-xs">
                    <span>Actual: <strong>{anomaly.actual_value.toFixed(0)}</strong></span>
                    <span>Expected: <strong>{anomaly.expected_value.toFixed(0)}</strong></span>
                    <span>Deviation: <strong>{anomaly.deviation_percent.toFixed(1)}%</strong></span>
                  </div>
                </div>
                <div className="text-right text-xs text-gray-500">
                  {new Date(anomaly.detected_at).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
