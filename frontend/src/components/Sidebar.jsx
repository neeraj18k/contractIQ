/**
 * Sidebar.jsx — session list + actions panel.
 *
 * Props:
 *   sessions          [{session_id, doc_id, filename, message_count, uploaded_at}]
 *   currentSessionId  string
 *   onSessionSelect   (session) => void
 *   onClearHistory    () => void   — clear messages, keep document
 *   onDeleteSession   () => void   — delete session + ChromaDB chunks
 *   onNewUpload       () => void   — navigate to /
 */
import React, { useState } from 'react';
import {
  FileText,
  Trash2,
  Plus,
  MessageSquare,
  ChevronRight,
  Clock,
  AlertTriangle,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const Sidebar = ({
  sessions         = [],
  currentSessionId = '',
  onSessionSelect,
  onClearHistory,
  onDeleteSession,
  onNewUpload,
}) => {
  const [confirmDelete, setConfirmDelete] = useState(false);

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div className="w-64 bg-gray-50 border-r border-gray-100
                    flex flex-col overflow-hidden shrink-0">

      {/* ── Logo / new upload ── */}
      <div className="px-4 py-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-blue-600" />
            <span className="font-semibold text-gray-900 text-sm">ContractIQ</span>
          </div>
        </div>
        <button
          onClick={onNewUpload}
          className="w-full flex items-center justify-center gap-2
                     px-3 py-2 rounded-xl text-sm font-medium
                     bg-blue-600 hover:bg-blue-700 text-white
                     transition-colors"
        >
          <Plus className="h-4 w-4" />
          Upload New Contract
        </button>
      </div>

      {/* ── Session list ── */}
      <div className="flex-1 overflow-y-auto py-2">
        <p className="px-4 py-2 text-xs font-medium text-gray-400 uppercase tracking-wide">
          Sessions
        </p>

        {sessions.length === 0 ? (
          <p className="px-4 text-xs text-gray-400 mt-1">No sessions yet.</p>
        ) : (
          <div className="space-y-0.5 px-2">
            {sessions.map((sess) => {
              const isActive = sess.session_id === currentSessionId;
              return (
                <button
                  key={sess.session_id}
                  onClick={() => onSessionSelect?.(sess)}
                  className={`
                    w-full text-left px-3 py-2.5 rounded-xl
                    flex items-start gap-2.5 transition-colors
                    ${isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'hover:bg-gray-100 text-gray-700'}
                  `}
                >
                  {/* Icon */}
                  <FileText className={`h-4 w-4 mt-0.5 shrink-0
                    ${isActive ? 'text-blue-500' : 'text-gray-400'}`}
                  />

                  {/* Info */}
                  <div className="min-w-0 flex-1">
                    <p className={`text-xs font-medium truncate
                      ${isActive ? 'text-blue-700' : 'text-gray-700'}`}>
                      {sess.filename || 'Untitled contract'}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="flex items-center gap-1 text-xs text-gray-400">
                        <MessageSquare className="h-3 w-3" />
                        {sess.message_count ?? 0}
                      </span>
                      {sess.uploaded_at && (
                        <span className="flex items-center gap-1 text-xs text-gray-400">
                          <Clock className="h-3 w-3" />
                          {_relativeTime(sess.uploaded_at)}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Active indicator */}
                  {isActive && (
                    <ChevronRight className="h-3.5 w-3.5 text-blue-400
                                             shrink-0 mt-0.5" />
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* ── Actions for current session ── */}
      <div className="border-t border-gray-100 p-3 space-y-1.5">
        {/* Clear history */}
        <button
          onClick={onClearHistory}
          className="w-full flex items-center gap-2 px-3 py-2
                     text-xs text-gray-600 hover:bg-gray-100
                     rounded-lg transition-colors"
        >
          <MessageSquare className="h-3.5 w-3.5" />
          Clear Chat History
        </button>

        {/* Delete session — two-step confirm */}
        {!confirmDelete ? (
          <button
            onClick={() => setConfirmDelete(true)}
            className="w-full flex items-center gap-2 px-3 py-2
                       text-xs text-red-500 hover:bg-red-50
                       rounded-lg transition-colors"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Delete Session
          </button>
        ) : (
          <div className="bg-red-50 rounded-lg p-2.5 space-y-2">
            <div className="flex items-center gap-1.5 text-xs text-red-600">
              <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
              <span>Delete document + history?</span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setConfirmDelete(false);
                  onDeleteSession?.();
                }}
                className="flex-1 py-1 text-xs bg-red-600 hover:bg-red-700
                           text-white rounded-md transition-colors"
              >
                Yes, delete
              </button>
              <button
                onClick={() => setConfirmDelete(false)}
                className="flex-1 py-1 text-xs bg-gray-200 hover:bg-gray-300
                           text-gray-700 rounded-md transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ── Helper ────────────────────────────────────────────────────────────────────
function _relativeTime(isoString) {
  try {
    return formatDistanceToNow(new Date(isoString), { addSuffix: true });
  } catch {
    return '';
  }
}

export default Sidebar;