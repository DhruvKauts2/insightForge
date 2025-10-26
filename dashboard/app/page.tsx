'use client';

import { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Database, TrendingUp } from 'lucide-react';
import MetricsCard from '@/components/MetricsCard';
import LogSearch from '@/components/LogSearch';
import LogTable from '@/components/LogTable';
import LogVolumeChart from '@/components/LogVolumeChart';
import ServiceMetricsChart from '@/components/ServiceMetricsChart';
import ErrorDistributionChart from '@/components/ErrorDistributionChart';
import AnomalyPanel from '@/components/AnomalyPanel';
import {
  searchLogs,
  getMetricsOverview,
} from '@/lib/api';

export default function Dashboard() {
  const [logs, setLogs] = useState([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadInitialData();
    // Refresh metrics every 30 seconds
    const interval = setInterval(loadMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [logsData, metricsData] = await Promise.all([
        searchLogs({ limit: 50 }),
        getMetricsOverview(),
      ]);
      setLogs(logsData.logs || []);
      setMetrics(metricsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      const metricsData = await getMetricsOverview();
      setMetrics(metricsData);
    } catch (error) {
      console.error('Error loading metrics:', error);
    }
  };

  const handleSearch = async (params: any) => {
    try {
      setLoading(true);
      const data = await searchLogs(params);
      setLogs(data.logs || []);
    } catch (error) {
      console.error('Error searching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">LogFlow</h1>
              <p className="text-sm text-gray-500 mt-1">
                Distributed Log Aggregation System
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium flex items-center gap-2">
                <span className="w-2 h-2 bg-green-600 rounded-full animate-pulse"></span>
                Live
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricsCard
            title="Total Logs"
            value={metrics?.total_logs?.toLocaleString() || '0'}
            icon={<Database className="w-8 h-8" />}
            subtitle="All time"
          />
          <MetricsCard
            title="Logs/Minute"
            value={metrics?.logs_per_minute?.toFixed(1) || '0'}
            icon={<TrendingUp className="w-8 h-8" />}
            trend={{ value: 12.5, isPositive: true }}
          />
          <MetricsCard
            title="Active Services"
            value={metrics?.services_count || '0'}
            icon={<Activity className="w-8 h-8" />}
            subtitle="Healthy"
          />
          <MetricsCard
            title="Error Rate"
            value={`${metrics?.error_rate?.toFixed(2) || '0'}%`}
            icon={<AlertTriangle className="w-8 h-8" />}
            trend={{ value: 2.1, isPositive: false }}
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <LogVolumeChart />
          <ServiceMetricsChart />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ErrorDistributionChart />
          <AnomalyPanel />
        </div>

        {/* Search Section */}
        <div className="mb-6">
          <LogSearch onSearch={handleSearch} />
        </div>

        {/* Logs Table */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Recent Logs
            </h2>
            <span className="text-sm text-gray-500">
              {logs.length} results
            </span>
          </div>
          <LogTable logs={logs} loading={loading} />
        </div>
      </main>
    </div>
  );
}
