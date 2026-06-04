/**
 * MessageBubble.jsx — single chat message with markdown + streaming cursor.
 */
import React, { memo }       from 'react';
import ReactMarkdown          from 'react-markdown';
import remarkGfm              from 'remark-gfm';
import { formatDistanceToNow } from 'date-fns';
import { User, Bot }          from 'lucide-react';

const MessageBubble = ({ role, content = '', timestamp, isStreaming = false }) => {
  const isUser = role === 'user';

  return (
    <div className={`flex items-end gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}>

      {/* Avatar — assistant */}
      {!isUser && (
        <div className="shrink-0 w-7 h-7 rounded-full bg-blue-100
                        flex items-center justify-center mb-0.5">
          <Bot className="h-4 w-4 text-blue-600" />
        </div>
      )}

      {/* Bubble */}
      <div className={`
        relative max-w-sm lg:max-w-2xl px-4 py-3 rounded-2xl text-sm
        leading-relaxed shadow-sm
        overflow-x-hidden break-words word-break
        ${isUser
          ? 'bg-blue-600 text-white rounded-br-sm'
          : 'bg-gray-50 border border-gray-100 text-gray-800 rounded-bl-sm'
        }
      `}>

        {isUser ? (
          <p className="whitespace-pre-wrap break-words">{content}</p>
        ) : (
          <div className="
            prose prose-sm max-w-none break-words
            prose-p:my-1 prose-p:leading-relaxed
            prose-headings:font-semibold prose-headings:my-2
            prose-ul:my-1 prose-ul:pl-4
            prose-ol:my-1 prose-ol:pl-4
            prose-li:my-0.5
            prose-strong:font-semibold prose-strong:text-gray-900
            prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5
            prose-code:rounded prose-code:text-xs prose-code:font-mono
            prose-pre:bg-gray-900 prose-pre:text-gray-100
            prose-pre:rounded-lg prose-pre:text-xs prose-pre:overflow-x-auto
            prose-blockquote:border-l-blue-400 prose-blockquote:text-gray-600
            prose-a:text-blue-600 prose-a:underline
            prose-hr:border-gray-200
          ">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content || ' '}
            </ReactMarkdown>
            {isStreaming && (
              <span className="inline-block w-0.5 h-4 bg-blue-500
                               animate-pulse ml-0.5 align-middle" />
            )}
          </div>
        )}

        {timestamp && !isStreaming && (
          <p className={`text-xs mt-1.5 select-none
            ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
            {_formatTime(timestamp)}
          </p>
        )}
      </div>

      {/* Avatar — user */}
      {isUser && (
        <div className="shrink-0 w-7 h-7 rounded-full bg-blue-600
                        flex items-center justify-center mb-0.5">
          <User className="h-4 w-4 text-white" />
        </div>
      )}
    </div>
  );
};

function _formatTime(ts) {
  try { return formatDistanceToNow(new Date(ts), { addSuffix: true }); }
  catch { return ''; }
}

export default memo(MessageBubble);