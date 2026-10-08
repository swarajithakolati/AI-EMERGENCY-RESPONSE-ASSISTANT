import React, { useState, useEffect } from 'react';
import { 
  Radio, 
  Search, 
  Filter, 
  ArrowRight, 
  AlertCircle, 
  Layers, 
  ShieldAlert, 
  Clock, 
  RefreshCw,
  Sparkles
} from 'lucide-react';
import { RawReport } from '../../types';
import { api } from '../../services/api';
import { getSourceBadge, formatRelativeTime } from '../../utils/helpers';

interface LiveReportFeedProps {
  onSelectIncident: (incidentId: string) => void;
}

export const LiveReportFeed: React.FC<LiveReportFeedProps> = ({ onSelectIncident }) => {
  const [reports, setReports] = useState<RawReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [sourceFilter, setSourceFilter] = useState('All');
  const [noiseFilter, setNoiseFilter] = useState<'all' | 'emergency' | 'noise'>('all');
  const [search, setSearch] = useState('');

  const fetchReports = async () => {
    try {
      setLoading(true);
      const data = await api.getReports({
        source: sourceFilter !== 'All' ? sourceFilter : undefined,
        is_noise: noiseFilter === 'noise' ? true : noiseFilter === 'emergency' ? false : undefined,
        limit: 150
      });
      setReports(data);
    } catch (e) {
      console.error('Failed to fetch reports', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
    const interval = setInterval(fetchReports, 5000);
    return () => clearInterval(interval);
  }, [sourceFilter, noiseFilter]);

  const filteredReports = reports.filter((r) => {
    if (search) {
      const q = search.toLowerCase();
      return r.raw_text.toLowerCase().includes(q) || r.id.toLowerCase().includes(q) || (r.matched_incident_id && r.matched_incident_id.toLowerCase().includes(q));
    }
    return true;
  });

  const getProcessingBadge = (status: string) => {
    switch (status) {
      case 'UPDATED':
      case 'MATCHED':
        return { bg: 'bg-emerald-950/80', text: 'text-emerald-300', border: 'border-emerald-600/50' };
      case 'NOISE':
        return { bg: 'bg-slate-900', text: 'text-slate-500', border: 'border-slate-800' };
      case 'FLAGGED':
        return { bg: 'bg-purple-950/80', text: 'text-purple-300', border: 'border-purple-600/60' };
      default:
        return { bg: 'bg-blue-950/80', text: 'text-blue-300', border: 'border-blue-600/50' };
    }
  };

  return (
    <div className="space-y-4">
      {/* Header & Controls */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Radio className="w-5 h-5 text-emerald-400 animate-pulse" />
            <h2 className="text-base font-bold text-white">
              Live Incoming Emergency Ingest Stream
            </h2>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800">
              5-STAGE PIPELINE ACTIVE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time feed showing unstructured messages parsed, matched, or filtered as noise.
          </p>
        </div>

        {/* Filter Bar */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Source Filter */}
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="px-2.5 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200"
          >
            {['All', 'AUDIO', 'WHATSAPP', 'SMS', 'SOCIAL_MEDIA', 'MANUAL', 'FILE'].map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          {/* Noise / Emergency Toggle */}
          <div className="flex items-center rounded-lg bg-slate-950 border border-slate-800 p-0.5 text-xs">
            <button
              onClick={() => setNoiseFilter('all')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all ${
                noiseFilter === 'all' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All ({reports.length})
            </button>
            <button
              onClick={() => setNoiseFilter('emergency')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all ${
                noiseFilter === 'emergency' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Emergencies
            </button>
            <button
              onClick={() => setNoiseFilter('noise')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all ${
                noiseFilter === 'noise' ? 'bg-amber-700 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Filtered Noise
            </button>
          </div>

          <button
            onClick={fetchReports}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
            title="Refresh stream"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Reports Stream Grid */}
      <div className="space-y-2.5">
        {filteredReports.map((rep) => {
          const srcBadge = getSourceBadge(rep.source);
          const procBadge = getProcessingBadge(rep.processing_status);

          return (
            <div
              key={rep.id}
              className={`p-3.5 rounded-xl border transition-all ${
                rep.is_noise 
                  ? 'bg-slate-950/50 border-slate-800/60 opacity-75' 
                  : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono text-xs font-bold text-slate-300 px-1.5 py-0.5 rounded bg-slate-800">
                    {rep.id}
                  </span>

                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${srcBadge.bg} ${srcBadge.text} ${srcBadge.border}`}>
                    {srcBadge.label}
                  </span>

                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${procBadge.bg} ${procBadge.text} ${procBadge.border}`}>
                    STAGE: {rep.processing_status}
                  </span>

                  {rep.is_noise && (
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800">
                      NOISE FILTERED (NO TICKET CREATED)
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-400 font-mono text-[11px]">
                    {formatRelativeTime(rep.timestamp)}
                  </span>
                </div>
              </div>

              {/* Message Quote */}
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-xs font-mono text-slate-200 mb-2">
                "{rep.raw_text}"
              </div>

              {/* Extraction / Incident Link Row */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs pt-1 border-t border-slate-800/60">
                <div className="flex flex-wrap items-center gap-3 text-slate-400 text-[11px]">
                  {rep.emergency_type !== 'None' && (
                    <span>Type: <strong className="text-blue-300">{rep.emergency_type}</strong></span>
                  )}
                  {rep.location_interpreted && (
                    <span>Location: <strong className="text-slate-200">{rep.location_interpreted}</strong></span>
                  )}
                  {rep.people_affected && (
                    <span>People: <strong className="text-amber-300">{rep.people_affected}</strong></span>
                  )}
                  {rep.vulnerable_people && (
                    <span>Vulnerable: <strong className="text-rose-300">{rep.vulnerable_people}</strong></span>
                  )}
                </div>

                {/* Associated Incident link */}
                {rep.matched_incident_id && (
                  <button
                    onClick={() => onSelectIncident(rep.matched_incident_id!)}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-blue-950/60 hover:bg-blue-900 border border-blue-800/60 text-blue-300 font-semibold text-xs transition-colors self-start sm:self-auto"
                  >
                    <span>Evolving Incident: {rep.matched_incident_id}</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
