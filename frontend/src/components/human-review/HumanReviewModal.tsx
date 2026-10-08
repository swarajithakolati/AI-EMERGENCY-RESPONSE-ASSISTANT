import React, { useState, useEffect } from 'react';
import { 
  X, 
  AlertTriangle, 
  ShieldAlert, 
  Layers, 
  CheckCircle2, 
  UserCheck, 
  RefreshCw,
  GitMerge,
  Split
} from 'lucide-react';
import { RawReport, Incident } from '../../types';
import { api } from '../../services/api';

interface HumanReviewModalProps {
  onClose: () => void;
  onRefresh: () => void;
}

export const HumanReviewModal: React.FC<HumanReviewModalProps> = ({ onClose, onRefresh }) => {
  const [flaggedReports, setFlaggedReports] = useState<RawReport[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  const loadReviewQueue = async () => {
    try {
      setLoading(true);
      const [allReps, allIncs] = await Promise.all([
        api.getReports({ limit: 100 }),
        api.getIncidents()
      ]);
      const flagged = allReps.filter(r => r.processing_status === 'FLAGGED' || r.verification === 'Unverified');
      setFlaggedReports(flagged);
      setIncidents(allIncs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReviewQueue();
  }, []);

  const handleMerge = async (reportId: string, targetIncidentId: string) => {
    await api.mergeIntoIncident({ target_incident_id: targetIncidentId, report_id: reportId });
    await loadReviewQueue();
    onRefresh();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-3 sm:p-5 overflow-y-auto">
      <div className="bg-[#0b1120] border border-purple-500/40 w-full max-w-4xl rounded-2xl shadow-2xl flex flex-col max-h-[92vh] overflow-hidden my-auto animate-fade-in">
        
        {/* HEADER */}
        <div className="p-4 sm:p-5 border-b border-slate-800 bg-slate-900 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-purple-950 border border-purple-500/50 flex items-center justify-center">
              <UserCheck className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>Human-In-The-Loop Decision Queue</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-950 text-purple-300 border border-purple-700">
                  AI ASSISTS • HUMAN DECIDES
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Uncertain duplicate matches and conflicting headcounts require responder approval.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* BODY */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 text-xs">
          {loading ? (
            <div className="text-center py-12 text-slate-400">Loading pending reviews...</div>
          ) : flaggedReports.length === 0 ? (
            <div className="text-center py-12 space-y-2">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
              <h4 className="text-sm font-bold text-slate-200">All Reports Synchronized & Verified</h4>
              <p className="text-xs text-slate-400">No unresolved duplicate conflicts currently waiting for operator review.</p>
            </div>
          ) : (
            flaggedReports.map((rep) => {
              const matchedInc = incidents.find(i => i.id === rep.matched_incident_id);
              return (
                <div key={rep.id} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-slate-300 bg-slate-800 px-2 py-0.5 rounded">
                        {rep.id}
                      </span>
                      <span className="text-slate-400 font-mono text-[10px]">{rep.source}</span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-yellow-950 text-yellow-300 border border-yellow-800">
                        {rep.processing_status}
                      </span>
                    </div>

                    <div className="text-[11px] text-cyan-300 font-mono">
                      Match Confidence: {Math.round(rep.match_confidence * 100)}%
                    </div>
                  </div>

                  {/* Incoming Raw Message */}
                  <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-slate-200 font-mono">
                    "{rep.raw_text}"
                  </div>

                  {/* Candidate Incident Association */}
                  {matchedInc ? (
                    <div className="p-3 rounded-lg bg-blue-950/30 border border-blue-800/40 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-blue-300 font-semibold">Suggested Incident Candidate:</span>
                        <strong className="font-mono text-blue-400">{matchedInc.id}</strong>
                      </div>
                      <div className="text-slate-300 font-medium">{matchedInc.title}</div>
                      <div className="text-slate-400 text-[11px]">{matchedInc.best_known_location} • {matchedInc.people_affected} people affected</div>
                    </div>
                  ) : (
                    <div className="text-slate-400 text-[11px]">No specific candidate incident linked.</div>
                  )}

                  {/* Decision Action Buttons */}
                  <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
                    {rep.matched_incident_id && (
                      <button
                        onClick={() => handleMerge(rep.id, rep.matched_incident_id!)}
                        className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1.5 shadow-md"
                      >
                        <GitMerge className="w-3.5 h-3.5" />
                        <span>MERGE INTO {rep.matched_incident_id}</span>
                      </button>
                    )}

                    <button
                      onClick={onClose}
                      className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center gap-1.5"
                    >
                      <Split className="w-3.5 h-3.5" />
                      <span>KEEP SEPARATE</span>
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* FOOTER */}
        <div className="p-3.5 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>HUMAN OPERATOR AUTHORIZATION ACTIVE</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold"
          >
            Done
          </button>
        </div>

      </div>
    </div>
  );
};
