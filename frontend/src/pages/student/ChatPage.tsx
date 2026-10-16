import React, { useState, useRef, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { ChatMessage, ChatSession, Profile } from '../../types';
import { api } from '../../services/api';
import {
  Send,
  Bot,
  User,
  FileText,
  Database,
  BookOpen,
  ShieldCheck,
  Plus,
  Trash2,
  MessageSquare,
  AlertCircle,
  HelpCircle,
  ArrowRight,
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-react';

interface ChatPageProps {
  currentUser: Profile;
}

export const ChatPage: React.FC<ChatPageProps> = ({ currentUser }) => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Active session state from URL
  const activeSessionId = searchParams.get('session');

  // Sessions list state
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [sessionsError, setSessionsError] = useState<string | null>(null);

  // Active conversation thread state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [inputText, setInputText] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Prompt suggestions
  const [suggestedPrompts, setSuggestedPrompts] = useState<string[]>([
    'What is my attendance percentage?',
    'What about CS401?',
    'How many classes to recover?',
    'Show my Mid-Term exam marks',
    'Do I have any pending fee invoices?',
    'What is my timetable today?',
    'What is the attendance policy?',
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  // Load Sessions List on mount
  const fetchSessions = async () => {
    setLoadingSessions(true);
    setSessionsError(null);
    try {
      const data = await api.getChatSessions();
      setSessions(data);
      return data;
    } catch (err: any) {
      setSessionsError(err.message || 'Failed to load conversation history');
      return [];
    } finally {
      setLoadingSessions(false);
    }
  };

  useEffect(() => {
    const initData = async () => {
      // Load suggestions
      try {
        const prompts = await api.getChatSuggestions();
        if (prompts && prompts.length > 0) {
          setSuggestedPrompts(prompts);
        }
      } catch {
        // use defaults
      }

      // Load sessions
      const loadedSessions = await fetchSessions();

      // If URL already has session ID, load it
      if (activeSessionId) {
        loadSessionMessages(activeSessionId);
      } else if (loadedSessions.length > 0) {
        // Default to most recent session
        const mostRecent = loadedSessions[0];
        setSearchParams({ session: mostRecent.id }, { replace: true });
        loadSessionMessages(mostRecent.id);
      } else {
        // Brand new state
        setMessages([getWelcomeMessage()]);
      }
    };

    initData();
  }, []);

  // When activeSessionId changes in URL, load its messages
  useEffect(() => {
    if (activeSessionId) {
      loadSessionMessages(activeSessionId);
    }
  }, [activeSessionId]);

  const getWelcomeMessage = (): ChatMessage => ({
    id: `welcome-${Date.now()}`,
    sender: 'bot',
    text: `👋 Hello **${currentUser.full_name}**!\n\nI am your **CSIC Academic Assistant**, connected directly to your university student records in the relational database.\n\nYou can ask me in plain language about:\n- **Attendance records & recovery calculations** (e.g., *"What is my attendance?"*, *"What about CS401?"*, *"How many classes to recover?"*)\n- **Exam performance & GPAs** (*"Show my marks"*)\n- **Fee account & invoices** (*"Do I owe any tuition fees?"*)\n- **Class timetable** (*"What is my schedule today?"*)\n- **University Regulations & Policies** (*"What is the medical leave rule?"*)\n\nSelect a suggested prompt below or type your question to start!`,
    timestamp: 'Just now',
    query_type: 'general',
  });

  const loadSessionMessages = async (sessionId: string) => {
    setLoadingMessages(true);
    try {
      const history = await api.getSessionMessages(sessionId);
      if (history && history.length > 0) {
        setMessages(history);
      } else {
        setMessages([getWelcomeMessage()]);
      }
    } catch {
      setMessages([
        {
          id: `err-${Date.now()}`,
          sender: 'bot',
          text: '⚠️ Unable to retrieve conversation history from the academic server. Please check your connection or start a new chat.',
          timestamp: 'Just now',
          query_type: 'general',
        },
      ]);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleSelectSession = (sessionId: string) => {
    if (sessionId === activeSessionId) return;
    setSearchParams({ session: sessionId });
  };

  const handleNewChat = async () => {
    try {
      const newSession = await api.createChatSession('New Conversation');
      setSessions((prev) => [newSession, ...prev]);
      setSearchParams({ session: newSession.id });
      setMessages([getWelcomeMessage()]);
    } catch (err: any) {
      // Fallback: clear param to start fresh local thread
      setSearchParams({});
      setMessages([getWelcomeMessage()]);
    }
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteChatSession(sessionId);
      const remaining = sessions.filter((s) => s.id !== sessionId);
      setSessions(remaining);

      if (activeSessionId === sessionId) {
        if (remaining.length > 0) {
          setSearchParams({ session: remaining[0].id });
        } else {
          setSearchParams({});
          setMessages([getWelcomeMessage()]);
        }
      }
    } catch (err) {
      console.error('Failed to delete session', err);
    }
  };

  const handleSendMessage = async (textOverride?: string) => {
    const textToSend = textOverride || inputText;
    if (!textToSend.trim() || isSending) return;

    const trimmed = textToSend.trim();
    setInputText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    // Temporary optimistic user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      session_id: activeSessionId || undefined,
      sender: 'user',
      text: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);

    try {
      // Ensure we have a session ID
      let targetSessionId = activeSessionId;
      if (!targetSessionId) {
        const titleSnippet = trimmed.length > 35 ? trimmed.substring(0, 32) + '...' : trimmed;
        const newSess = await api.createChatSession(titleSnippet);
        targetSessionId = newSess.id;
        setSessions((prev) => [newSess, ...prev]);
        setSearchParams({ session: newSess.id }, { replace: true });
      }

      const botReply = await api.sendChatMessage(trimmed, targetSessionId);
      setMessages((prev) => [...prev, botReply]);

      // Refresh session preview in sidebar
      setSessions((prev) =>
        prev.map((s) =>
          s.id === targetSessionId
            ? {
                ...s,
                last_message_preview: botReply.text.substring(0, 75) + '...',
                updated_at: new Date().toISOString(),
              }
            : s
        )
      );
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: 'bot',
          text: `⚠️ **Connection / Verification Notice**\n\n${err.message || 'Unable to verify your records from the academic database. Please check your login session or network.'}`,
          timestamp: 'Just now',
          query_type: 'general',
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Group sessions into Today vs Previous
  const groupSessions = (list: ChatSession[]) => {
    const today: ChatSession[] = [];
    const previous: ChatSession[] = [];
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();

    list.forEach((s) => {
      const sDate = new Date(s.updated_at || s.created_at).getTime();
      if (!isNaN(sDate) && sDate >= todayStart) {
        today.push(s);
      } else {
        previous.push(s);
      }
    });

    return { today, previous };
  };

  const { today: todaySessions, previous: previousSessions } = groupSessions(sessions);
  const activeSession = sessions.find((s) => s.id === activeSessionId);

  return (
    <div className="flex h-[calc(100vh-4.25rem)] w-full overflow-hidden bg-[#F1F4F8] text-[#101828]">
      {/* ================= LEFT PANE: CONVERSATION HISTORY ================= */}
      <div
        className={`bg-white border-r border-[#D8E0EA] flex flex-col shrink-0 transition-all duration-200 z-20 ${
          sidebarOpen ? 'w-72 lg:w-80' : 'w-0 overflow-hidden border-none'
        }`}
      >
        {/* Sidebar Header & New Chat Button */}
        <div className="p-3.5 border-b border-[#D8E0EA] bg-white flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-[#1D4ED8]" />
            <span className="font-bold text-sm text-[#101828] tracking-tight">Conversations</span>
          </div>

          <button
            onClick={handleNewChat}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1D4ED8] hover:bg-[#1E40AF] text-white text-xs font-semibold shadow-xs transition-colors"
            title="Start a new academic conversation"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Sessions List Scroll Area */}
        <div className="flex-1 overflow-y-auto p-2.5 space-y-4">
          {loadingSessions ? (
            <div className="space-y-2.5 p-2">
              {[1, 2, 3].map((n) => (
                <div key={n} className="h-14 bg-slate-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : sessionsError ? (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">
              <div className="flex items-center gap-1.5 font-semibold mb-1">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
                <span>Failed to load history</span>
              </div>
              <p className="text-[11px] mb-2">{sessionsError}</p>
              <button
                onClick={fetchSessions}
                className="px-2 py-1 bg-white border border-red-300 rounded text-[11px] font-medium hover:bg-red-50"
              >
                Retry
              </button>
            </div>
          ) : sessions.length === 0 ? (
            <div className="p-6 text-center text-slate-500 text-xs">
              <MessageSquare className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <p className="font-semibold text-slate-700">No conversations yet</p>
              <p className="text-[11px] text-slate-500 mt-1">
                Click "+ New Chat" above to ask about your attendance, marks, fees, or timetable.
              </p>
            </div>
          ) : (
            <>
              {/* TODAY GROUP */}
              {todaySessions.length > 0 && (
                <div>
                  <div className="px-2.5 pb-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Today ({todaySessions.length})
                  </div>
                  <div className="space-y-1">
                    {todaySessions.map((s) => {
                      const isActive = s.id === activeSessionId;
                      return (
                        <div
                          key={s.id}
                          onClick={() => handleSelectSession(s.id)}
                          className={`group flex items-start justify-between p-2.5 rounded-lg text-xs cursor-pointer transition-all border ${
                            isActive
                              ? 'bg-[#F1F4F8] border-[#1D4ED8] text-[#101828] font-medium shadow-xs'
                              : 'bg-white hover:bg-slate-50 border-transparent text-slate-700'
                          }`}
                        >
                          <div className="min-w-0 flex-1 pr-2">
                            <div className="truncate font-semibold text-[#101828] leading-tight">
                              {s.title}
                            </div>
                            <div className="truncate text-[11px] text-[#475467] mt-1">
                              {s.last_message_preview || 'No messages yet'}
                            </div>
                          </div>
                          <button
                            onClick={(e) => handleDeleteSession(s.id, e)}
                            className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-600 rounded transition-opacity"
                            title="Delete conversation"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* PREVIOUS DAYS GROUP */}
              {previousSessions.length > 0 && (
                <div>
                  <div className="px-2.5 pb-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Previous Conversations ({previousSessions.length})
                  </div>
                  <div className="space-y-1">
                    {previousSessions.map((s) => {
                      const isActive = s.id === activeSessionId;
                      return (
                        <div
                          key={s.id}
                          onClick={() => handleSelectSession(s.id)}
                          className={`group flex items-start justify-between p-2.5 rounded-lg text-xs cursor-pointer transition-all border ${
                            isActive
                              ? 'bg-[#F1F4F8] border-[#1D4ED8] text-[#101828] font-medium shadow-xs'
                              : 'bg-white hover:bg-slate-50 border-transparent text-slate-700'
                          }`}
                        >
                          <div className="min-w-0 flex-1 pr-2">
                            <div className="truncate font-semibold text-[#101828] leading-tight">
                              {s.title}
                            </div>
                            <div className="truncate text-[11px] text-[#475467] mt-1">
                              {s.last_message_preview || 'No messages yet'}
                            </div>
                          </div>
                          <button
                            onClick={(e) => handleDeleteSession(s.id, e)}
                            className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-600 rounded transition-opacity"
                            title="Delete conversation"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Sidebar Footer Info */}
        <div className="p-3 border-t border-[#D8E0EA] bg-[#F1F4F8] text-[11px] text-[#475467] flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>SQL Relational Persistence</span>
          </span>
          <span className="font-mono text-[10px] text-slate-500">v2.1</span>
        </div>
      </div>

      {/* ================= MAIN RIGHT PANE: CHAT WORKSPACE ================= */}
      <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#F1F4F8]">
        {/* Top Workspace Header Bar */}
        <div className="h-14 px-4 bg-white border-b border-[#D8E0EA] flex items-center justify-between shrink-0 shadow-2xs">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 text-slate-600 hover:text-[#101828] hover:bg-slate-100 rounded-lg transition-colors"
              title={sidebarOpen ? 'Hide conversation history' : 'Show conversation history'}
            >
              {sidebarOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeftOpen className="w-4 h-4 text-[#1D4ED8]" />}
            </button>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-bold text-[#101828] truncate max-w-xs sm:max-w-md">
                  {activeSession ? activeSession.title : 'New Academic Conversation'}
                </h1>
                <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#ECFDF3] text-[#027A48] border border-[#A6F4C5]">
                  <ShieldCheck className="w-3 h-3" />
                  Grounded Identity
                </span>
              </div>
              <div className="text-[11px] text-[#475467]">
                Authenticated: <strong className="text-[#101828]">{currentUser.full_name}</strong> (Roll: {currentUser.roll_number || currentUser.id}) • {currentUser.department || 'Computer Science'}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleNewChat}
              className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold rounded-lg bg-white hover:bg-slate-50 border border-[#D8E0EA] text-[#101828] transition-colors"
            >
              <Plus className="w-3.5 h-3.5 text-[#1D4ED8]" />
              <span className="hidden sm:inline">New Session</span>
            </button>
          </div>
        </div>

        {/* Message Thread Container */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
          {loadingMessages ? (
            <div className="flex items-center justify-center h-48 text-slate-500 text-xs">
              <Bot className="w-5 h-5 text-[#1D4ED8] animate-spin mr-2" />
              <span>Loading conversation thread from database...</span>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'bot' && (
                  <div className="w-8 h-8 rounded-lg bg-[#14253D] text-white flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[88%] sm:max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed shadow-xs ${
                    msg.sender === 'user'
                      ? 'bg-[#14253D] text-white rounded-tr-none'
                      : 'bg-white text-[#101828] border border-[#D8E0EA] rounded-tl-none'
                  }`}
                >
                  {/* Status Indicator Chip */}
                  {msg.sender === 'bot' && msg.query_type && (
                    <div className="mb-2.5 flex items-center gap-2">
                      {['attendance', 'marks', 'fees', 'timetable', 'notices'].includes(msg.query_type) ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-mono font-semibold px-2 py-0.5 rounded-md bg-[#ECFDF3] text-[#027A48] border border-[#A6F4C5]">
                          <Database className="w-3 h-3 text-[#027A48]" />
                          Verified Database Fact ({msg.query_type.toUpperCase()})
                        </span>
                      ) : ['policy_document', 'rag_document'].includes(msg.query_type) ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-mono font-semibold px-2 py-0.5 rounded-md bg-[#FFFAEB] text-[#B54708] border border-[#FEDF89]">
                          <BookOpen className="w-3 h-3 text-[#B54708]" />
                          University Policy Guide
                        </span>
                      ) : null}
                    </div>
                  )}

                  {/* Message Body */}
                  {msg.sender === 'user' ? (
                    <div className="text-white font-medium leading-relaxed whitespace-pre-wrap">
                      {msg.text}
                    </div>
                  ) : (
                    <div className="prose prose-sm max-w-none text-[#101828] prose-p:leading-relaxed prose-headings:text-[#101828] prose-headings:font-bold prose-headings:my-2 prose-a:text-[#1D4ED8] prose-a:font-semibold prose-a:no-underline hover:prose-a:underline prose-table:my-2 prose-th:bg-slate-100 prose-th:p-2 prose-td:p-2 prose-td:border prose-td:border-slate-200">
                      <ReactMarkdown
                        components={{
                          a: ({ href, children }) => {
                            if (href && href.startsWith('/')) {
                              return (
                                <Link
                                  to={href}
                                  className="inline-flex items-center gap-1 text-[#1D4ED8] hover:text-[#1E40AF] font-semibold underline decoration-2 underline-offset-2"
                                >
                                  {children}
                                  <ArrowRight className="w-3.5 h-3.5" />
                                </Link>
                              );
                            }
                            return (
                              <a
                                href={href}
                                target="_blank"
                                rel="noreferrer"
                                className="text-[#1D4ED8] hover:underline"
                              >
                                {children}
                              </a>
                            );
                          },
                        }}
                      >
                        {msg.text}
                      </ReactMarkdown>
                    </div>
                  )}

                  {/* Grounding Source Citations */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-[#D8E0EA] space-y-1.5">
                      <span className="text-[10px] uppercase font-mono text-[#475467] font-bold block">
                        Verified Sources & Grounding:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.sources.map((src, i) => (
                          <span
                            key={i}
                            className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-[#475467] border border-[#D8E0EA] flex items-center gap-1"
                          >
                            <FileText className="w-3 h-3 text-[#1D4ED8]" />
                            {src}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div
                    className={`text-[10px] mt-2 font-mono ${
                      msg.sender === 'user' ? 'text-slate-300 text-right' : 'text-[#475467]'
                    }`}
                  >
                    {msg.timestamp}
                  </div>
                </div>

                {msg.sender === 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-[#1D4ED8] text-white flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))
          )}

          {isSending && (
            <div className="flex gap-3 items-center text-[#475467] text-xs pl-2 py-2">
              <Bot className="w-4 h-4 text-[#1D4ED8] animate-spin" />
              <span>Querying verified relational database & computing academic impact...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompts Shelf */}
        <div className="px-4 py-2 bg-white border-t border-[#D8E0EA]">
          <div className="flex items-center gap-1.5 text-[11px] font-mono uppercase font-semibold text-[#475467] mb-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-[#1D4ED8]" />
            <span>Suggested Academic Inquiries</span>
          </div>
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-thin">
            {suggestedPrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(p)}
                disabled={isSending}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-[#F1F4F8] hover:bg-blue-50 text-[#101828] hover:text-[#1D4ED8] border border-[#D8E0EA] hover:border-[#1D4ED8] whitespace-nowrap transition-colors shadow-2xs disabled:opacity-50"
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Input Composer Bar */}
        <div className="p-3.5 bg-white border-t border-[#D8E0EA]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-end gap-2.5 max-w-4xl mx-auto"
          >
            <div className="flex-1 relative rounded-xl border border-[#D8E0EA] bg-white focus-within:border-[#1D4ED8] focus-within:ring-2 focus-within:ring-blue-100 transition-all">
              <textarea
                ref={textareaRef}
                rows={1}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about attendance, CS401, recovery classes, marks, fees, timetable, or regulations..."
                className="w-full text-sm py-2.5 px-3.5 bg-transparent resize-none outline-none text-[#101828] placeholder:text-slate-400 max-h-32"
                style={{ minHeight: '42px' }}
              />
            </div>

            <button
              type="submit"
              disabled={!inputText.trim() || isSending}
              className="h-[42px] px-5 rounded-xl bg-[#1D4ED8] hover:bg-[#1E40AF] text-white font-semibold text-sm disabled:opacity-40 transition-colors shadow-xs flex items-center justify-center gap-1.5 shrink-0"
              aria-label="Send message"
            >
              <span>Send</span>
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="text-[10px] text-center text-[#475467] mt-1.5">
            Press <kbd className="px-1 py-0.5 bg-slate-100 rounded border border-slate-200">Enter</kbd> to send, <kbd className="px-1 py-0.5 bg-slate-100 rounded border border-slate-200">Shift + Enter</kbd> for newline. Zero fake answers guaranteed.
          </div>
        </div>
      </div>
    </div>
  );
};
