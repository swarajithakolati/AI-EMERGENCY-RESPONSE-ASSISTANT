import React from 'react';
import { 
  Users, 
  MapPin, 
  Layers, 
  Clock, 
  Flame, 
  AlertCircle,
  Truck,
  HeartHandshake,
  ShieldCheck,
  ChevronRight,
  TrendingUp
} from 'lucide-react';
import { Incident } from '../../types';
import { getSeverityBadge, getStatusBadge, formatRelativeTime } from '../../utils/helpers';

interface IncidentCardProps {
  incident: Incident;
  onClick: (incident: Incident) => void;
  isSelected?: boolean;
}

export const IncidentCard: React.FC<IncidentCardProps> = ({ incident, onClick, isSelected }) => {
  const sev = getSeverityBadge(incident.severity);
  const stat = getStatusBadge(incident.status);

  return (
    <div
      onClick={() => onClick(incident)}
      className={`group cursor-pointer rounded-xl p-3.5 transition-all relative border bg-slate-900/80 hover:bg-slate-800/90 ${
        isSelected
          ? 'border-blue-500 ring-1 ring-blue-500/50 shadow-lg shadow-blue-950/40'
          : 'border-slate-800 hover:border-slate-700'
      } ${incident.severity === 'Critical' ? 'border-l-4 border-l-red-500' : ''}`}
    >
      {/* Top row: ID, Emergency Type, Badges */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-mono text-xs font-bold text-slate-300 px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700">
            {incident.id}
          </span>
          <span className="text-xs font-bold text-blue-400">
            {incident.emergency_type}
          </span>
          {incident.verification === 'Unverified' && (
            <span className="text-[10px] font-semibold text-yellow-400 px-1.5 py-0.2 rounded bg-yellow-950/80 border border-yellow-700/60">
              UNVERIFIED
            </span>
          )}
          {incident.status === 'CONFLICTING' && (
            <span className="text-[10px] font-semibold text-purple-300 px-1.5 py-0.2 rounded bg-purple-950/90 border border-purple-600/60 animate-pulse">
              CONFLICT
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          {/* Status Badge */}
          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border flex items-center gap-1 ${stat.bg} ${stat.text} ${stat.border}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${stat.dot}`}></span>
            {stat.label}
          </span>

          {/* Severity Badge */}
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${sev.bg} ${sev.text} ${sev.border} ${sev.glow}`}>
            {sev.label}
          </span>
        </div>
      </div>

      {/* Incident Title */}
      <h3 className="text-sm font-semibold text-slate-100 group-hover:text-blue-300 transition-colors line-clamp-1 mb-1.5">
        {incident.title}
      </h3>

      {/* Location & Landmark */}
      <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-2">
        <MapPin className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
        <span className="truncate font-medium text-slate-300">{incident.best_known_location}</span>
        <span className="text-[10px] text-slate-400 font-mono">({Math.round(incident.location_confidence * 100)}% conf)</span>
      </div>

      {/* Impact Indicators: People affected, Vulnerable, Resource */}
      <div className="grid grid-cols-2 gap-2 my-2 py-2 px-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs">
        {/* People count */}
        <div className="flex items-center gap-1.5">
          <Users className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
          <span className="text-slate-400">People Affected:</span>
          <span className="font-bold text-amber-300 font-mono text-xs">{incident.people_affected}</span>
        </div>

        {/* Merged Reports Count */}
        <div className="flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
          <span className="text-slate-400">Merged Reports:</span>
          <span className="font-bold text-cyan-300 font-mono text-xs">{incident.report_count}</span>
        </div>
      </div>

      {/* Vulnerable People Pill */}
      {incident.vulnerable_people && (
        <div className="flex items-center gap-1.5 text-[11px] text-rose-300 bg-rose-950/40 border border-rose-800/50 px-2 py-1 rounded-md mb-2">
          <HeartHandshake className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
          <span className="truncate font-medium">Vulnerable: {incident.vulnerable_people}</span>
        </div>
      )}

      {/* Primary Resource Needed */}
      <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mb-2">
        <Truck className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
        <span className="text-slate-400">Resource:</span>
        <span className="text-slate-300 font-medium truncate">{incident.primary_resource}</span>
      </div>

      {/* Escalation Reason if present */}
      {incident.last_escalation_reason && (
        <div className="flex items-start gap-1.5 text-[10px] text-amber-300/90 bg-amber-950/30 border border-amber-900/40 p-1.5 rounded mb-2">
          <TrendingUp className="w-3 h-3 text-amber-400 mt-0.5 flex-shrink-0" />
          <span className="line-clamp-1 italic">{incident.last_escalation_reason}</span>
        </div>
      )}

      {/* Footer: Time & Action */}
      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60 mt-1">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>Updated {formatRelativeTime(incident.updated_at)}</span>
        </div>

        <div className="flex items-center gap-1 text-blue-400 group-hover:translate-x-0.5 transition-transform font-medium text-[11px]">
          <span>View sitrep</span>
          <ChevronRight className="w-3 h-3" />
        </div>
      </div>
    </div>
  );
};
