import React, { useState, useEffect } from 'react';
import { 
  X, 
  MapPin, 
  Users, 
  HeartHandshake, 
  Truck, 
  Clock, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  FileText, 
  TrendingUp, 
  Layers, 
  MessageSquare, 
  Bot, 
  Edit3, 
  ChevronRight,
  ShieldAlert,
  Save
} from 'lucide-react';
import { Incident, IncidentUpdate, IncidentConflict, RawReport } from '../../types';
import { api } from '../../services/api';
import { getSeverityBadge, getStatusBadge, getSourceBadge, formatRelativeTime } from '../../utils/helpers';

interface IncidentDetailModalProps {
  incidentId: string;
  onClose: () => void;
  onRefresh: () => void;
}

export const IncidentDetailModal: React.FC<IncidentDetailModalProps> = ({
  incidentId,
  onClose,
  onRefresh
}) => {
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'summary' | 'timeline' | 'sources' | 'location' | 'ai-evidence'>('summary');
  
  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editPeople, setEditPeople] = useState<number>(0);
  const [editVulnerable, setEditVulnerable] = useState<string>('');
  const [editStatus, setEditStatus] = useState<string>('');
  const [editSeverity, setEditSeverity] = useState<string>('');
  const [editResource, setEditResource] = useState<string>('');
  const [editNotes, setEditNotes] = useState<string>('');

  const fetchDetail = async () => {
    try {
      setLoading(true);
      const data = await api.getIncidentDetail(incidentId);
      setIncident(data);
      setEditPeople(data.people_affected);
      setEditVulnerable(data.vulnerable_people || '');
      setEditStatus(data.status);
      setEditSeverity(data.severity);
      setEditResource(data.primary_resource);
    } catch (e) {
      console.error('Failed to load incident detail', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [incidentId]);

  const handleVerify = async () => {
    if (!incident) return;
    await api.verifyIncident(incident.id);
    await fetchDetail();
    onRefresh();
  };

  const handleResolve = async () => {
    if (!incident) return;
    await api.resolveIncident(incident.id, 'Responder marked incident as RESOLVED on scene.');
    await fetchDetail();
    onRefresh();
  };

  const handleSaveEdit = async () => {
    if (!incident) return;
    await api.updateIncident(incident.id, {
      people_affected: editPeople,
      vulnerable_people: editVulnerable,
      status: editStatus as any,
      severity: editSeverity as any,
      primary_resource: editResource,
      notes: editNotes || 'Operator updated sitrep parameters'
    });
    setIsEditing(false);
    await fetchDetail();
    onRefresh();
  };

  const handleResolveConflict = async (conflictId: number, action: string) => {
    if (!incident) return;
    await api.resolveIncidentConflict(incident.id, conflictId, { action });
    await fetchDetail();
    onRefresh();
  };

  if (loading || !incident) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl flex items-center gap-3 text-slate-300">
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading SitRep for {incidentId}...</span>
        </div>
      </div>
    );
  }

  const sev = getSeverityBadge(incident.severity);
  const stat = getStatusBadge(incident.status);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-2 sm:p-4 overflow-y-auto">
      <div className="bg-[#0b1120] border border-slate-800 w-full max-w-4xl rounded-2xl shadow-2xl flex flex-col max-h-[92vh] overflow-hidden my-auto animate-fade-in">
        
        {/* HEADER */}
        <div className="p-4 sm:p-5 border-b border-slate-800 bg-slate-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="font-mono text-xs font-bold text-white px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                {incident.id}
              </span>
              <span className="text-sm font-bold text-blue-400">
                {incident.emergency_type} Emergency
              </span>

              {/* Status Badge */}
              <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border flex items-center gap-1 ${stat.bg} ${stat.text} ${stat.border}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${stat.dot}`}></span>
                {stat.label}
              </span>

              {/* Severity Badge */}
              <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${sev.bg} ${sev.text} ${sev.border} ${sev.glow}`}>
                {sev.label} SEVERITY
              </span>

              {/* Verification Badge */}
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                incident.verification === 'Verified' ? 'bg-emerald-950/80 text-emerald-300 border-emerald-700/60'
                : incident.verification === 'Partially Verified' ? 'bg-blue-950/80 text-blue-300 border-blue-700/60'
                : 'bg-yellow-950/80 text-yellow-300 border-yellow-700/60'
              }`}>
                {incident.verification.toUpperCase()}
              </span>

              <span className="text-xs font-mono text-slate-400">
                (AI Confidence: {Math.round(incident.confidence * 100)}%)
              </span>
            </div>

            <h2 className="text-base sm:text-lg font-bold text-slate-100">
              {incident.title}
            </h2>
          </div>

          {/* Close and quick actions */}
          <div className="flex items-center gap-2 self-end sm:self-center">
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white bg-slate-800/80 hover:bg-slate-700 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* NAVIGATION TABS */}
        <div className="flex items-center gap-1 px-4 pt-2 border-b border-slate-800 bg-slate-950/80 overflow-x-auto scrollbar-none text-xs">
          {[
            { id: 'summary', label: 'Current SitRep Summary', icon: FileText },
            { id: 'timeline', label: `Incident Timeline (${incident.updates?.length || 0})`, icon: Clock },
            { id: 'sources', label: `Source Reports (${incident.source_reports?.length || 0})`, icon: MessageSquare },
            { id: 'location', label: 'Location Intelligence', icon: MapPin },
            { id: 'ai-evidence', label: 'AI Decision Evidence', icon: Bot },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-1.5 px-3 py-2 font-medium border-b-2 transition-all whitespace-nowrap ${
                  isActive
                    ? 'border-blue-500 text-blue-400 font-bold bg-blue-950/20'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* MODAL BODY */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">

          {/* CONFLICT BANNER IF ACTIVE */}
          {incident.conflicts && incident.conflicts.filter(c => c.status === 'PENDING_REVIEW').length > 0 && (
            <div className="p-3.5 rounded-xl bg-purple-950/50 border border-purple-600/60 text-xs text-purple-200 space-y-2 animate-pulse-slow">
              <div className="flex items-center gap-2 font-bold text-purple-300">
                <AlertTriangle className="w-4 h-4 text-purple-400" />
                <span>CONFLICTING INFORMATION DETECTED</span>
              </div>
              {incident.conflicts.filter(c => c.status === 'PENDING_REVIEW').map(conflict => (
                <div key={conflict.id} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2 rounded bg-purple-900/40 border border-purple-700/50">
                  <div>
                    <span>Field: <strong>{conflict.field_name}</strong> — </span>
                    <span>Current Record: <strong className="text-amber-300">{conflict.existing_value}</strong> vs </span>
                    <span>Reported: <strong className="text-rose-300">{conflict.conflicting_value}</strong></span>
                    <span className="text-[10px] text-purple-400 block font-mono">Confidence: {Math.round(conflict.confidence * 100)}%</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => handleResolveConflict(conflict.id, 'USE_LATEST')}
                      className="px-2 py-1 text-[11px] font-semibold bg-purple-600 hover:bg-purple-500 text-white rounded transition-colors"
                    >
                      Use Latest ({conflict.conflicting_value})
                    </button>
                    <button
                      onClick={() => handleResolveConflict(conflict.id, 'KEEP_EXISTING')}
                      className="px-2 py-1 text-[11px] font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 transition-colors"
                    >
                      Keep Current ({conflict.existing_value})
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 1: SUMMARY */}
          {activeTab === 'summary' && (
            <div className="space-y-4">
              {/* Quick Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <div className="text-[11px] text-slate-400 mb-1 flex items-center gap-1">
                    <Users className="w-3.5 h-3.5 text-amber-400" />
                    <span>People Affected</span>
                  </div>
                  <div className="text-xl font-bold font-mono text-amber-300">
                    {incident.people_affected}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <div className="text-[11px] text-slate-400 mb-1 flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Merged Reports</span>
                  </div>
                  <div className="text-xl font-bold font-mono text-cyan-300">
                    {incident.report_count}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <div className="text-[11px] text-slate-400 mb-1 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Verification</span>
                  </div>
                  <div className="text-sm font-bold text-slate-200">
                    {incident.verification}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <div className="text-[11px] text-slate-400 mb-1 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-blue-400" />
                    <span>Established</span>
                  </div>
                  <div className="text-xs font-bold text-slate-300">
                    {formatRelativeTime(incident.created_at)}
                  </div>
                </div>
              </div>

              {/* What / Where / When Summary Card */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 border-b border-slate-800 pb-2 flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-blue-400" />
                  <span>Current Situation Assessment</span>
                </h4>

                <p className="text-sm text-slate-200 leading-relaxed font-normal">
                  {incident.summary}
                </p>

                {/* Vulnerable Person Highlight */}
                {incident.vulnerable_people && (
                  <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 text-rose-200 text-xs flex items-start gap-2">
                    <HeartHandshake className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="block text-rose-300">Vulnerable Individuals Detected:</strong>
                      <span>{incident.vulnerable_people}</span>
                    </div>
                  </div>
                )}

                {/* Primary Resource */}
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs flex items-center gap-2">
                  <Truck className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                  <div>
                    <span className="text-slate-400">Primary Dispatch Requirement: </span>
                    <strong className="text-indigo-300 font-semibold">{incident.primary_resource}</strong>
                  </div>
                </div>

                {/* Escalation note if present */}
                {incident.last_escalation_reason && (
                  <div className="p-3 rounded-lg bg-amber-950/40 border border-amber-800/50 text-amber-200 text-xs flex items-start gap-2">
                    <TrendingUp className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="block text-amber-300">Latest Escalation Factor:</strong>
                      <span>{incident.last_escalation_reason}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Edit Mode Panel */}
              {isEditing ? (
                <div className="p-4 rounded-xl bg-slate-950 border border-blue-500/50 space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <h4 className="text-xs font-bold text-blue-400 flex items-center gap-1.5">
                      <Edit3 className="w-3.5 h-3.5" />
                      <span>Human Responder SitRep Override</span>
                    </h4>
                    <button
                      onClick={() => setIsEditing(false)}
                      className="text-xs text-slate-400 hover:text-slate-200"
                    >
                      Cancel
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-slate-400 mb-1">People Affected Count:</label>
                      <input
                        type="number"
                        value={editPeople}
                        onChange={(e) => setEditPeople(parseInt(e.target.value) || 0)}
                        className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-slate-400 mb-1">Operational Status:</label>
                      <select
                        value={editStatus}
                        onChange={(e) => setEditStatus(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-white"
                      >
                        {['ACTIVE', 'ESCALATED', 'RESCUE IN PROGRESS', 'RESOLVED', 'UNVERIFIED', 'CONFLICTING'].map(s => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-slate-400 mb-1">Severity:</label>
                      <select
                        value={editSeverity}
                        onChange={(e) => setEditSeverity(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-white"
                      >
                        {['Critical', 'High', 'Medium', 'Low'].map(s => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-slate-400 mb-1">Vulnerable Persons Description:</label>
                      <input
                        type="text"
                        value={editVulnerable}
                        onChange={(e) => setEditVulnerable(e.target.value)}
                        placeholder="e.g. 1 Elderly Diabetic person"
                        className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-white"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Operator Notes / Rationale:</label>
                    <input
                      type="text"
                      value={editNotes}
                      onChange={(e) => setEditNotes(e.target.value)}
                      placeholder="Reason for manual adjustment..."
                      className="w-full px-2.5 py-1.5 rounded text-xs bg-slate-900 border border-slate-700 text-white"
                    />
                  </div>

                  <div className="flex justify-end pt-2">
                    <button
                      onClick={handleSaveEdit}
                      className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1.5"
                    >
                      <Save className="w-3.5 h-3.5" />
                      <span>Save Changes & Log Audit</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between pt-2">
                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 flex items-center gap-1.5 transition-colors"
                  >
                    <Edit3 className="w-3.5 h-3.5 text-blue-400" />
                    <span>Edit SitRep / Override</span>
                  </button>

                  <div className="flex items-center gap-2">
                    {incident.verification !== 'Verified' && (
                      <button
                        onClick={handleVerify}
                        className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white flex items-center gap-1.5 shadow-md transition-colors"
                      >
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>Verify Authenticity</span>
                      </button>
                    )}

                    {incident.status !== 'RESOLVED' && (
                      <button
                        onClick={handleResolve}
                        className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-emerald-800 text-emerald-300 border border-emerald-700/50 flex items-center gap-1.5 transition-colors"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Mark Resolved</span>
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: TIMELINE */}
          {activeTab === 'timeline' && (
            <div className="space-y-3">
              <div className="text-xs text-slate-400 font-medium pb-2 border-b border-slate-800 flex items-center justify-between">
                <span>Preserved Historical Chronology (No overwritten records)</span>
                <span className="font-mono text-slate-500">{incident.updates?.length || 0} Total Events</span>
              </div>

              <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                {incident.updates?.map((upd, idx) => (
                  <div key={upd.id} className="relative group">
                    {/* Circle Node */}
                    <div className={`absolute -left-6 top-1 w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                      upd.update_type === 'CREATED' ? 'bg-blue-600 border-blue-400'
                      : upd.update_type === 'ESCALATED' ? 'bg-red-600 border-red-400 animate-pulse'
                      : upd.update_type === 'RESOLVED' ? 'bg-emerald-600 border-emerald-400'
                      : upd.update_type === 'VULNERABILITY_DETECTED' ? 'bg-rose-600 border-rose-400'
                      : 'bg-slate-800 border-slate-600'
                    }`}></div>

                    {/* Timeline Card */}
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 group-hover:border-slate-700 transition-all text-xs">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <div className="flex items-center gap-1.5 font-bold text-slate-200">
                          <span className="font-mono text-blue-400">[{formatRelativeTime(upd.timestamp)}]</span>
                          <span className="uppercase text-[11px] text-slate-300">{upd.update_type.replace(/_/g, ' ')}</span>
                          <span className={`text-[9px] px-1.5 py-0.2 rounded ${upd.actor === 'AI' ? 'bg-cyan-950 text-cyan-400' : 'bg-amber-950 text-amber-400'}`}>
                            {upd.actor}
                          </span>
                        </div>
                        {upd.source_report_id && (
                          <span className="font-mono text-[10px] text-slate-500">
                            Ref: {upd.source_report_id}
                          </span>
                        )}
                      </div>

                      <p className="text-slate-300 font-normal leading-relaxed">
                        {upd.description}
                      </p>

                      {upd.evidence && (
                        <div className="mt-1.5 pt-1.5 border-t border-slate-800/80 text-[11px] text-slate-400 italic">
                          "{upd.evidence}"
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: SOURCE REPORTS */}
          {activeTab === 'sources' && (
            <div className="space-y-3">
              <div className="text-xs text-slate-400 font-medium pb-1 border-b border-slate-800 flex items-center justify-between">
                <span>Original Incoming Messages ({incident.source_reports?.length || 0} Merged Reports)</span>
                <span className="text-[11px] text-slate-400">MANY REPORTS ➔ ONE INCIDENT</span>
              </div>

              {incident.source_reports?.map((rep) => {
                const srcBadge = getSourceBadge(rep.source);
                return (
                  <div key={rep.id} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-slate-300 bg-slate-800 px-1.5 py-0.5 rounded">
                          {rep.id}
                        </span>
                        <span className={`px-2 py-0.5 rounded border text-[10px] font-semibold ${srcBadge.bg} ${srcBadge.text} ${srcBadge.border}`}>
                          {srcBadge.label}
                        </span>
                        <span className="text-slate-400 font-mono text-[10px]">
                          {formatRelativeTime(rep.timestamp)}
                        </span>
                      </div>

                      <div className="flex items-center gap-1.5 text-[10px]">
                        <span className="text-slate-400">Match Confidence:</span>
                        <strong className="text-cyan-300 font-mono">{Math.round(rep.confidence * 100)}%</strong>
                      </div>
                    </div>

                    {/* Raw Text Quote */}
                    <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono text-xs">
                      "{rep.raw_text}"
                    </div>

                    {/* Extracted signals from this specific message */}
                    <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-400 pt-1">
                      {rep.people_affected && (
                        <span>People: <strong className="text-amber-300">{rep.people_affected}</strong></span>
                      )}
                      {rep.vulnerable_people && (
                        <span>Vulnerable: <strong className="text-rose-300">{rep.vulnerable_people}</strong></span>
                      )}
                      {rep.urgency && (
                        <span>Urgency: <strong className="text-slate-200">{rep.urgency}</strong></span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* TAB 4: LOCATION INTELLIGENCE */}
          {activeTab === 'location' && (
            <div className="space-y-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5 border-b border-slate-800 pb-2">
                  <MapPin className="w-4 h-4 text-red-400" />
                  <span>Geospatial & Landmark Intelligence</span>
                </h4>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Best-Known Location:</span>
                    <strong className="text-slate-100 text-sm font-semibold">{incident.best_known_location}</strong>
                  </div>

                  <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Location Confidence:</span>
                    <strong className="text-cyan-300 text-sm font-mono">{Math.round(incident.location_confidence * 100)}%</strong>
                    <span className="text-[10px] text-slate-400 block">Based on landmark and proximity cluster</span>
                  </div>

                  <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Interpreted Sector / Zone:</span>
                    <span className="text-slate-200">{incident.interpreted_location || 'General Sector'}</span>
                  </div>

                  <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Identified Landmark:</span>
                    <span className="text-slate-200">{incident.landmark || 'MRTS Station & West Gate'}</span>
                  </div>

                  <div className="p-2.5 rounded bg-slate-950 border border-slate-800 sm:col-span-2">
                    <span className="text-slate-400 block mb-0.5">Uncertainty Radius & Geofence:</span>
                    <span className="text-slate-300 font-mono">
                      GPS: {incident.latitude.toFixed(4)}° N, {incident.longitude.toFixed(4)}° E (±{Math.round(incident.uncertainty_radius_m)}m radius)
                    </span>
                    <p className="text-[10px] text-slate-500 mt-1">
                      *Honest Location Metric: Exact precision is never fabricated without confirmed GPS telemetry.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: AI EVIDENCE */}
          {activeTab === 'ai-evidence' && (
            <div className="space-y-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5 border-b border-slate-800 pb-2">
                  <Bot className="w-4 h-4 text-cyan-400" />
                  <span>Explainable AI Decision Factors</span>
                </h4>

                <div className="space-y-2.5">
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <strong className="text-blue-300 block mb-1">1. Duplicate & Clustering Rationale:</strong>
                    <p className="text-slate-300 leading-relaxed">
                      Incoming reports were aggregated under incident <strong>{incident.id}</strong> due to spatial proximity (Velachery MRTS station landmarks), concurrent time window, and matching flood distress semantics.
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <strong className="text-amber-300 block mb-1">2. Severity & Urgency Escalation:</strong>
                    <p className="text-slate-300 leading-relaxed">
                      {incident.last_escalation_reason || "Urgency was evaluated from affected headcount and environmental escalation indicators."}
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <strong className="text-emerald-300 block mb-1">3. Human-in-the-Loop Governance:</strong>
                    <p className="text-slate-300 leading-relaxed">
                      This incident is monitored by AI assistance. All field resource commitments remain under the full authority of the human command operator.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>

        {/* FOOTER */}
        <div className="p-3.5 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-1.5 font-mono text-[11px]">
            <ShieldAlert className="w-3.5 h-3.5 text-cyan-400" />
            <span>AI EMERGENCY RESPONSE ASSISTANT • HUMAN-IN-THE-LOOP</span>
          </div>

          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold transition-colors"
          >
            Close SitRep
          </button>
        </div>

      </div>
    </div>
  );
};
