import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '../../types';
import { api } from '../../services/api';
import {
  X,
  Send,
  Sparkles,
  Bot,
  User,
  FileText,
  Database,
  BookOpen,
} from 'lucide-react';
import { Badge } from '../common/Badge';

export const ChatbotDrawer: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'bot',
      text: "👋 Welcome to **CSIC AI Academic Assistant**!\n\nI provide real-time verified answers from your university database records (attendance, marks, fees, timetable) and official college policy regulations with zero hallucination.",
      timestamp: 'Just now',
      query_type: 'general',
    },
  ]);
  const [suggestedPrompts, setSuggestedPrompts] = useState<string[]>([
    'What is my attendance percentage?',
    'Show my Mid-Term exam marks',
    'Do I have any pending fee invoices?',
    'What is my timetable today?',
    'Medical leave policy for attendance?',
    'What are the exam passing marks?',
    'What is the grading criteria?',
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState<string | undefined>(undefined);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  // Load suggestions and past history on mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const prompts = await api.getChatSuggestions();
        if (prompts && prompts.length > 0) {
          setSuggestedPrompts(prompts);
        }
        const history = await api.getChatHistory();
        if (history && history.length > 0) {
          setMessages(history);
        }
      } catch {
        // use defaults
      }
    };
    loadInitialData();
  }, []);

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputText;
    if (!text.trim() || isTyping) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsTyping(true);

    try {
      const response = await api.sendChatMessage(text, sessionId);
      setMessages((prev) => [...prev, response]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: 'bot',
          text: '⚠️ I encountered an error communicating with the academic backend service. Please verify your connection or login session and try again.',
          timestamp: 'Just now',
          query_type: 'general',
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const isStructuredQuery = (queryType?: string) => {
    return ['attendance', 'marks', 'fees', 'timetable', 'notices'].includes(queryType || '');
  };

  const isPolicyQuery = (queryType?: string) => {
    return ['policy_document', 'rag_document'].includes(queryType || '');
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle AI Assistant"
        className="fixed bottom-6 right-6 z-40 p-4 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-xl shadow-indigo-600/40 hover:scale-105 active:scale-95 transition-all flex items-center justify-center border border-indigo-400/40 group"
      >
        <Sparkles className="w-6 h-6 animate-pulse group-hover:rotate-12 transition-transform" />
        <span className="sr-only">Open Chatbot</span>
      </button>

      {/* Slide-over Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={() => setIsOpen(false)}
          />

          <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
            <div className="w-screen max-w-md glass-panel border-l border-white/10 shadow-2xl flex flex-col bg-slate-950/95">
              {/* Header */}
              <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-slate-900/90">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/30">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      CSIC Academic AI
                      <Badge variant="primary" size="sm">
                        RAG
                      </Badge>
                    </h3>
                    <p className="text-[11px] text-slate-400 font-mono flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                      PostgreSQL 3NF + Gemini 2.5 Flash
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                  aria-label="Close AI Assistant"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Message List */}
              <div className="flex-1 p-4 overflow-y-auto space-y-4">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-3 ${
                      msg.sender === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {msg.sender === 'bot' && (
                      <div className="w-7 h-7 rounded-lg bg-indigo-600/30 border border-indigo-400/30 flex items-center justify-center text-indigo-300 shrink-0 mt-1">
                        <Bot className="w-4 h-4" />
                      </div>
                    )}

                    <div
                      className={`max-w-[85%] rounded-2xl p-3.5 text-xs sm:text-sm leading-relaxed shadow-sm ${
                        msg.sender === 'user'
                          ? 'bg-indigo-600 text-white rounded-tr-none'
                          : 'bg-slate-900/90 text-slate-200 border border-white/10 rounded-tl-none'
                      }`}
                    >
                      {/* Classification Badge Distinction */}
                      {msg.sender === 'bot' && msg.query_type && (
                        <div className="mb-2">
                          {isStructuredQuery(msg.query_type) && (
                            <span className="inline-flex items-center gap-1 text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                              <Database className="w-3 h-3 text-emerald-400" />
                              Verified Database Fact
                            </span>
                          )}

                          {isPolicyQuery(msg.query_type) && (
                            <span className="inline-flex items-center gap-1 text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                              <BookOpen className="w-3 h-3 text-amber-400" />
                              Institutional Policy RAG
                            </span>
                          )}
                        </div>
                      )}

                      <div className="whitespace-pre-wrap">{msg.text}</div>

                      {/* Source Citations Badges */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-2.5 pt-2 border-t border-white/10 space-y-1">
                          <span className="text-[10px] uppercase font-mono text-slate-400 block font-semibold">
                            Grounding Sources:
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {msg.sources.map((src, i) => (
                              <span
                                key={i}
                                className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-indigo-300 border border-white/10 flex items-center gap-1 shadow-sm"
                              >
                                <FileText className="w-2.5 h-2.5 text-indigo-400" />
                                {src}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div
                        className={`text-[10px] mt-1.5 font-mono ${
                          msg.sender === 'user' ? 'text-indigo-200 text-right' : 'text-slate-500'
                        }`}
                      >
                        {msg.timestamp}
                      </div>
                    </div>

                    {msg.sender === 'user' && (
                      <div className="w-7 h-7 rounded-lg bg-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-1">
                        <User className="w-4 h-4" />
                      </div>
                    )}
                  </div>
                ))}

                {isTyping && (
                  <div className="flex gap-3 items-center text-slate-400 text-xs pl-2 animate-pulse">
                    <Bot className="w-4 h-4 text-indigo-400 animate-bounce" />
                    <span>Querying institutional database views & RAG knowledge base...</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Quick Prompts */}
              <div className="p-3 border-t border-white/10 bg-slate-900/70">
                <span className="text-[10px] font-mono uppercase text-slate-400 block mb-1.5 font-semibold">
                  Suggested Questions
                </span>
                <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
                  {suggestedPrompts.map((p, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(p)}
                      className="px-2.5 py-1 rounded-lg text-xs bg-slate-800 hover:bg-slate-700 text-indigo-200 hover:text-white border border-white/5 whitespace-nowrap transition-colors shadow-sm"
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              {/* Input Form */}
              <div className="p-4 border-t border-white/10 bg-slate-900/90">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex items-center gap-2"
                >
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Ask about marks, attendance, fees, policies..."
                    className="flex-1 glass-input rounded-xl px-3.5 py-2.5 text-xs sm:text-sm text-slate-100 placeholder:text-slate-500 border border-white/10 focus:border-indigo-500 focus:outline-none"
                  />
                  <button
                    type="submit"
                    disabled={!inputText.trim() || isTyping}
                    className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-40 disabled:hover:bg-indigo-600 transition-colors shadow-lg shadow-indigo-600/30"
                    aria-label="Send message"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
