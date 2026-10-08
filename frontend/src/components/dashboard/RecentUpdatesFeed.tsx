import React from 'react';
import { 
  Activity, 
  TrendingUp, 
  Users, 
  HeartHandshake, 
  CheckCircle2, 
  AlertTriangle,
  LifeBuoy,
  Layers,
  ChevronRight
} from 'lucide-react';
import { formatRelativeTime } from '../../utils/helpers';

interface RecentUpdateItem {
  id: number;
  incident_id: string;
  timestamp: string;
  update_type: string;
  description: string;
  actor: string;
}

interface RecentUpdatesFeedProps {
  updates: RecentUpdateItem[];
  onSelectIncident: (incidentId: string) => void;
}

export const RecentUpdatesFeed: React.FC<RecentUpdatesFeedProps> = ({ updates, onSelectIncident }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'PEOPLE_COUNT_UPDATED':
        return <Users className="w-3.5 h-3.5 text-amber-400" />;
      case 'VULNERABILITY_DETECTED':
        return <HeartHandshake className="w-3.5 h-3.5 text-rose-400" />;
      case 'ESCALATED':
        return <TrendingUp className="w-3.5 h-3.5 text-red-400" />;
      case 'STATUS_CHANGED':
        return <LifeBuoy className="w-3.5 h-3.5 text-cyan-400" />;
      case 'RESOLVED':
        return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />;
      case 'CONFLICT_FLAGGED':
        return <AlertTriangle className="w-3.5 h-3.5 text-purple-400" />;
      case 'REPORT_ATTACHED':
      case 'DUPLICATE_MERGED':
      default:
        return <Layers className="w-3.5 h-3.5 text-blue-400" />;
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 flex flex-col h-full">
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Live SitRep Updates
          </h3>
        </div>
        <span className="text-[10px] font-mono text-slate-400 font-semibold px-2 py-0.5 rounded-full bg-slate-950 border border-slate-800">
          REAL-TIME MEMORY
        </span>
      </div>

      <div className="space-y-2 overflow-y-auto flex-1 pr-1 max-h-[360px]">
        {updates.length === 0 ? (
          <div className="text-center py-6 text-slate-500 text-xs">
            No recent state changes logged yet.
          </div>
        ) : (
          updates.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelectIncident(item.incident_id)}
              className="p-2 rounded-lg bg-slate-950/70 hover:bg-slate-800/80 border border-slate-800/80 hover:border-slate-700 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between gap-1 mb-1">
                <div className="flex items-center gap-1.5">
                  <div className="w-5 h-5 rounded flex items-center justify-center bg-slate-900 border border-slate-800">
                    {getIcon(item.update_type)}
                  </div>
                  <span className="font-mono text-[11px] font-bold text-blue-400 group-hover:text-blue-300">
                    {item.incident_id}
                  </span>
                  <span className="text-[10px] uppercase font-semibold text-slate-400">
                    • {item.update_type.replace(/_/g, ' ')}
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">
                  {formatRelativeTime(item.timestamp)}
                </span>
              </div>

              <p className="text-xs text-slate-300 line-clamp-2 pl-6">
                {item.description}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
