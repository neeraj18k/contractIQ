/**
 * App.jsx — root component with global session state.
 *
 * Keeps session/doc info at top level so Home (upload) and Chat (query)
 * share the same session without prop-drilling through React Router.
 */
import React, { useState, useCallback } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';

import Home from './pages/Home';
import Chat from './pages/Chat';

function App() {
  // ── Global session state ───────────────────────────────────────────────────
  // Set by Home (upload success) → consumed by Chat (query calls)
  const [session, setSession] = useState(null);
  // Shape: { sessionId, docId, filename, chunkCount, pageCount }

  /**
   * Called by UploadZone / Home after successful upload.
   * Navigating to /chat happens inside Home — App just stores the data.
   */
  const handleUploadSuccess = useCallback((uploadData) => {
    setSession({
      sessionId:  uploadData.session_id,
      docId:      uploadData.doc_id,
      filename:   uploadData.filename,
      chunkCount: uploadData.chunk_count,
      pageCount:  uploadData.page_count,
    });
  }, []);

  /**
   * Called by Chat Sidebar when user picks a different session,
   * or when a session is deleted.
   */
  const handleSessionChange = useCallback((newSession) => {
    setSession(newSession);
  }, []);

  /** Clear session — used on logout / new upload */
  const handleSessionClear = useCallback(() => {
    setSession(null);
  }, []);

  // ── Routes ─────────────────────────────────────────────────────────────────
  return (
    <Router>
      <Routes>
        {/* Home — upload page */}
        <Route
          path="/"
          element={
            <Home
              onUploadSuccess={handleUploadSuccess}
              currentSession={session}
            />
          }
        />

        {/* Chat — query page, redirect to / if no session */}
        <Route
          path="/chat"
          element={
            session ? (
              <Chat
                session={session}
                onSessionChange={handleSessionChange}
                onSessionClear={handleSessionClear}
              />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;