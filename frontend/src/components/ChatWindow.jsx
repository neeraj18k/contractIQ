/**
 * ChatWindow.jsx — scrollable message list + input bar.
 */
import React, { useEffect, useRef, memo } from 'react';
import { Send, Loader2 }  from 'lucide-react';
import MessageBubble      from './MessageBubble';

const ChatWindow = ({
  messages      = [],
  isStreaming   = false,
  streamedText  = '',
  inputValue    = '',
  inputRef,
  onInputChange,
  onSendMessage,
  onKeyDown,
  historyLoaded = true,
}) => {
  const bottomRef    = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const distFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;
    if (distFromBottom < 120) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages.length, streamedText]);

  const showEmpty = historyLoaded && messages.length === 0 && !isStreaming;

  return (
    <div className="flex flex-col h-full bg-white min-h-0">

      {/* Message list */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto overflow-x-hidden
                   px-4 py-4 space-y-4 scroll-smooth"
      >
        {/* Skeleton */}
        {!historyLoaded && (
          <div className="space-y-3 animate-pulse">
            {[1, 2, 3].map(i => (
              <div key={i} className={`flex ${i % 2 === 0 ? 'justify-end' : ''}`}>
                <div className={`h-10 rounded-2xl bg-gray-100
                  ${i % 2 === 0 ? 'w-48' : 'w-64'}`} />
              </div>
            ))}
          </div>
        )}

        {/* Empty */}
        {showEmpty && (
          <div className="flex flex-col items-center justify-center h-full
                          text-gray-400 select-none pt-20">
            <div className="text-4xl mb-3">📄</div>
            <p className="text-base font-medium text-gray-500">
              Contract loaded — ask anything
            </p>
            <p className="text-sm mt-1">
              e.g. "What are the termination clauses?"
            </p>
          </div>
        )}

        {/* Messages */}
        {historyLoaded && messages.map((msg, idx) => (
          <MessageBubble
            key={`${idx}-${msg.timestamp || idx}`}
            role={msg.role}
            content={msg.content}
            timestamp={msg.timestamp}
          />
        ))}

        {/* Live streaming */}
        {isStreaming && (
          <MessageBubble
            role="assistant"
            content={streamedText}
            isStreaming
          />
        )}

        {/* Thinking indicator */}
        {isStreaming && !streamedText && (
          <div className="flex items-center gap-2 text-gray-400 text-sm pl-1">
            <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
            <span>Analyzing contract…</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="border-t border-gray-100 bg-white px-4 py-3 shrink-0">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={e => onInputChange(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask a question about the contract…"
            disabled={isStreaming}
            rows={1}
            className="flex-1 resize-none px-4 py-2.5 border border-gray-200
                       rounded-xl text-sm focus:outline-none focus:ring-2
                       focus:ring-blue-500 focus:border-transparent
                       disabled:bg-gray-50 disabled:text-gray-400
                       placeholder:text-gray-300 max-h-32 overflow-y-auto
                       leading-relaxed"
            style={{ minHeight: '42px' }}
          />
          <button
            onClick={onSendMessage}
            disabled={isStreaming || !inputValue.trim()}
            className="flex items-center justify-center w-10 h-10 rounded-xl
                       shrink-0 bg-blue-600 hover:bg-blue-700
                       disabled:bg-gray-200 disabled:cursor-not-allowed
                       transition-colors"
            aria-label="Send"
          >
            {isStreaming
              ? <Loader2 className="h-4 w-4 text-white animate-spin" />
              : <Send    className="h-4 w-4 text-white" />
            }
          </button>
        </div>
        <p className="text-xs text-gray-300 mt-1.5 pl-1">
          Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

export default memo(ChatWindow);