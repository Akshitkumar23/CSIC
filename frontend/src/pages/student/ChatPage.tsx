import React, { useState, useRef, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { ChatMessage, ChatSession, Profile } from '../../types';
import { api } from '../../services/api';
import {
  Send,
  Bot,
  User,
  Plus,
  Trash2,
  MessageSquare,
  AlertCircle,
  ArrowRight,
  PanelLeftClose,
  PanelLeftOpen,
  X,
  SquarePen,
} from 'lucide-react';

interface ChatPageProps {
  currentUser: Profile;
}

export const ChatPage: React.FC<ChatPageProps> = ({ currentUser }) => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Active session state from URL
  const activeSessionId = searchParams.get('session');
  const currentSessionIdRef = useRef<string | null>(activeSessionId);
  currentSessionIdRef.current = activeSessionId;

  // Active request and init refs to prevent race conditions & duplicate loads
  const activeFetchReqIdRef = useRef<number>(0);
  const initialLoadDoneRef = useRef<boolean>(false);
  const skipNextSessionLoadRef = useRef<string | null>(null);

  // Sessions list state
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [sessionsError, setSessionsError] = useState<string | null>(null);

  // Active conversation thread state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [inputText, setInputText] = useState('');

  // Default sidebar closed for clean, distraction-free ChatGPT-style focus
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  // Scroll management
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isNearBottomRef = useRef<boolean>(true);
  const shouldForceScrollRef = useRef<boolean>(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Handle Escape key to dismiss mobile/desktop drawer
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && sidebarOpen) {
        setSidebarOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [sidebarOpen]);

  // Track scroll position to prevent auto-scrolling when user is reading past messages
  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    isNearBottomRef.current = scrollHeight - scrollTop - clientHeight < 120;
  };

  useEffect(() => {
    if (shouldForceScrollRef.current || isNearBottomRef.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      shouldForceScrollRef.current = false;
    }
  }, [messages, isSending]);

  // Load Sessions List & Initial Conversation (Single request execution)
  useEffect(() => {
    let isCancelled = false;

    const initData = async () => {
      setLoadingSessions(true);
      setSessionsError(null);

      try {
        const loadedSessions = await api.getChatSessions();
        if (isCancelled) return;

        setSessions(loadedSessions);
        setLoadingSessions(false);

        // Single initial load decision:
        const urlSessionId = searchParams.get('session');
        if (urlSessionId) {
          loadSessionMessages(urlSessionId);
        } else if (loadedSessions.length > 0) {
          // Default to most recent session
          const mostRecent = loadedSessions[0];
          setSearchParams({ session: mostRecent.id }, { replace: true });
          loadSessionMessages(mostRecent.id);
        } else {
          // Brand new empty state
          setMessages([]);
        }
      } catch (err: any) {
        if (isCancelled) return;
        setSessionsError('Unable to load past conversations.');
        setLoadingSessions(false);
      } finally {
        initialLoadDoneRef.current = true;
      }
    };

    initData();

    return () => {
      isCancelled = true;
    };
  }, []);

  // When activeSessionId changes in URL after initialization, safely load its messages
  useEffect(() => {
    if (!initialLoadDoneRef.current) return;

    if (skipNextSessionLoadRef.current === activeSessionId) {
      skipNextSessionLoadRef.current = null;
      return;
    }

    if (activeSessionId) {
      loadSessionMessages(activeSessionId);
    } else {
      setMessages([]);
    }
  }, [activeSessionId]);

  // Safe message history loader with race-condition guards
  const loadSessionMessages = async (sessionId: string) => {
    const requestId = ++activeFetchReqIdRef.current;
    setLoadingMessages(true);

    try {
      const history = await api.getSessionMessages(sessionId);
      // Race guard: If user switched sessions or a newer fetch started, discard
      if (requestId !== activeFetchReqIdRef.current || currentSessionIdRef.current !== sessionId) {
        return;
      }
      setMessages(history || []);
      shouldForceScrollRef.current = true;
    } catch (err) {
      console.error('Failed to load session history:', err);
      if (requestId === activeFetchReqIdRef.current && currentSessionIdRef.current === sessionId) {
        setMessages([]);
      }
    } finally {
      if (requestId === activeFetchReqIdRef.current) {
        setLoadingMessages(false);
      }
    }
  };

  const handleSelectSession = (sessionId: string) => {
    skipNextSessionLoadRef.current = null;
    if (sidebarOpen && typeof window !== 'undefined' && window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
    if (sessionId === activeSessionId) return;
    setSearchParams({ session: sessionId });
  };

  const handleNewChat = () => {
    skipNextSessionLoadRef.current = null;
    if (sidebarOpen && typeof window !== 'undefined' && window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
    setSearchParams({});
    setMessages([]);
    if (textareaRef.current) {
      textareaRef.current.focus();
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
          setMessages([]);
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
      textareaRef.current.style.height = '42px';
    }

    let targetSessionId = activeSessionId;

    // Temporary optimistic user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      session_id: targetSessionId || undefined,
      sender: 'user',
      text: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);
    shouldForceScrollRef.current = true;

    try {
      // If starting from a new conversation without session ID, create session first
      if (!targetSessionId) {
        const titleSnippet = trimmed.length > 35 ? trimmed.substring(0, 32) + '...' : trimmed;
        const newSess = await api.createChatSession(titleSnippet);
        targetSessionId = newSess.id;
        skipNextSessionLoadRef.current = newSess.id;
        setSessions((prev) => [newSess, ...prev]);
        setSearchParams({ session: newSess.id }, { replace: true });
        currentSessionIdRef.current = newSess.id;
      }

      const botReply = await api.sendChatMessage(trimmed, targetSessionId);

      // Race guard: Only append botReply if user is still in the same session
      if (currentSessionIdRef.current === targetSessionId) {
        setMessages((prev) => [...prev, botReply]);
        shouldForceScrollRef.current = true;
      }

      // Refresh sidebar preview
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
      console.error('Chat error:', err);
      // Friendly, non-technical error in UI
      if (currentSessionIdRef.current === targetSessionId) {
        setMessages((prev) => [
          ...prev,
          {
            id: `bot-err-${Date.now()}`,
            sender: 'bot',
            text: "I'm having trouble connecting to the university server right now. Please check your connection or try again in a moment.",
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            query_type: 'general',
          },
        ]);
        shouldForceScrollRef.current = true;
      }
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

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    // Auto-grow textarea smoothly up to 140px
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 140)}px`;
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
  const hasMessages = messages.length > 0;

  return (
    <div className="relative flex h-full w-full overflow-hidden bg-[#F8FAFC] text-[#101828]">
      {/* Mobile Drawer Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* ================= LEFT CONVERSATION HISTORY DRAWER ================= */}
      <div
        className={`bg-white border-r border-[#D8E0EA] flex flex-col shrink-0 transition-all duration-200 ${
          sidebarOpen
            ? 'fixed inset-y-0 left-0 z-40 w-72 sm:w-80 h-full shadow-2xl lg:static lg:h-full lg:shadow-none lg:w-72'
            : 'hidden'
        }`}
      >
        {/* Sidebar Header & New Chat Button */}
        <div className="p-3 border-b border-[#D8E0EA] bg-white flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-[#1D4ED8]" />
            <span className="font-semibold text-sm text-[#101828]">History</span>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={handleNewChat}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[#1D4ED8] hover:bg-[#1E40AF] text-white text-xs font-medium transition-colors shadow-2xs"
              title="Start a new chat"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>New Chat</span>
            </button>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
              aria-label="Close conversation history"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Sessions List Scroll Area */}
        <div className="flex-1 overflow-y-auto p-2 space-y-3">
          {loadingSessions ? (
            <div className="space-y-2 p-2">
              {[1, 2, 3].map((n) => (
                <div key={n} className="h-12 bg-slate-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : sessionsError ? (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">
              <div className="flex items-center gap-1.5 font-semibold mb-1">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
                <span>Failed to load history</span>
              </div>
              <p className="text-[11px] mb-2">{sessionsError}</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="p-6 text-center text-slate-400 text-xs">
              <MessageSquare className="w-7 h-7 text-slate-300 mx-auto mb-2" />
              <p className="font-medium text-slate-600">No conversations yet</p>
            </div>
          ) : (
            <>
              {/* TODAY */}
              {todaySessions.length > 0 && (
                <div>
                  <div className="px-2 pb-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Today
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
                              ? 'bg-blue-50/70 border-blue-200 text-[#101828] font-medium'
                              : 'bg-white hover:bg-slate-50 border-transparent text-slate-700'
                          }`}
                        >
                          <div className="min-w-0 flex-1 pr-2">
                            <div className="truncate font-medium text-[#101828] leading-tight">
                              {s.title}
                            </div>
                            <div className="truncate text-[11px] text-slate-400 mt-0.5">
                              {s.last_message_preview || 'No messages'}
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

              {/* PREVIOUS DAYS */}
              {previousSessions.length > 0 && (
                <div>
                  <div className="px-2 pb-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Previous
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
                              ? 'bg-blue-50/70 border-blue-200 text-[#101828] font-medium'
                              : 'bg-white hover:bg-slate-50 border-transparent text-slate-700'
                          }`}
                        >
                          <div className="min-w-0 flex-1 pr-2">
                            <div className="truncate font-medium text-[#101828] leading-tight">
                              {s.title}
                            </div>
                            <div className="truncate text-[11px] text-slate-400 mt-0.5">
                              {s.last_message_preview || 'No messages'}
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
      </div>

      {/* ================= MAIN CHAT WORKSPACE ================= */}
      <div className="flex-1 flex flex-col h-full min-w-0 overflow-hidden bg-[#F8FAFC]">
        {/* Minimal Header */}
        <div className="h-14 px-4 bg-white border-b border-[#D8E0EA] flex items-center justify-between shrink-0 shadow-2xs gap-3">
          <div className="flex items-center gap-2.5 min-w-0">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 text-slate-600 hover:text-[#101828] hover:bg-slate-100 rounded-lg transition-colors shrink-0"
              title={sidebarOpen ? 'Hide history' : 'Show history'}
              aria-label="Toggle history"
            >
              {sidebarOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeftOpen className="w-4 h-4 text-[#1D4ED8]" />}
            </button>

            <div className="min-w-0">
              <h1 className="text-sm font-bold text-[#101828] truncate leading-tight">
                CSIC Assistant
              </h1>
              <p className="text-[11px] text-slate-500 truncate">
                Simple academic chat
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={handleNewChat}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-white hover:bg-slate-50 border border-[#D8E0EA] text-[#101828] transition-colors shadow-2xs"
              title="Start a new chat"
            >
              <SquarePen className="w-3.5 h-3.5 text-[#1D4ED8]" />
              <span className="hidden sm:inline">New Chat</span>
            </button>
          </div>
        </div>

        {/* Message Thread Container */}
        <div
          ref={scrollContainerRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5"
        >
          {loadingMessages ? (
            <div className="flex items-center justify-center h-48 text-slate-400 text-xs">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-[#1D4ED8] animate-bounce [animation-delay:-0.3s]" />
                <span className="w-2 h-2 rounded-full bg-[#1D4ED8] animate-bounce [animation-delay:-0.15s]" />
                <span className="w-2 h-2 rounded-full bg-[#1D4ED8] animate-bounce" />
              </div>
            </div>
          ) : !hasMessages ? (
            /* Clean Empty Welcome State */
            <div className="flex flex-col items-center justify-center min-h-[60vh] max-w-lg mx-auto text-center px-4 py-8 space-y-6">
              <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center text-[#1D4ED8] shadow-xs">
                <Bot className="w-6 h-6" />
              </div>

              <div className="space-y-1.5">
                <h2 className="text-xl sm:text-2xl font-bold text-[#101828]">
                  What can I help you with{currentUser.full_name ? `, ${currentUser.full_name.split(' ')[0]}` : ''}?
                </h2>
                <p className="text-xs sm:text-sm text-[#475467]">
                  Ask about attendance, marks, fees or your timetable.
                </p>
              </div>

              {/* 4 Clean Suggestion Chips */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full pt-2">
                {[
                  { label: 'Check my attendance', query: 'What is my attendance percentage?' },
                  { label: 'Show my marks', query: 'Show my Mid-Term exam marks' },
                  { label: 'Fees due', query: 'Do I have any pending fee invoices?' },
                  { label: "Today's timetable", query: 'What is my timetable today?' },
                ].map((chip, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(chip.query)}
                    className="p-3 text-left rounded-xl border border-[#D8E0EA] bg-white hover:border-[#1D4ED8] hover:bg-blue-50/50 text-[#101828] text-xs font-medium transition-all shadow-2xs group flex items-center justify-between"
                  >
                    <span>{chip.label}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-[#1D4ED8] transition-colors" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2.5 sm:gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'bot' && (
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#14253D] text-white flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
                    <Bot className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[88%] sm:max-w-[78%] rounded-2xl p-3.5 sm:p-4 text-sm leading-relaxed shadow-2xs break-words overflow-x-auto ${
                    msg.sender === 'user'
                      ? 'bg-[#1D4ED8] text-white rounded-tr-xs'
                      : 'bg-white text-[#101828] border border-[#D8E0EA] rounded-tl-xs'
                  }`}
                >
                  {/* Message Body */}
                  {msg.sender === 'user' ? (
                    <div className="text-white font-normal whitespace-pre-wrap">
                      {msg.text}
                    </div>
                  ) : (
                    <div className="prose prose-sm max-w-none text-[#101828] prose-p:leading-relaxed prose-headings:text-[#101828] prose-headings:font-bold prose-headings:my-2 prose-a:text-[#1D4ED8] prose-a:font-semibold prose-a:no-underline hover:prose-a:underline">
                      <ReactMarkdown
                        components={{
                          table: ({ children }) => (
                            <div className="my-3 overflow-x-auto rounded-lg border border-[#D8E0EA]">
                              <table className="min-w-full text-left text-xs divide-y divide-[#D8E0EA]">
                                {children}
                              </table>
                            </div>
                          ),
                          thead: ({ children }) => (
                            <thead className="bg-[#F8FAFC] text-slate-700 font-semibold">
                              {children}
                            </thead>
                          ),
                          th: ({ children }) => (
                            <th className="px-3 py-2 text-xs font-semibold text-slate-700">
                              {children}
                            </th>
                          ),
                          tbody: ({ children }) => (
                            <tbody className="divide-y divide-[#E2E8F0] bg-white">
                              {children}
                            </tbody>
                          ),
                          td: ({ children }) => (
                            <td className="px-3 py-2 text-xs text-slate-700 whitespace-nowrap">
                              {children}
                            </td>
                          ),
                          code: ({ inline, className, children, ...props }: any) => {
                            return inline ? (
                              <code
                                className="px-1.5 py-0.5 rounded bg-slate-100 font-mono text-[11px] text-slate-800"
                                {...props}
                              >
                                {children}
                              </code>
                            ) : (
                              <pre className="my-2 p-3 rounded-lg bg-slate-900 text-slate-100 overflow-x-auto font-mono text-xs">
                                <code {...props}>{children}</code>
                              </pre>
                            );
                          },
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

                  {/* Compact Subtle Sources Citation */}
                  {msg.sender === 'bot' && msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-slate-100 flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] text-slate-400 font-medium">Source:</span>
                      {msg.sources.map((src, i) => (
                        <span
                          key={i}
                          className="text-[11px] px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200 text-slate-600 font-medium"
                        >
                          {src}
                        </span>
                      ))}
                    </div>
                  )}

                  <div
                    className={`text-[10px] mt-1.5 ${
                      msg.sender === 'user' ? 'text-blue-200 text-right' : 'text-slate-400'
                    }`}
                  >
                    {msg.timestamp}
                  </div>
                </div>

                {msg.sender === 'user' && (
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#1D4ED8] text-white flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
                    <User className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  </div>
                )}
              </div>
            ))
          )}

          {/* ChatGPT-style Typing Indicator */}
          {isSending && (
            <div className="flex gap-2.5 sm:gap-3 justify-start items-center">
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#14253D] text-white flex items-center justify-center shrink-0 shadow-xs">
                <Bot className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              </div>
              <div className="px-4 py-3 bg-white border border-[#D8E0EA] rounded-2xl rounded-tl-xs shadow-2xs flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#1D4ED8] animate-bounce [animation-delay:-0.3s]" />
                <span className="w-2 h-2 rounded-full bg-[#1D4ED8] animate-bounce [animation-delay:-0.15s]" />
                <span className="w-2 h-2 rounded-full bg-[#1D4ED8] animate-bounce" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Composer Bar */}
        <div className="p-3 sm:p-4 bg-white border-t border-[#D8E0EA] shrink-0">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-end gap-2 max-w-3xl mx-auto"
          >
            <div className="flex-1 relative rounded-2xl border border-[#D8E0EA] bg-white focus-within:border-[#1D4ED8] focus-within:ring-2 focus-within:ring-blue-100 transition-all min-w-0">
              <textarea
                ref={textareaRef}
                rows={1}
                value={inputText}
                onChange={handleTextareaChange}
                onKeyDown={handleKeyDown}
                placeholder="Message CSIC Assistant…"
                className="w-full text-xs sm:text-sm py-2.5 px-3.5 bg-transparent resize-none outline-none text-[#101828] placeholder:text-slate-400 max-h-36"
                style={{ minHeight: '42px' }}
              />
            </div>

            <button
              type="submit"
              disabled={!inputText.trim() || isSending}
              className="h-[42px] w-[42px] sm:w-auto sm:px-4 rounded-xl bg-[#1D4ED8] hover:bg-[#1E40AF] text-white font-semibold text-xs sm:text-sm disabled:opacity-40 transition-colors shadow-2xs flex items-center justify-center gap-1.5 shrink-0"
              aria-label="Send message"
            >
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </form>
          <div className="text-[11px] text-center text-slate-400 mt-2 hidden sm:block">
            CSIC Assistant answers from verified academic records and university policy.
          </div>
        </div>
      </div>
    </div>
  );
};
