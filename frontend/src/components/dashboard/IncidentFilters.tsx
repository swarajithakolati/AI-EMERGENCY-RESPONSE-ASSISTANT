import React from 'react';
import { Search, Filter, X } from 'lucide-react';
import { EmergencyType, SeverityType, StatusType, VerificationType } from '../../types';

interface IncidentFiltersProps {
  search: string;
  onSearchChange: (search: string) => void;
  selectedType: string;
  onTypeChange: (type: string) => void;
  selectedSeverity: string;
  onSeverityChange: (severity: string) => void;
  selectedStatus: string;
  onStatusChange: (status: string) => void;
  selectedVerification: string;
  onVerificationChange: (v: string) => void;
  onResetFilters: () => void;
  totalFiltered: number;
}

const EMERGENCY_TYPES = [
  'All', 'Flood', 'Fire', 'Medical', 'Rescue', 'Building collapse',
  'Accident', 'Missing person', 'Road blockage', 'Power emergency'
];

const SEVERITIES = ['All', 'Critical', 'High', 'Medium', 'Low'];
const STATUSES = ['All', 'ACTIVE', 'ESCALATED', 'RESCUE IN PROGRESS', 'RESOLVED', 'UNVERIFIED', 'CONFLICTING'];

export const IncidentFilters: React.FC<IncidentFiltersProps> = ({
  search,
  onSearchChange,
  selectedType,
  onTypeChange,
  selectedSeverity,
  onSeverityChange,
  selectedStatus,
  onStatusChange,
  selectedVerification,
  onVerificationChange,
  onResetFilters,
  totalFiltered
}) => {
  const hasActiveFilters = search || selectedType !== 'All' || selectedSeverity !== 'All' || selectedStatus !== 'All' || selectedVerification !== 'All';

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 space-y-2.5">
      {/* Search and Quick Metrics */}
      <div className="flex flex-col sm:flex-row gap-2 items-center justify-between">
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search location, landmark, ID..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
          {search && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-between sm:justify-end">
          <span className="text-xs text-slate-400">
            Showing <strong className="text-slate-200">{totalFiltered}</strong> incidents
          </span>

          {hasActiveFilters && (
            <button
              onClick={onResetFilters}
              className="text-[11px] text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium underline"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Filter Row: Type, Severity, Status */}
      <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800/80 text-xs">
        {/* Type Dropdown */}
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] text-slate-400 font-medium">Type:</span>
          <select
            value={selectedType}
            onChange={(e) => onTypeChange(e.target.value)}
            className="px-2 py-1 text-xs rounded-md bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-blue-500"
          >
            {EMERGENCY_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        {/* Severity Selector */}
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] text-slate-400 font-medium">Severity:</span>
          <div className="flex items-center gap-1">
            {SEVERITIES.map((s) => (
              <button
                key={s}
                onClick={() => onSeverityChange(s)}
                className={`px-2 py-0.5 text-[11px] rounded transition-all ${
                  selectedSeverity === s
                    ? s === 'Critical' ? 'bg-red-900 text-red-200 font-bold border border-red-600'
                    : s === 'High' ? 'bg-orange-900 text-orange-200 font-bold border border-orange-600'
                    : 'bg-blue-600 text-white font-bold'
                    : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Status Dropdown */}
        <div className="flex items-center gap-1.5 ml-auto">
          <span className="text-[11px] text-slate-400 font-medium">Status:</span>
          <select
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
            className="px-2 py-1 text-xs rounded-md bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:border-blue-500"
          >
            {STATUSES.map((st) => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};
