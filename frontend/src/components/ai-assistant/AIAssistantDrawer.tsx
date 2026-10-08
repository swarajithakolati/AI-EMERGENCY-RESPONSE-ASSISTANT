import React, { useState } from 'react';
import { 
  X, 
  Bot, 
  Send, 
  Sparkles, 
  HelpCircle, 
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { api } from '../../services/api';

interface AIAssistantDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedIncidentId?: string | null;
}

interface MessageItem {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  sources?: string[];
  suggestedActions?: string[];
  timestamp: string;
}

const PRESET_QUESTIONS = [
  "What are the most critical incidents?",
  "Which incidents have vulnerable people?",
  "Show unresolved medical emergencies",
  "What changed recently?",
  "Which reports are unverified?",
  "Which incidents have conflicting information?",
  "Summarize the Velachery incident"
];

export const AIAssistantDrawer: React.FC<AIAssistantDrawerProps> = ({
  isOpen,
  onClose,
  selectedIncidentId
}) => {
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      text: "Hello Commander. I am your grounded AI Emergency Operations Assistant. Ask me anything about active incidents, casualty headcounts, vulnerable individuals, or conflicting reports across Chennai sectors.",
      sources: ["Live Incident DB Engine"],
      suggestedActions: ["What are the most critical incidents?", "Which incidents have vulnerable people?"],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSend = async (queryText?: string) => {
    const q = queryText || inputQuery;
    if (!q.trim()) return;

    const userMsg: MessageItem = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await api.queryAIAssistant(q, selectedIncidentId || undefined);
      const botMsg: MessageItem = {
        id: `bot-${Date.now()}`,
        sender: 'assistant',
        text: res.answer,
        sources: res.sources_used,
        suggestedActions: res.suggested_actions,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          text: "I could not retrieve live incident context. Please ensure the emergency database is active.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 z-40 w-full sm:w-[440px] bg-[#0b1120] border-l border-slate-800 shadow-2xl flex flex-col animate-slide-up">
      {/* HEADER */}
      <div className="p-3.5 sm:p-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-500/40 flex items-center justify-center">
            <Bot className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-slate-100 flex items-center gap-1.5">
              <span>AI Responder Assistant</span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                GROUNDED
              </span>
            </h3>
            <p className="text-[10px] text-slate-400">
              Factual Q&A over live database snapshot
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded-md text-slate-400 hover:text-white bg-slate-800"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* QUICK SUGGESTION CHIPS */}
      <div className="px-3 py-2 bg-slate-950/80 border-b border-slate-800/80 overflow-x-auto scrollbar-none flex items-center gap-1.5">
        {PRESET_QUESTIONS.map((pq, i) => (
          <button
            key={i}
            onClick={() => handleSend(pq)}
            className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 text-[11px] text-slate-300 hover:text-cyan-300 border border-slate-800 whitespace-nowrap transition-colors flex-shrink-0"
          >
            {pq}
          </button>
        ))}
      </div>

      {/* CHAT MESSAGES BODY */}
      <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`p-3 rounded-2xl max-w-[90%] text-xs leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none shadow-md'
              }`}
            >
              {/* Formatted Markdown text */}
              <div className="whitespace-pre-line">
                {m.text}
              </div>

              {/* Citations / Sources Used */}
              {m.sources && m.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-800 text-[10px] text-slate-400 space-y-0.5">
                  <span className="font-semibold text-slate-400 block">Verified Data Sources:</span>
                  <div className="flex flex-wrap gap-1">
                    {m.sources.map((src, idx) => (
                      <span key={idx} className="font-mono bg-slate-950 px-1.5 py-0.2 rounded border border-slate-800 text-slate-300">
                        {src}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Suggestion Pills */}
              {m.suggestedActions && m.suggestedActions.length > 0 && (
                <div className="mt-2 pt-1.5 flex flex-wrap gap-1">
                  {m.suggestedActions.map((act, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSend(act)}
                      className="text-[10px] bg-cyan-950/60 hover:bg-cyan-900 text-cyan-300 border border-cyan-800/60 px-2 py-0.5 rounded transition-colors flex items-center gap-1"
                    >
                      <span>{act}</span>
                      <ArrowRight className="w-2.5 h-2.5" />
                    </button>
                  ))}
                </div>
              )}
            </div>

            <span className="text-[9px] text-slate-500 font-mono mt-1 px-1">
              {m.timestamp}
            </span>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400 max-w-[80%]">
            <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
            <span>Analyzing incident database...</span>
          </div>
        )}
      </div>

      {/* INPUT BAR */}
      <div className="p-3 bg-slate-900 border-t border-slate-800">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask question about casualties, flood, resources..."
            className="flex-1 px-3 py-2 text-xs rounded-xl bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="p-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white disabled:opacity-50 transition-colors shadow-md shadow-cyan-950"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
