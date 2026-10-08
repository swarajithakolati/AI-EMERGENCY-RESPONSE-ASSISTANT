import React from 'react';
import { 
  AlertTriangle, 
  Flame, 
  Users, 
  LifeBuoy, 
  ShieldAlert, 
  Play, 
  Bot, 
  PlusCircle, 
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { AnalyticsSummary } from '../../types';

interface HeaderProps {
  analytics: AnalyticsSummary | null;
  onOpenDemo: () => void;
  onOpenInputCenter: () => void;
  onToggleAIAssistant: () => void;
  onResetData: () => void;
  isAIAssistantOpen: boolean;
  unresolvedConflictsCount: number;
  onOpenReviewQueue: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  analytics,
  onOpenDemo,
  onOpenInputCenter,
  onToggleAIAssistant,
  onResetData,
  isAIAssistantOpen,
  unresolvedConflictsCount,
  onOpenReviewQueue
}) => {
  return (
    <header className="sticky top-0 z-30 bg-[#0b1120]/95 backdrop-blur-md border-b border-slate-800/80 px-4 py-2.5">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
        {/* Brand & Tagline */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-red-600 to-amber-600 flex items-center justify-center shadow-lg shadow-red-900/30">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
                  AI EMERGENCY RESPONSE ASSISTANT
                </h1>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-red-950/80 text-red-400 border border-red-800/60 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
                  OPERATIONAL COMMAND
                </span>
              </div>
              <p className="text-xs text-slate-400 font-normal">
                “Helping emergency responders understand incoming information faster.”
              </p>
            </div>
          </div>
        </div>

        {/* Live Top Summary KPIs */}
        {analytics && (
          <div className="flex items-center gap-2 overflow-x-auto pb-1 lg:pb-0 scrollbar-none">
            {/* Active Incidents */}
            <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800">
              <AlertTriangle className="w-3.5 h-3.5 text-blue-400" />
              <div>
                <div className="text-[10px] text-slate-400 font-medium leading-none">Active</div>
                <div className="text-sm font-bold text-blue-300 leading-tight">{analytics.active_incidents}</div>
              </div>
            </div>

            {/* Critical Incidents */}
            <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-red-950/40 border border-red-800/40">
              <Flame className="w-3.5 h-3.5 text-red-400 animate-pulse" />
              <div>
                <div className="text-[10px] text-red-300 font-medium leading-none">Critical</div>
                <div className="text-sm font-bold text-red-400 leading-tight">{analytics.critical_incidents}</div>
              </div>
            </div>

            {/* People Affected */}
            <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800">
              <Users className="w-3.5 h-3.5 text-amber-400" />
              <div>
                <div className="text-[10px] text-slate-400 font-medium leading-none">People At Risk</div>
                <div className="text-sm font-bold text-amber-300 leading-tight">{analytics.total_people_affected}</div>
              </div>
            </div>

            {/* Rescue in Progress */}
            <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-cyan-950/40 border border-cyan-800/40">
              <LifeBuoy className="w-3.5 h-3.5 text-cyan-400" />
              <div>
                <div className="text-[10px] text-cyan-300 font-medium leading-none">Rescues Active</div>
                <div className="text-sm font-bold text-cyan-300 leading-tight">{analytics.rescue_in_progress}</div>
              </div>
            </div>

            {/* Compression Indicator */}
            <div className="hidden sm:flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-indigo-950/40 border border-indigo-800/40">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <div>
                <div className="text-[10px] text-indigo-300 font-medium leading-none">Compression</div>
                <div className="text-sm font-bold text-indigo-300 leading-tight">{analytics.compression_ratio}x ({analytics.total_reports} → {analytics.underlying_incidents})</div>
              </div>
            </div>
          </div>
        )}

        {/* Action Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Velachery Showcase Button */}
          <button
            onClick={onOpenDemo}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-gradient-to-r from-red-600 via-rose-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white shadow-lg shadow-red-950/60 transition-all hover:scale-[1.02] active:scale-[0.98]"
            title="Start Interactive Velachery 6-Stage Demo"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>START DEMO</span>
          </button>

          {/* New Ingest Button */}
          <button
            onClick={onOpenInputCenter}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-950/50 transition-all"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>+ Ingest Report</span>
          </button>

          {/* Human Review Button */}
          {unresolvedConflictsCount > 0 && (
            <button
              onClick={onOpenReviewQueue}
              className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-lg bg-purple-950/80 hover:bg-purple-900 border border-purple-700/50 text-purple-300 transition-all animate-pulse"
              title="Conflicts & Uncertain Merges"
            >
              <AlertTriangle className="w-3.5 h-3.5 text-purple-400" />
              <span>Review ({unresolvedConflictsCount})</span>
            </button>
          )}

          {/* AI Responder Assistant Toggle */}
          <button
            onClick={onToggleAIAssistant}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-lg border transition-all ${
              isAIAssistantOpen 
                ? 'bg-cyan-950 border-cyan-500 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.3)]' 
                : 'bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800'
            }`}
          >
            <Bot className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden sm:inline">AI Assistant</span>
          </button>

          {/* Reset Demo Data */}
          <button
            onClick={onResetData}
            className="p-1.5 text-slate-400 hover:text-slate-200 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 rounded-lg transition-all"
            title="Reset to Fresh Seed Dataset"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  );
};
