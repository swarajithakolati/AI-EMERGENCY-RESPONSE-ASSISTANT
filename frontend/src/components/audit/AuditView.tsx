import React, { useState, useEffect } from 'react';
import { History, Search, ShieldCheck, Bot, User, RefreshCw } from 'lucide-react';
import { AuditLog } from '../../types';
import { api } from '../../services/api';
import { formatRelativeTime } from '../../utils/helpers';

export const AuditView: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [actorFilter, setActorFilter] = useState('All');
  const [search, setSearch] = useState('');

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await api.getAuditLogs({
        actor: actorFilter !== 'All' ? actorFilter : undefined,
        limit: 150
      });
      setLogs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actorFilter]);

  const filteredLogs = logs.filter(l => {
    if (!search) return true;
    const q = search.toLowerCase();
    return l.action.toLowerCase().includes(q) || (l.notes && l.notes.toLowerCase().includes(q)) || (l.incident_id && l.incident_id.toLowerCase().includes(q));
  });

  return (
    <div className="space-y-4 text-xs">
      {/* Header & Controls */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">
              Immutable Governance & Audit Trail
            </h2>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800">
              AUDIT LEDGER ACTIVE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Full compliance record of all autonomous AI interpretations and human responder override decisions.
          </p>
        </div>

        {/* Filter Bar */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search actions..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <select
            value={actorFilter}
            onChange={(e) => setActorFilter(e.target.value)}
            className="px-2.5 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-200"
          >
            <option value="All">All Actors</option>
            <option value="AI">AI Pipeline</option>
            <option value="RESPONDER">Human Responder</option>
          </select>

          <button
            onClick={fetchLogs}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                <th className="p-3">Time</th>
                <th className="p-3">Actor</th>
                <th className="p-3">Action Event</th>
                <th className="p-3">Incident Ref</th>
                <th className="p-3">Report Ref</th>
                <th className="p-3">Details / Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3 text-slate-400 whitespace-nowrap">
                    {formatRelativeTime(log.timestamp)}
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded font-sans text-[10px] font-bold ${
                      log.actor === 'AI' 
                        ? 'bg-cyan-950 text-cyan-300 border border-cyan-800' 
                        : 'bg-amber-950 text-amber-300 border border-amber-800'
                    }`}>
                      {log.actor}
                    </span>
                  </td>
                  <td className="p-3 font-semibold text-slate-200">
                    {log.action}
                  </td>
                  <td className="p-3 text-blue-400">
                    {log.incident_id || '—'}
                  </td>
                  <td className="p-3 text-slate-400">
                    {log.report_id || '—'}
                  </td>
                  <td className="p-3 font-sans text-slate-300 text-xs">
                    {log.notes || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
