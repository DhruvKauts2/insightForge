'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getLogVolume } from '@/lib/api';

export default function LogVolumeChart() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const volume = await getLogVolume(60); // Last 60 minutes
      
      // Transform data for Recharts
      const chartData = volume.map(item => ({
        time: new Date(item.timestamp).toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        total: item.total,
        INFO: item.INFO || 0,
        WARNING: item.WARNING || 0,
        ERROR: item.ERROR || 0,
        CRITICAL: item.CRITICAL || 0,
        DEBUG: item.DEBUG || 0,
      }));
      
      setData(chartData);
      setLoading(false);
    } catch (error) {
      console.error('Error loading chart data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Log Volume Over Time</h3>
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Log Volume Over Time</h3>
        <span className="text-xs text-gray-500">Last 60 minutes</span>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="total" 
            stroke="#3b82f6" 
            strokeWidth={2}
            name="Total"
          />
          <Line 
            type="monotone" 
            dataKey="ERROR" 
            stroke="#ef4444" 
            strokeWidth={2}
            name="Errors"
          />
          <Line 
            type="monotone" 
            dataKey="WARNING" 
            stroke="#f59e0b" 
            strokeWidth={2}
            name="Warnings"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
