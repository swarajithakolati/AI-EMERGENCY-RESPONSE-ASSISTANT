import React from 'react';
import { 
  LayoutDashboard, 
  MapPin, 
  Radio, 
  FileInput, 
  PlayCircle, 
  BarChart3, 
  History,
  ShieldCheck
} from 'lucide-react';

export type NavView = 'dashboard' | 'map' | 'live-feed' | 'input' | 'demo' | 'analytics' | 'audit';

interface SidebarProps {
  currentView: NavView;
  onSelectView: (view: NavView) => void;
  unverifiedCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onSelectView, unverifiedCount }) => {
  const navItems = [
    { id: 'dashboard' as NavView, label: 'Command Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'map' as NavView, label: 'Sector Map', icon: MapPin, badge: null },
    { id: 'live-feed' as NavView, label: 'Live Report Stream', icon: Radio, badge: 'LIVE' },
    { id: 'input' as NavView, label: 'Multi-Modal Ingest', icon: FileInput, badge: null },
    { id: 'demo' as NavView, label: 'Velachery Showcase', icon: PlayCircle, badge: 'DEMO' },
    { id: 'analytics' as NavView, label: 'Compression Analytics', icon: BarChart3, badge: null },
    { id: 'audit' as NavView, label: 'Audit Trail', icon: History, badge: null },
  ];

  return (
    <aside className="w-16 md:w-60 bg-[#090d16] border-r border-slate-800/80 flex flex-col justify-between py-3 flex-shrink-0">
      <div className="space-y-1 px-2">
        <div className="hidden md:block px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          Control Center
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectView(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all group relative ${
                isActive
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-[0_0_12px_rgba(59,130,246,0.15)] font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
              title={item.label}
            >
              <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-blue-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
              <span className="hidden md:inline truncate">{item.label}</span>
              
              {item.badge && (
                <span className={`hidden md:inline-block ml-auto text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.2 rounded ${
                  item.badge === 'DEMO' 
                    ? 'bg-red-950 text-red-400 border border-red-800/60' 
                    : 'bg-emerald-950 text-emerald-400 border border-emerald-800/60 animate-pulse'
                }`}>
                  {item.badge}
                </span>
              )}

              {/* Active bar indicator on mobile */}
              {isActive && (
                <div className="md:hidden absolute left-0 top-1 bottom-1 w-1 bg-blue-500 rounded-r"></div>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer System Principle Badge */}
      <div className="px-2 pt-3 border-t border-slate-800/80">
        <div className="hidden md:block p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/90 text-[11px] text-slate-400">
          <div className="flex items-center gap-1.5 font-bold text-slate-300 mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>Operational Safety</span>
          </div>
          <p className="text-[10px] leading-relaxed text-slate-400">
            AI ASSISTS. HUMAN RESPONDER DECIDES.
            Uncertain reports require verification before dispatch.
          </p>
        </div>
      </div>
    </aside>
  );
};
