import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  FastForward, 
  CheckCircle2, 
  AlertTriangle, 
  Users, 
  HeartHandshake, 
  TrendingUp, 
  LifeBuoy, 
  ShieldCheck, 
  Bot, 
  ArrowRight,
  Layers,
  Sparkles,
  X
} from 'lucide-react';
import { DemoStage } from '../../types';
import { api } from '../../services/api';

interface LiveDemoShowcaseProps {
  onClose: () => void;
  onRefreshDashboard: () => void;
  onOpenIncidentDetail: (incidentId: string) => void;
}

export const LiveDemoShowcase: React.FC<LiveDemoShowcaseProps> = ({
  onClose,
  onRefreshDashboard,
  onOpenIncidentDetail
}) => {
  const [stages, setStages] = useState<DemoStage[]>([]);
  const [currentStageIndex, setCurrentStageIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [activePipelineStep, setActivePipelineStep] = useState<number>(0);
  const [lastStepResult, setLastStepResult] = useState<any>(null);
  const [createdIncidentId, setCreatedIncidentId] = useState<string | null>(null);

  useEffect(() => {
    api.getDemoStages().then(setStages).catch(console.error);
  }, []);

  const pipelineSteps = [
    { num: 1, label: 'INGEST', desc: 'Raw Channel Input' },
    { num: 2, label: 'UNDERSTAND', desc: 'Noise & Type Filter' },
    { num: 3, label: 'EXTRACT', desc: 'Headcount & Landmark' },
    { num: 4, label: 'MATCH', desc: 'Context & Anaphora' },
    { num: 5, label: 'TRACK', desc: 'Evolving Memory' },
  ];

  const runStep = async (stepIdx: number) => {
    if (stepIdx >= stages.length) {
      setIsPlaying(false);
      return;
    }
    
    setIsProcessing(true);
    setCurrentStageIndex(stepIdx);

    // Animate through the 5 pipeline steps visually
    for (let p = 1; p <= 5; p++) {
      setActivePipelineStep(p);
      await new Promise(r => setTimeout(r, 180));
    }

    try {
      const result = await api.executeDemoStep(stepIdx + 1);
      setLastStepResult(result);
      if (result.incident?.id) {
        setCreatedIncidentId(result.incident.id);
      }
      onRefreshDashboard();
    } catch (e) {
      console.error('Demo step failed', e);
    } finally {
      setIsProcessing(false);
    }
  };

  // Autoplay loop
  useEffect(() => {
    let timer: any;
    if (isPlaying && !isProcessing) {
      if (currentStageIndex < stages.length) {
        timer = setTimeout(() => {
          runStep(currentStageIndex);
          if (currentStageIndex + 1 < stages.length) {
            setCurrentStageIndex(prev => prev + 1);
          } else {
            setIsPlaying(false);
          }
        }, 2200);
      } else {
        setIsPlaying(false);
      }
    }
    return () => clearTimeout(timer);
  }, [isPlaying, isProcessing, currentStageIndex, stages.length]);

  const handleStartAutoplay = () => {
    setIsPlaying(true);
    if (currentStageIndex >= stages.length - 1) {
      setCurrentStageIndex(0);
    }
  };

  const handleReset = async () => {
    setIsPlaying(false);
    setCurrentStageIndex(0);
    setLastStepResult(null);
    setCreatedIncidentId(null);
    await api.resetDemoData();
    onRefreshDashboard();
  };

  const currentStage = stages[currentStageIndex] || stages[0];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-3 sm:p-5 overflow-y-auto">
      <div className="bg-[#090d16] border border-red-500/30 w-full max-w-5xl rounded-2xl shadow-[0_0_50px_rgba(239,68,68,0.15)] flex flex-col max-h-[92vh] overflow-hidden my-auto animate-fade-in">
        
        {/* TOP BANNER */}
        <div className="p-4 sm:p-5 bg-gradient-to-r from-red-950/80 via-slate-900 to-amber-950/80 border-b border-red-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-amber-500 flex items-center justify-center shadow-lg shadow-red-500/20">
              <Sparkles className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base sm:text-lg font-bold text-white">
                  LIVE DEMO SHOWCASE: Velachery Flooding
                </h2>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-red-900/80 text-red-300 border border-red-600/60">
                  STAGE {currentStageIndex + 1} OF 6
                </span>
              </div>
              <p className="text-xs text-slate-300">
                “MANY RAW REPORTS → ONE EVOLVING INCIDENT” (Zero duplicate tickets created)
              </p>
            </div>
          </div>

          {/* Controls & Close */}
          <div className="flex items-center gap-2">
            <button
              onClick={isPlaying ? () => setIsPlaying(false) : handleStartAutoplay}
              disabled={isProcessing}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-md ${
                isPlaying 
                  ? 'bg-amber-600 hover:bg-amber-500 text-white'
                  : 'bg-red-600 hover:bg-red-500 text-white'
              }`}
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 fill-current" />}
              <span>{isPlaying ? 'PAUSE' : 'AUTOPLAY'}</span>
            </button>

            <button
              onClick={() => runStep(currentStageIndex)}
              disabled={isProcessing || isPlaying}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all disabled:opacity-50"
            >
              <span>Next Stage</span>
              <FastForward className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={handleReset}
              disabled={isProcessing}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
              title="Reset Demo State"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors ml-2"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* 5-PART FLOW PIPELINE ANIMATION BAR */}
        <div className="bg-slate-950 px-4 py-3 border-b border-slate-800">
          <div className="grid grid-cols-5 gap-2 text-center text-xs">
            {pipelineSteps.map((step) => {
              const isActive = activePipelineStep === step.num;
              const isPast = activePipelineStep > step.num;
              return (
                <div
                  key={step.num}
                  className={`p-2 rounded-lg border transition-all ${
                    isActive
                      ? 'bg-blue-950/80 border-blue-400 text-blue-300 shadow-[0_0_12px_rgba(59,130,246,0.3)] scale-[1.03]'
                      : isPast
                      ? 'bg-slate-900 border-slate-700 text-slate-300'
                      : 'bg-slate-950/50 border-slate-800/80 text-slate-400'
                  }`}
                >
                  <div className="text-[10px] font-mono font-bold text-slate-400">
                    PART {step.num}
                  </div>
                  <div className="font-bold text-xs">{step.label}</div>
                  <div className="text-[9px] text-slate-400 truncate">{step.desc}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* MAIN BODY: 6 STAGE STEPPER & REAL-TIME STATE DIFF */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 grid grid-cols-1 lg:grid-cols-12 gap-4">

          {/* Left Column: Stage Sequence Selector (4 cols) */}
          <div className="lg:col-span-4 space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
              Sequential Showcase Stages
            </h3>

            {stages.map((stg, idx) => {
              const isCurrent = currentStageIndex === idx;
              const isDone = currentStageIndex > idx;
              return (
                <div
                  key={stg.stage}
                  onClick={() => runStep(idx)}
                  className={`p-2.5 rounded-xl border text-xs cursor-pointer transition-all ${
                    isCurrent
                      ? 'bg-red-950/40 border-red-500/70 text-red-100 shadow-md ring-1 ring-red-500/30'
                      : isDone
                      ? 'bg-slate-900/60 border-slate-700 text-slate-300 hover:bg-slate-800'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-900'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <span className="font-bold font-mono text-[11px] text-red-400">
                      STAGE {stg.stage}
                    </span>
                    <span className="text-[9px] font-mono uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                      {stg.source}
                    </span>
                  </div>

                  <div className="font-semibold text-slate-200 line-clamp-1">
                    {stg.title}
                  </div>

                  <p className="text-[11px] text-slate-400 mt-1 italic line-clamp-1">
                    "{stg.raw_text}"
                  </p>
                </div>
              );
            })}
          </div>

          {/* Right Column: Live Pipeline Output & State Diff (8 cols) */}
          <div className="lg:col-span-8 space-y-3 flex flex-col">

            {/* Active Stage Processing Card */}
            {currentStage && (
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
                    <h4 className="font-bold text-sm text-slate-100">{currentStage.title}</h4>
                  </div>
                  <span className="text-xs font-mono font-bold text-amber-400">
                    Source: {currentStage.source}
                  </span>
                </div>

                {/* Raw Input Prompt */}
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                    Incoming Raw Report:
                  </span>
                  <p className="text-sm font-mono text-cyan-300 font-semibold">
                    "{currentStage.raw_text}"
                  </p>
                </div>

                {/* Expected AI Action */}
                <div className="p-2.5 rounded-lg bg-blue-950/30 border border-blue-800/40 text-xs text-blue-200 flex items-start gap-2">
                  <Bot className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="block text-blue-300">Expected AI Transformation:</strong>
                    <span>{currentStage.expected_action}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Live Evolving Incident Result Card */}
            {lastStepResult?.incident && (
              <div className="p-4 rounded-xl bg-slate-900/90 border border-emerald-500/40 space-y-3 animate-slide-up flex-1">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="font-mono text-xs font-bold text-white px-2 py-0.5 rounded bg-slate-800">
                      {lastStepResult.incident.id}
                    </span>
                    <span className="text-xs font-bold text-emerald-400">
                      INCIDENT EVOLUTION CONFIRMED
                    </span>
                  </div>

                  <button
                    onClick={() => onOpenIncidentDetail(lastStepResult.incident.id)}
                    className="text-xs font-semibold text-blue-400 hover:text-blue-300 underline flex items-center gap-1"
                  >
                    <span>View Full SitRep</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>

                {/* Evolution Parameters State */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  <div className="p-2 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Status:</span>
                    <strong className="text-slate-100 font-bold">{lastStepResult.incident.status}</strong>
                  </div>

                  <div className="p-2 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Severity:</span>
                    <strong className={`font-bold ${
                      lastStepResult.incident.severity === 'Critical' ? 'text-red-400' : 'text-orange-400'
                    }`}>
                      {lastStepResult.incident.severity}
                    </strong>
                  </div>

                  <div className="p-2 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">People Affected:</span>
                    <strong className="text-amber-300 font-bold font-mono text-sm">{lastStepResult.incident.people_affected}</strong>
                  </div>

                  <div className="p-2 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Corroborated Reports:</span>
                    <strong className="text-cyan-300 font-bold font-mono text-sm">{lastStepResult.incident.report_count} Reports</strong>
                  </div>
                </div>

                {/* Vulnerability Alert if triggered */}
                {lastStepResult.incident.vulnerable_people && (
                  <div className="p-2.5 rounded-lg bg-rose-950/40 border border-rose-800/60 text-xs text-rose-200 flex items-center gap-2">
                    <HeartHandshake className="w-4 h-4 text-rose-400 flex-shrink-0" />
                    <span><strong>Vulnerable Person:</strong> {lastStepResult.incident.vulnerable_people}</span>
                  </div>
                )}

                {/* Causal Escalation Reason */}
                {lastStepResult.incident.last_escalation_reason && (
                  <div className="p-2.5 rounded-lg bg-amber-950/30 border border-amber-900/40 text-xs text-amber-200 flex items-start gap-2">
                    <TrendingUp className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="block text-amber-300">Why State Changed:</strong>
                      <span>{lastStepResult.incident.last_escalation_reason}</span>
                    </div>
                  </div>
                )}
              </div>
            )}

          </div>

        </div>

        {/* BOTTOM FOOTER */}
        <div className="p-3.5 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span className="font-mono text-[11px] text-slate-400">
            HACKATHON SHOWCASE: PROVING 6 DISPARATE MESSAGES CONVERGE INTO 1 EVOLVING RECORD
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold transition-colors"
          >
            Close Showcase
          </button>
        </div>

      </div>
    </div>
  );
};
