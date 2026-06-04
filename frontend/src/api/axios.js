/**
 * axios.js — ContractIQ API client
 *
 * SSE streaming: fetch + ReadableStream (axios stream browser mein kaam nahi karta)
 * Regular calls: axios
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api`;

// ── Axios instance (non-streaming calls) ──────────────────────────────────────
import axios from 'axios';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// ── Request interceptor — debug logging ───────────────────────────────────────
apiClient.interceptors.request.use((config) => {
  console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// ── Response interceptor — unified error shape ────────────────────────────────
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      'Unknown error';
    console.error(`[API] Error: ${detail}`);
    return Promise.reject(new Error(detail));
  }
);


// ── Upload ────────────────────────────────────────────────────────────────────

/**
 * Upload a PDF contract.
 *
 * @param {File} file
 * @param {(pct: number) => void} [onProgress]  0-100 upload progress callback
 * @returns {Promise<{ doc_id, session_id, filename, chunk_count, page_count, status, message }>}
 */
export const uploadFile = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const res = await apiClient.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress
      ? (e) => {
          const pct = e.total ? Math.round((e.loaded / e.total) * 100) : 0;
          onProgress(pct);
        }
      : undefined,
  });

  return res.data;   // { doc_id, session_id, chunk_count, page_count, ... }
};


// ── Query — SSE streaming ─────────────────────────────────────────────────────

/**
 * Stream a contract query using fetch + ReadableStream.
 * axios responseType:'stream' does NOT work in browsers — use fetch instead.
 *
 * @param {string}   query
 * @param {string}   sessionId
 * @param {string}   [docId]        optional — server resolves from session if omitted
 * @param {object}   callbacks
 * @param {(token: string) => void}         callbacks.onToken    — called per word
 * @param {(sources: object[]) => void}     callbacks.onSources  — called with final sources array
 * @param {(err: Error) => void}            callbacks.onError
 * @param {() => void}                      callbacks.onDone
 * @returns {Promise<void>}
 */
export const queryContractStream = async (
  query,
  sessionId,
  docId,
  { onToken, onSources, onError, onDone } = {}
) => {
  try {
    const res = await fetch(`${API_BASE}/query`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        query,
        session_id: sessionId,
        doc_id:     docId || undefined,   // omit if empty — server resolves
      }),
    });

    if (!res.ok) {
      // Parse FastAPI error detail
      let detail = `HTTP ${res.status}`;
      try {
        const errBody = await res.json();
        detail = errBody.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }

    if (!res.body) {
      throw new Error('No response body — SSE stream unavailable.');
    }

    // ── Read SSE stream ────────────────────────────────────────────────────
    const reader  = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let   buffer  = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // SSE events are separated by \n\n
      const events = buffer.split('\n\n');
      buffer = events.pop();           // keep incomplete last chunk

      for (const event of events) {
        if (!event.startsWith('data: ')) continue;
        const payload = event.slice(6);   // strip "data: "

        if (payload === '') continue;;

        // ── __DONE__ sentinel ────────────────────────────────────────────
        if (payload === '__DONE__') {
          onDone?.();
          continue;
        }

        // ── JSON event (sources or warning) ──────────────────────────────
        if (payload.startsWith('{')) {
          try {
            const parsed = JSON.parse(payload);

            if (parsed.sources !== undefined) {
              onSources?.(parsed.sources);
            }
            if (parsed.warning) {
              console.warn('[STREAM] Server warning:', parsed.warning);
            }
            if (parsed.error) {
              onError?.(new Error(parsed.error));
            }
          } catch (_) {
            // Not valid JSON — treat as text token
            onToken?.(payload);
          }
          continue;
        }

        // ── Text token ────────────────────────────────────────────────────
        onToken?.(payload);
      }
    }
  } catch (err) {
    console.error('[API] Stream error:', err);
    onError?.(err instanceof Error ? err : new Error(String(err)));
  }
};


// ── Session management ────────────────────────────────────────────────────────

/** List all sessions */
export const listSessions = async () => {
  const res = await apiClient.get('/sessions');
  return res.data;   // { sessions: [...], count: N }
};

/** Get session history + doc metadata */
export const getSessionHistory = async (sessionId) => {
  const res = await apiClient.get(`/sessions/${sessionId}`);
  return res.data;
};

/** Clear chat history (keep document + ChromaDB chunks) */
export const clearSession = async (sessionId) => {
  const res = await apiClient.post(`/sessions/${sessionId}/clear`);
  return res.data;
};

/** Delete session + ChromaDB chunks entirely */
export const deleteSession = async (sessionId) => {
  const res = await apiClient.delete(`/sessions/${sessionId}`);
  return res.data;
};


// ── Health ────────────────────────────────────────────────────────────────────

export const healthCheck = async () => {
  const res = await apiClient.get('/health');
  return res.data;   // { status, chroma_ok, gemini_ok, session_count }
};


export default apiClient;