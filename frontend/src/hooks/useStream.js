/**
 * useStream.js — SSE streaming hook for ContractIQ query responses.
 *
 * Parses backend SSE format:
 *   data: <word>        → text token
 *   data: __DONE__      → text stream complete
 *   data: {"sources":[]} → sources JSON
 *   data: {"warning":""}  → soft warning
 *   data: {"error":""}    → hard error
 */
import { useState, useCallback, useRef } from 'react';
import { queryContractStream } from '../api/axios';

export const useStream = () => {
  const [streamedText, setStreamedText]   = useState('');
  const [sources,      setSources]        = useState([]);
  const [isStreaming,  setIsStreaming]     = useState(false);
  const [isDone,       setIsDone]         = useState(false);
  const [error,        setError]          = useState(null);

  // Ref holds accumulated text so callbacks always see latest value
  const accumulatedRef = useRef('');

  /**
   * Send a query and stream the response.
   *
   * @param {string} query
   * @param {string} sessionId
   * @param {string} [docId]   — optional, server resolves from session
   * @returns {Promise<string>} final complete response text
   */
  const sendQuery = useCallback(async (query, sessionId, docId) => {
    // ── Reset state ──────────────────────────────────────────────────────────
    setStreamedText('');
    setSources([]);
    setError(null);
    setIsDone(false);
    setIsStreaming(true);
    accumulatedRef.current = '';

    return new Promise((resolve) => {
      queryContractStream(query, sessionId, docId, {

        // ── Token received ───────────────────────────────────────────────────
        onToken: (token) => {
          accumulatedRef.current += token;
          setStreamedText(accumulatedRef.current);
        },

        // ── Sources received (after __DONE__) ────────────────────────────────
        onSources: (sourcesArray) => {
          setSources(sourcesArray || []);
        },

        // ── Stream complete ───────────────────────────────────────────────────
        onDone: () => {
          setIsStreaming(false);
          setIsDone(true);
          resolve(accumulatedRef.current);
        },

        // ── Error ─────────────────────────────────────────────────────────────
        onError: (err) => {
          console.error('[useStream] Stream error:', err);
          setError(err.message || 'Streaming failed.');
          setIsStreaming(false);
          setIsDone(true);
          resolve(accumulatedRef.current);  // resolve with whatever we got
        },
      });
    });
  }, []);

  /**
   * Reset all stream state — call before starting a new session.
   */
  const resetStream = useCallback(() => {
    setStreamedText('');
    setSources([]);
    setError(null);
    setIsDone(false);
    setIsStreaming(false);
    accumulatedRef.current = '';
  }, []);

  return {
    streamedText,   // accumulated response text (updates live)
    sources,        // final sources array (set after __DONE__)
    isStreaming,    // true while tokens are arriving
    isDone,         // true after __DONE__ received
    error,          // error message string or null
    sendQuery,      // (query, sessionId, docId?) => Promise<string>
    resetStream,    // () => void
  };
};