import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell,
  Legend 
} from 'recharts';
import { 
  Sparkles, 
  BarChart3, 
  Users, 
  Layers, 
  Flame, 
  ShieldCheck, 
  FilterX, 
  RefreshCw 
} from 'lucide-react';
import { AnalyticsSummary } from '../../types';
import { api } from '../../services/api';

const COLORS = ['#ef4444', '#f97316', '#3b82f6', '#06b6d4', '#a855f7', '#10b981', '#64748b'];

export const AnalyticsView: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await api.getAnalytics();
      setAnalytics(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading || !analytics) {
    return <div className="text-center py-12 text-slate-400">Loading Operational Compression Analytics...</div>;
  }

  // Format data for charts
  const typeChartData = Object.entries(analytics.incidents_by_type).map(([name, value]) => ({
    name,
    value
  }));

  const severityChartData = Object.entries(analytics.incidents_by_severity).map(([name, value]) => ({
    name,
    value
  }));

  const sourceChartData = Object.entries(analytics.reports_by_source).map(([name, value]) => ({
    name,
    value
  }));

  return (
    <div className="space-y-5">
      {/* Top Banner: Central Product Idea */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-blue-950/80 via-slate-900 to-indigo-950/80 border border-blue-500/30">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-5 h-5 text-cyan-400" />
              <h2 className="text-lg font-bold text-white">
                Information Overload Compression & Resolution Metrics
              </h2>
            </div>
            <p className="text-xs text-slate-300">
              Transforming hundreds of chaotic reports into an organized, evolving incident picture.
            </p>
          </div>

          {/* Large Compression KPI */}
          <div className="flex items-center gap-4 bg-slate-950/80 p-3 rounded-xl border border-slate-800">
            <div>
              <span className="text-[10px] text-slate-400 font-medium block">Information Compression Ratio:</span>
              <span className="text-2xl font-bold font-mono text-cyan-300">{analytics.compression_ratio}x</span>
            </div>
            <div className="text-xs text-slate-400 border-l border-slate-800 pl-4 space-y-0.5">
              <div><strong>{analytics.total_reports}</strong> Raw Reports Ingested</div>
              <div><strong>{analytics.underlying_incidents}</strong> Underlying Incidents</div>
              <div><strong className="text-amber-400">{analytics.noise_filtered}</strong> Noise Queries Filtered</div>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 mb-1 flex items-center gap-1">
            <Layers className="w-4 h-4 text-blue-400" />
            <span>Total Raw Reports</span>
          </div>
          <div className="text-2xl font-bold font-mono text-white">{analytics.total_reports}</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 mb-1 flex items-center gap-1">
            <Flame className="w-4 h-4 text-red-400" />
            <span>Active Incidents</span>
          </div>
          <div className="text-2xl font-bold font-mono text-red-400">{analytics.active_incidents}</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 mb-1 flex items-center gap-1">
            <Users className="w-4 h-4 text-amber-400" />
            <span>People Affected</span>
          </div>
          <div className="text-2xl font-bold font-mono text-amber-300">{analytics.total_people_affected}</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 mb-1 flex items-center gap-1">
            <FilterX className="w-4 h-4 text-slate-400" />
            <span>Noise Filtered Out</span>
          </div>
          <div className="text-2xl font-bold font-mono text-slate-300">{analytics.noise_filtered}</div>
        </div>
      </div>

      {/* Recharts Visualizations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Incidents by Emergency Type */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Incidents by Emergency Classification
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={typeChartData}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution Pie */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Incidents by Severity Level
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityChartData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(((percent as number) || 0) * 100).toFixed(0)}%`}
                >
                  {severityChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Reports by Ingestion Channel */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3 md:col-span-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Multi-Modal Ingestion Channel Distribution (WhatsApp, Audio, SMS, Social, Manual, File)
          </h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sourceChartData} layout="vertical">
                <XAxis type="number" stroke="#64748b" fontSize={10} />
                <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={11} width={100} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                />
                <Bar dataKey="value" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
};
