/**
 * ClauseHighlight.jsx — right panel showing RAG source citations.
 * Reads both `preview` and `text` fields — works with old + new backend.
 */
import React, { useState, memo } from 'react';
import { FileText, ChevronDown, ChevronUp, BookOpen } from 'lucide-react';

const ClauseHighlight = ({ sources = [] }) => {
  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-slate-50 to-white
                    border-l border-gray-100 overflow-hidden">

      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 shrink-0">
        <h3 className="font-semibold text-gray-800 text-sm flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-blue-500" />
          Source Clauses
          {sources.length > 0 && (
            <span className="ml-auto bg-blue-100 text-blue-600
                             text-xs font-medium px-2 py-0.5 rounded-full">
              {sources.length}
            </span>
          )}
        </h3>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto px-3 py-3">
        {sources.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="space-y-3">
            {sources.map((source, idx) => (
              <SourceCard
                key={`${source.page_num}-${source.chunk_index}-${idx}`}
                source={source}
                index={idx + 1}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};


const SourceCard = memo(({ source, index }) => {
  const [expanded, setExpanded] = useState(false);

  // PREVIEW FIX: check both fields — backend sends either 'preview' or 'text'
  const displayText  = source.preview || source.text || "";
  const filename     = source.source_filename || "contract";
  const relevance    = source.relevance_score ?? 0;
  const relevancePct = Math.round(relevance * 100);

  const barColor =
    relevancePct >= 80 ? "bg-green-500" :
    relevancePct >= 50 ? "bg-yellow-400" :
                         "bg-gray-300";

  const hasMore = displayText.length > 150;

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-3
                    hover:border-blue-200 hover:shadow-sm transition-all duration-150">

      {/* Card header */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs font-bold text-gray-400">#{index}</span>
          <span className="bg-blue-50 text-blue-600 text-xs
                           font-semibold px-2 py-0.5 rounded-full">
            Page {source.page_num ?? "?"}
          </span>
          <span className="text-xs text-gray-400 truncate max-w-[90px]"
                title={filename}>
            {filename}
          </span>
        </div>

        {hasMore && (
          <button
            onClick={() => setExpanded(v => !v)}
            className="text-gray-400 hover:text-blue-500 transition-colors shrink-0"
            aria-label={expanded ? "Collapse" : "Expand"}
          >
            {expanded
              ? <ChevronUp   className="h-4 w-4" />
              : <ChevronDown className="h-4 w-4" />}
          </button>
        )}
      </div>

      {/* Relevance bar */}
      <div className="mb-2">
        <div className="flex justify-between text-xs text-gray-400 mb-0.5">
          <span>Relevance</span>
          <span className={
            relevancePct >= 80 ? "text-green-600 font-medium" :
            relevancePct >= 50 ? "text-yellow-600" : "text-gray-400"
          }>
            {relevancePct}%
          </span>
        </div>
        <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-300 ${barColor}`}
            style={{ width: `${relevancePct}%` }}
          />
        </div>
      </div>

      {/* Preview text — FIXED: uses displayText not source.text */}
      <div className={`text-xs text-gray-600 leading-relaxed
                       ${expanded ? "" : "line-clamp-3"}`}>
        {displayText || (
          <span className="text-gray-400 italic">No preview available.</span>
        )}
      </div>

      {/* Footer when expanded */}
      {expanded && (
        <div className="mt-2 pt-2 border-t border-gray-50
                        flex items-center gap-2 text-xs text-gray-400">
          <FileText className="h-3 w-3" />
          <span>Chunk {source.chunk_index ?? "?"}</span>
          <span>·</span>
          <span className="truncate">{filename}</span>
        </div>
      )}
    </div>
  );
});


const EmptyState = () => (
  <div className="flex flex-col items-center justify-center h-48 text-center px-4">
    <BookOpen className="h-8 w-8 text-gray-200 mb-3" />
    <p className="text-sm font-medium text-gray-400">No sources yet</p>
    <p className="text-xs text-gray-300 mt-1 leading-relaxed">
      Ask a question to see the contract clauses used to answer.
    </p>
  </div>
);

export default ClauseHighlight;