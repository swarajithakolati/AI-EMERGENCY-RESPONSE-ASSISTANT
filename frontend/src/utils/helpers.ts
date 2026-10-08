import { SeverityType, StatusType, SourceType, VerificationType } from '../types';

export function getSeverityBadge(severity: SeverityType) {
  switch (severity) {
    case 'Critical':
      return {
        bg: 'bg-red-950/80',
        text: 'text-red-400',
        border: 'border-red-500/40',
        glow: 'shadow-[0_0_12px_rgba(239,68,68,0.35)]',
        label: 'CRITICAL'
      };
    case 'High':
      return {
        bg: 'bg-orange-950/80',
        text: 'text-orange-400',
        border: 'border-orange-500/40',
        glow: 'shadow-[0_0_10px_rgba(249,115,22,0.25)]',
        label: 'HIGH'
      };
    case 'Medium':
      return {
        bg: 'bg-amber-950/80',
        text: 'text-amber-400',
        border: 'border-amber-500/40',
        glow: '',
        label: 'MEDIUM'
      };
    case 'Low':
    default:
      return {
        bg: 'bg-slate-800/80',
        text: 'text-slate-300',
        border: 'border-slate-600/40',
        glow: '',
        label: 'LOW'
      };
  }
}

export function getStatusBadge(status: StatusType) {
  switch (status) {
    case 'ACTIVE':
      return {
        bg: 'bg-blue-950/80',
        text: 'text-blue-400',
        border: 'border-blue-500/40',
        dot: 'bg-blue-400',
        label: 'ACTIVE'
      };
    case 'ESCALATED':
      return {
        bg: 'bg-rose-950/90',
        text: 'text-rose-300',
        border: 'border-rose-500/60',
        dot: 'bg-rose-500 animate-ping',
        label: 'ESCALATED'
      };
    case 'RESCUE IN PROGRESS':
      return {
        bg: 'bg-cyan-950/80',
        text: 'text-cyan-300',
        border: 'border-cyan-500/40',
        dot: 'bg-cyan-400 animate-pulse',
        label: 'RESCUE IN PROGRESS'
      };
    case 'RESOLVED':
      return {
        bg: 'bg-emerald-950/80',
        text: 'text-emerald-400',
        border: 'border-emerald-500/40',
        dot: 'bg-emerald-400',
        label: 'RESOLVED'
      };
    case 'UNVERIFIED':
      return {
        bg: 'bg-yellow-950/80',
        text: 'text-yellow-400',
        border: 'border-yellow-500/40',
        dot: 'bg-yellow-400',
        label: 'UNVERIFIED'
      };
    case 'CONFLICTING':
      return {
        bg: 'bg-purple-950/80',
        text: 'text-purple-300',
        border: 'border-purple-500/50',
        dot: 'bg-purple-400 animate-pulse',
        label: 'CONFLICTING'
      };
    default:
      return {
        bg: 'bg-slate-800',
        text: 'text-slate-300',
        border: 'border-slate-700',
        dot: 'bg-slate-400',
        label: status
      };
  }
}

export function getSourceBadge(source: SourceType) {
  switch (source) {
    case 'AUDIO':
      return { bg: 'bg-violet-950/70', text: 'text-violet-300', border: 'border-violet-500/30', label: 'Audio Call' };
    case 'WHATSAPP':
      return { bg: 'bg-emerald-950/70', text: 'text-emerald-300', border: 'border-emerald-500/30', label: 'WhatsApp' };
    case 'SMS':
      return { bg: 'bg-sky-950/70', text: 'text-sky-300', border: 'border-sky-500/30', label: 'SMS' };
    case 'SOCIAL_MEDIA':
      return { bg: 'bg-pink-950/70', text: 'text-pink-300', border: 'border-pink-500/30', label: 'Social Media' };
    case 'MANUAL':
      return { bg: 'bg-indigo-950/70', text: 'text-indigo-300', border: 'border-indigo-500/30', label: 'Manual Report' };
    case 'FILE':
    default:
      return { bg: 'bg-amber-950/70', text: 'text-amber-300', border: 'border-amber-500/30', label: 'File Upload' };
  }
}

export function formatRelativeTime(isoString: string): string {
  try {
    const d = new Date(isoString);
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - d.getTime()) / 1000);

    if (diffSec < 45) return 'Just now';
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    return 'Recent';
  }
}
