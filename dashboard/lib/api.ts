import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Search logs
export const searchLogs = async (params: {
  query?: string;
  service?: string;
  level?: string;
  startTime?: string;
  endTime?: string;
  limit?: number;
}) => {
  const response = await api.get('/api/v1/logs/search', { params });
  return response.data;
};

// Get metrics overview
export const getMetricsOverview = async () => {
  const response = await api.get('/api/v1/metrics/overview');
  return response.data;
};

// Get service metrics
export const getServiceMetrics = async (minutes: number = 60) => {
  const response = await api.get('/api/v1/metrics/services', {
    params: { minutes },
  });
  return response.data;
};

// Get log volume over time
export const getLogVolume = async (minutes: number = 60) => {
  const response = await api.get('/api/v1/metrics/log-volume', {
    params: { minutes },
  });
  return response.data;
};

// Get alert rules
export const getAlertRules = async () => {
  const response = await api.get('/api/v1/alerts/rules');
  return response.data;
};

// Get active alerts
export const getActiveAlerts = async () => {
  const response = await api.get('/api/v1/alerts/active');
  return response.data;
};

// Get service dependencies
export const getServiceDependencies = async (hours: number = 24) => {
  const response = await api.get('/api/v1/correlation/dependencies', {
    params: { time_window: hours },
  });
  return response.data;
};

// Get anomalies
export const getAnomalies = async (window_minutes: number = 60) => {
  const response = await api.get('/api/v1/anomaly/detect/log-volume', {
    params: { window_minutes },
  });
  return response.data;
};

// Get anomaly report
export const getAnomalyReport = async (window_minutes: number = 60) => {
  const response = await api.get('/api/v1/anomaly/report', {
    params: { window_minutes },
  });
  return response.data;
};

export default api;
