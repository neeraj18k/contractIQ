/**
 * Chat.jsx — main query interface.
 *
 * Props (from App.jsx):
 *   session         { sessionId, docId, filename, chunkCount, pageCount }
 *   onSessionChange (newSession) => void   — sidebar session switch
 *   onSessionClear  ()           => void   — session deleted
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate }    from 'react-router-dom';
import { FileText, Plus } from 'lucide-react';

import ChatWindow      from '../components/ChatWindow';
import ClauseHighlight from '../components/ClauseHighlight';
import Sidebar         from '../components/Sidebar';
import { useStream }   from '../hooks/useStream';
import {
  getSessionHistory,
  clearSession,
  deleteSession,
  listSessions,
} from '../api/axios';

const Chat = ({ session, onSessionChange, onSessionClear }) => {
  const navigate = useNavigate();

  // ── Derived from prop ───────────────────────────────────────────────────────
  const { sessionId, docId, filename, chunkCount, pageCount } = session;

  // ── State ───────────────────────────────────────────────────────────────────
  const [messages,      setMessages]      = useState([]);
  const [inputValue,    setInputValue]    = useState('');
  const [allSessions,   setAllSessions]   = useState([]);
  const [historyLoaded, setHistoryLoaded] = useState(false);

  const inputRef = useRef(null);

  const {
    streamedText,
    sources,
    isStreaming,
    isDone,
    error,
    sendQuery,
    resetStream,
  } = useStream();

  // ── Load session history on mount / session change ──────────────────────────
  useEffect(() => {
    setMessages([]);
    setHistoryLoaded(false);
    resetStream();

    const loadHistory = async () => {
      try {
        const data = await getSessionHistory(sessionId);
        // data.messages is list[dict] from session_store.get_history()
        const msgs = (data.messages || []).map((m) => ({
          role:      m.role,
          content:   m.content,
          timestamp: m.timestamp,
        }));
        setMessages(msgs);
      } catch (err) {
        // 404 = fresh session, no history yet — not an error
        if (!err.message?.includes('404')) {
          console.error('[Chat] Failed to load history:', err.message);
        }
      } finally {
        setHistoryLoaded(true);
      }
    };

    loadHistory();
  }, [sessionId]);   // re-run when session switches

  // ── Load sidebar session list ───────────────────────────────────────────────
  useEffect(() => {
    const load = async () => {
      try {
        const data = await listSessions();
        setAllSessions(data.sessions || []);
      } catch (err) {
        console.error('[Chat] Failed to load sessions:', err.message);
      }
    };
    load();
  }, [sessionId]);   // refresh after session changes

  // ── Append assistant message when stream completes ──────────────────────────
  useEffect(() => {
    if (isDone && streamedText.trim()) {
      setMessages((prev) => {
        // Avoid duplicate if already appended
        const last = prev[prev.length - 1];
        if (last?.role === 'assistant' && last?.content === streamedText) {
          return prev;
        }
        return [...prev, { role: 'assistant', content: streamedText }];
      });
    }
  }, [isDone]);   // only fires when stream finishes

  // ── Send message ────────────────────────────────────────────────────────────
  const handleSendMessage = useCallback(async () => {
    const query = inputValue.trim();
    if (!query || isStreaming) return;

    setInputValue('');
    resetStream();

    // Optimistically add user message
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: query, timestamp: new Date().toISOString() },
    ]);

    // sendQuery(query, sessionId, docId?)
    // docId optional — server resolves from session_store
    await sendQuery(query, sessionId, docId);

    // Re-focus input after send
    inputRef.current?.focus();
  }, [inputValue, isStreaming, sessionId, docId, sendQuery, resetStream]);

  // ── Enter key ───────────────────────────────────────────────────────────────
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  // ── Clear history ───────────────────────────────────────────────────────────
  const handleClearHistory = useCallback(async () => {
    if (!window.confirm('Clear chat history? The document will remain available.')) return;
    try {
      await clearSession(sessionId);
      setMessages([]);
      resetStream();
    } catch (err) {
      console.error('[Chat] Clear session failed:', err.message);
    }
  }, [sessionId, resetStream]);

  // ── Delete session ──────────────────────────────────────────────────────────
  const handleDeleteSession = useCallback(async () => {
    if (!window.confirm(
      `Delete session for "${filename}"?\nThis will remove the document and all chat history.`
    )) return;
    try {
      await deleteSession(sessionId);
      onSessionClear?.();
      navigate('/');
    } catch (err) {
      console.error('[Chat] Delete session failed:', err.message);
    }
  }, [sessionId, filename, onSessionClear, navigate]);

  // ── Sidebar session switch ──────────────────────────────────────────────────
  const handleSessionSelect = useCallback((sess) => {
    onSessionChange?.({
      sessionId:  sess.session_id,
      docId:      sess.doc_id,
      filename:   sess.filename   || 'Contract',
      chunkCount: sess.chunk_count || 0,
      pageCount:  sess.page_count  || 0,
    });
  }, [onSessionChange]);

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div className="flex h-screen bg-white overflow-hidden">

      {/* ── Sidebar ── */}
      <Sidebar
        sessions={allSessions}
        currentSessionId={sessionId}
        onSessionSelect={handleSessionSelect}
        onClearHistory={handleClearHistory}
        onDeleteSession={handleDeleteSession}
        onNewUpload={() => navigate('/')}
      />

      {/* ── Main panel ── */}
      <div className="flex-1 flex min-w-0">

        {/* Chat column */}
        <div className="flex-1 flex flex-col border-r border-gray-100 min-w-0">

          {/* Header */}
          <div className="flex items-center justify-between
                          bg-gradient-to-r from-blue-50 to-indigo-50
                          border-b border-gray-200 px-5 py-3 shrink-0">
            <div className="flex items-center gap-2 min-w-0">
              <FileText className="h-4 w-4 text-blue-600 shrink-0" />
              <div className="min-w-0">
                <p className="font-semibold text-gray-900 text-sm truncate">
                  {filename}
                </p>
                <p className="text-xs text-gray-400">
                  {chunkCount} chunks • {pageCount} pages •
                  session {sessionId.slice(0, 8)}…
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-1.5 text-xs text-blue-600
                         hover:text-blue-800 font-medium shrink-0 ml-3"
            >
              <Plus className="h-3.5 w-3.5" />
              New upload
            </button>
          </div>

          {/* Chat window */}
          <ChatWindow
            messages={messages}
            isStreaming={isStreaming}
            streamedText={streamedText}
            inputValue={inputValue}
            inputRef={inputRef}
            onInputChange={setInputValue}
            onSendMessage={handleSendMessage}
            onKeyDown={handleKeyDown}
            historyLoaded={historyLoaded}
          />
        </div>

        {/* Sources panel */}
        <div className="w-80 hidden lg:flex flex-col shrink-0">
          <ClauseHighlight sources={sources} />
        </div>
      </div>

      {/* ── Error toast ── */}
      {error && (
        <div className="fixed bottom-4 right-4 z-50 bg-red-500 text-white
                        px-4 py-3 rounded-lg shadow-lg text-sm max-w-sm">
          ⚠ {error}
        </div>
      )}
    </div>
  );
};

export default Chat;