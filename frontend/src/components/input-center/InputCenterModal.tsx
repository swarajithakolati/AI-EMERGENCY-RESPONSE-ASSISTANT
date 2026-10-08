import React, { useState } from 'react';
import { 
  X, 
  Send, 
  Mic, 
  MicOff, 
  FileText, 
  UploadCloud, 
  MessageSquare, 
  Smartphone, 
  Radio, 
  Share2, 
  CheckCircle2, 
  AlertCircle,
  FileSpreadsheet
} from 'lucide-react';
import { api } from '../../services/api';

interface InputCenterModalProps {
  onClose: () => void;
  onReportIngested: (result: any) => void;
}

export const InputCenterModal: React.FC<InputCenterModalProps> = ({ onClose, onReportIngested }) => {
  const [activeTab, setActiveTab] = useState<'text' | 'audio' | 'sms' | 'whatsapp' | 'social' | 'file' | 'manual'>('text');
  const [loading, setLoading] = useState(false);
  const [ingestResult, setIngestResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form states
  const [rawText, setRawText] = useState('');
  const [source, setSource] = useState('TEXT');
  const [smsPhone, setSmsPhone] = useState('+91 98401 23456');
  const [socialHandle, setSocialHandle] = useState('@ChennaiFloodWatch');
  const [manualTitle, setManualTitle] = useState('');
  const [manualLocation, setManualLocation] = useState('');
  const [manualPeople, setManualPeople] = useState(0);

  // Audio / Speech recording state
  const [isRecording, setIsRecording] = useState(false);
  const [audioTranscript, setAudioTranscript] = useState('');
  const [audioPreset, setAudioPreset] = useState('');

  const handleQuickPreset = (text: string, src: string) => {
    setRawText(text);
    setSource(src);
  };

  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawText.trim()) return;

    setLoading(true);
    setErrorMsg(null);
    setIngestResult(null);

    try {
      const res = await api.createReport({
        raw_text: rawText.trim(),
        source: source
      });
      setIngestResult(res);
      onReportIngested(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to ingest report');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setErrorMsg(null);
    setIngestResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await api.uploadFileReports(formData);
      setIngestResult(res);
      onReportIngested(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to parse file');
    } finally {
      setLoading(false);
    }
  };

  // Web Speech API / Voice Recording
  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      // Fallback simulated STT
      setIsRecording(true);
      setTimeout(() => {
        setAudioTranscript("Emergency 108 dispatch! Inundation near Velachery MRTS West Gate, 6 people trapped inside ground floor.");
        setIsRecording(false);
      }, 2000);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.lang = 'en-IN';
      recognition.interimResults = false;

      recognition.onstart = () => setIsRecording(true);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setAudioTranscript(transcript);
        setRawText(transcript);
        setIsRecording(false);
      };
      recognition.onerror = () => setIsRecording(false);
      recognition.onend = () => setIsRecording(false);

      recognition.start();
    } catch (e) {
      setIsRecording(false);
    }
  };

  const handleAudioSubmit = async () => {
    const textToSubmit = audioTranscript || rawText;
    if (!textToSubmit.trim()) return;

    setLoading(true);
    setErrorMsg(null);
    try {
      const formData = new FormData();
      formData.append('simulated_transcript', textToSubmit);
      const res = await api.uploadAudioReport(formData);
      setIngestResult(res);
      onReportIngested(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to process audio report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-3 sm:p-5 overflow-y-auto">
      <div className="bg-[#0b1120] border border-slate-800 w-full max-w-3xl rounded-2xl shadow-2xl flex flex-col max-h-[92vh] overflow-hidden my-auto animate-fade-in">
        
        {/* HEADER */}
        <div className="p-4 sm:p-5 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center shadow-md shadow-blue-900/40">
              <UploadCloud className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">
                Multi-Modal Emergency Ingest Center
              </h2>
              <p className="text-xs text-slate-400">
                Common processing pipeline: Ingest ➔ Understand ➔ Extract ➔ Track ➔ Show
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white bg-slate-800/80 hover:bg-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* CHANNEL TABS */}
        <div className="flex items-center gap-1 px-4 pt-2 border-b border-slate-800 bg-slate-950/80 overflow-x-auto scrollbar-none text-xs">
          {[
            { id: 'text', label: 'Text Input', icon: FileText, src: 'TEXT' },
            { id: 'audio', label: 'Audio / Call STT', icon: Mic, src: 'AUDIO' },
            { id: 'whatsapp', label: 'WhatsApp', icon: MessageSquare, src: 'WHATSAPP' },
            { id: 'sms', label: 'SMS Gateway', icon: Smartphone, src: 'SMS' },
            { id: 'social', label: 'Social Media', icon: Share2, src: 'SOCIAL_MEDIA' },
            { id: 'file', label: 'Batch CSV / JSON', icon: FileSpreadsheet, src: 'FILE' },
            { id: 'manual', label: 'Manual Dispatch', icon: Radio, src: 'MANUAL' },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id as any);
                  setSource(tab.src);
                }}
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

          {/* QUICK TEST TEMPLATES */}
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1.5">
              Quick Test Scenarios:
            </span>
            <div className="flex flex-wrap gap-1.5">
              <button
                type="button"
                onClick={() => handleQuickPreset("6 people trapped near Velachery MRTS west gate.", "WHATSAPP")}
                className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 text-blue-300 border border-slate-700 text-[11px]"
              >
                💧 Velachery Flood (6 People)
              </button>
              <button
                type="button"
                onClick={() => handleQuickPreset("Elderly person is still inside near Velachery station and needs insulin.", "AUDIO")}
                className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 text-rose-300 border border-slate-700 text-[11px]"
              >
                🏥 Vulnerable / Insulin Need
              </button>
              <button
                type="button"
                onClick={() => handleQuickPreset("Is there traffic near Velachery right now?", "WHATSAPP")}
                className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 text-amber-300 border border-slate-700 text-[11px]"
              >
                🚫 Non-Emergency Traffic Noise
              </button>
              <button
                type="button"
                onClick={() => handleQuickPreset("Transformer fire on Usman Road T Nagar near Panagal Park! 8 people trapped in basement.", "AUDIO")}
                className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 text-red-300 border border-slate-700 text-[11px]"
              >
                🔥 T. Nagar Fire
              </button>
            </div>
          </div>

          {/* TAB 1: TEXT INPUT */}
          {activeTab === 'text' && (
            <form onSubmit={handleTextSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Raw Emergency Text / Dispatch Note:
                </label>
                <textarea
                  rows={4}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Paste or type any incoming emergency distress message (e.g. '4 people trapped in water near station backside road...')"
                  className="w-full p-3 rounded-xl bg-slate-950 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading || !rawText.trim()}
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-1.5 shadow-lg shadow-blue-950/50 disabled:opacity-50 transition-all"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{loading ? 'Processing via 5-Part Flow...' : 'Ingest & Track Incident'}</span>
                </button>
              </div>
            </form>
          )}

          {/* TAB 2: AUDIO / STT */}
          {activeTab === 'audio' && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col items-center justify-center text-center space-y-3">
                <button
                  type="button"
                  onClick={toggleRecording}
                  className={`w-16 h-16 rounded-full flex items-center justify-center transition-all shadow-xl ${
                    isRecording
                      ? 'bg-red-600 text-white animate-pulse ring-4 ring-red-500/40'
                      : 'bg-blue-600 hover:bg-blue-500 text-white'
                  }`}
                >
                  {isRecording ? <MicOff className="w-7 h-7" /> : <Mic className="w-7 h-7" />}
                </button>

                <div>
                  <h4 className="font-bold text-sm text-slate-200">
                    {isRecording ? 'Listening... Speak emergency details clearly' : 'Click Mic to Record 108 Emergency Audio'}
                  </h4>
                  <p className="text-[11px] text-slate-400">
                    Converts Speech-to-Text ➔ NLP Understanding ➔ Entity Extraction ➔ Incident Matching
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Recognized / Simulated Speech Transcript:
                </label>
                <textarea
                  rows={3}
                  value={audioTranscript || rawText}
                  onChange={(e) => {
                    setAudioTranscript(e.target.value);
                    setRawText(e.target.value);
                  }}
                  placeholder="Speech transcription will appear here..."
                  className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs font-mono"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={handleAudioSubmit}
                  disabled={loading || (!audioTranscript && !rawText)}
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-1.5 disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{loading ? 'Transcribing & Processing...' : 'Process Audio Pipeline'}</span>
                </button>
              </div>
            </div>
          )}

          {/* TAB 3: WHATSAPP */}
          {activeTab === 'whatsapp' && (
            <div className="space-y-3">
              <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-800/40 space-y-2">
                <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
                  <MessageSquare className="w-4 h-4" />
                  <span>WhatsApp Emergency Helpline Bot Simulation</span>
                </div>
                <textarea
                  rows={3}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Type WhatsApp message..."
                  className="w-full p-2.5 rounded-lg bg-slate-950 border border-emerald-800/60 text-white text-xs"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={handleTextSubmit}
                  disabled={loading || !rawText.trim()}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Send WhatsApp Report</span>
                </button>
              </div>
            </div>
          )}

          {/* TAB 4: SMS */}
          {activeTab === 'sms' && (
            <div className="space-y-3">
              <div className="p-3.5 rounded-xl bg-sky-950/20 border border-sky-800/40 space-y-2">
                <div className="flex items-center justify-between text-xs text-sky-300">
                  <div className="flex items-center gap-1.5 font-bold">
                    <Smartphone className="w-4 h-4" />
                    <span>Inbound SMS Gateway (Shortcode 112 / 1070)</span>
                  </div>
                  <input
                    type="text"
                    value={smsPhone}
                    onChange={(e) => setSmsPhone(e.target.value)}
                    className="px-2 py-0.5 rounded bg-slate-950 border border-slate-700 text-slate-300 font-mono text-[11px]"
                  />
                </div>
                <textarea
                  rows={3}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Type SMS text..."
                  className="w-full p-2.5 rounded-lg bg-slate-950 border border-sky-800/60 text-white text-xs"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={handleTextSubmit}
                  disabled={loading || !rawText.trim()}
                  className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Ingest SMS Report</span>
                </button>
              </div>
            </div>
          )}

          {/* TAB 5: SOCIAL MEDIA */}
          {activeTab === 'social' && (
            <div className="space-y-3">
              <div className="p-3.5 rounded-xl bg-pink-950/20 border border-pink-800/40 space-y-2">
                <div className="flex items-center justify-between text-xs text-pink-300">
                  <div className="flex items-center gap-1.5 font-bold">
                    <Share2 className="w-4 h-4" />
                    <span>Social Media Scraper / Public Feed</span>
                  </div>
                  <input
                    type="text"
                    value={socialHandle}
                    onChange={(e) => setSocialHandle(e.target.value)}
                    className="px-2 py-0.5 rounded bg-slate-950 border border-slate-700 text-slate-300 font-mono text-[11px]"
                  />
                </div>
                <textarea
                  rows={3}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Social media post content..."
                  className="w-full p-2.5 rounded-lg bg-slate-950 border border-pink-800/60 text-white text-xs"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={handleTextSubmit}
                  disabled={loading || !rawText.trim()}
                  className="px-4 py-2 rounded-lg bg-pink-600 hover:bg-pink-500 text-white font-semibold text-xs flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Ingest Social Post</span>
                </button>
              </div>
            </div>
          )}

          {/* TAB 6: FILE UPLOAD (CSV / JSON) */}
          {activeTab === 'file' && (
            <div className="space-y-4">
              <div className="p-6 rounded-xl border-2 border-dashed border-slate-700 hover:border-blue-500 bg-slate-950/70 flex flex-col items-center justify-center text-center space-y-2 transition-colors cursor-pointer relative">
                <UploadCloud className="w-10 h-10 text-blue-400" />
                <div>
                  <h4 className="font-bold text-sm text-slate-200">
                    Upload Batch CSV or JSON Emergency Feed
                  </h4>
                  <p className="text-xs text-slate-400">
                    Supports columns: <code>raw_text</code>, <code>source</code>, <code>timestamp</code> (Handles malformed rows gracefully)
                  </p>
                </div>
                <input
                  type="file"
                  accept=".csv,.json"
                  onChange={handleFileUpload}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
              </div>
            </div>
          )}

          {/* TAB 7: MANUAL DISPATCH */}
          {activeTab === 'manual' && (
            <form onSubmit={handleTextSubmit} className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="block text-slate-300 mb-1">Incident Type / Title:</label>
                  <input
                    type="text"
                    value={manualTitle}
                    onChange={(e) => setManualTitle(e.target.value)}
                    placeholder="e.g. Flash Flood Rescue"
                    className="w-full p-2 rounded bg-slate-950 border border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 mb-1">Landmark / Location:</label>
                  <input
                    type="text"
                    value={manualLocation}
                    onChange={(e) => setManualLocation(e.target.value)}
                    placeholder="e.g. Velachery MRTS West Gate"
                    className="w-full p-2 rounded bg-slate-950 border border-slate-700 text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Field Dispatch Notes:
                </label>
                <textarea
                  rows={3}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Official control-room operator field report notes..."
                  className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs"
                  required
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading || !rawText.trim()}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Submit Manual Dispatch Report</span>
                </button>
              </div>
            </form>
          )}

          {/* ERROR ALERT */}
          {errorMsg && (
            <div className="p-3 rounded-xl bg-red-950/60 border border-red-800 text-red-200 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* SUCCESS RESULT CARD */}
          {ingestResult && (
            <div className="p-3.5 rounded-xl bg-slate-900 border border-emerald-500/50 text-xs text-slate-200 space-y-2 animate-slide-up">
              <div className="flex items-center gap-2 text-emerald-400 font-bold">
                <CheckCircle2 className="w-4 h-4" />
                <span>Report Successfully Processed!</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] pt-1 border-t border-slate-800">
                <div>Status: <strong className="text-white">{ingestResult.status}</strong></div>
                <div>Report ID: <strong className="text-cyan-300 font-mono">{ingestResult.report_id || 'Batch'}</strong></div>
                {ingestResult.matched_incident_id && (
                  <div className="col-span-2">
                    Evolving Incident Attached: <strong className="text-blue-400 font-mono">{ingestResult.matched_incident_id}</strong>
                  </div>
                )}
              </div>
            </div>
          )}

        </div>

        {/* FOOTER */}
        <div className="p-3.5 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span className="font-mono text-[11px]">COMMON INTERNAL SCHEMA INGESTION ACTIVE</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
