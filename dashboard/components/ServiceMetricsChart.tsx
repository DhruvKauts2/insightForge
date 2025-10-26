'use client';

import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getServiceMetrics } from '@/lib/api';

export default function ServiceMetricsChart() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const metrics = await getServiceMetrics(60);
      
      // Transform for chart
      const chartData = metrics.map(item => ({
        service: item.service.replace('-service', ''),
        logs: item.total_logs,
        errors: item.error_count,
        errorRate: parseFloat(item.error_rate.toFixed(2)),
      }));
      
      setData(chartData);
      setLoading(false);
    } catch (error) {
      console.error('Error loading service metrics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Service Metrics</h3>
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Service Metrics</h3>
        <span className="text-xs text-gray-500">Last 60 minutes</span>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="service" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          <Bar dataKey="logs" fill="#3b82f6" name="Total Logs" />
          <Bar dataKey="errors" fill="#ef4444" name="Errors" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
