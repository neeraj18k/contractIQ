"""
In-memory session store for chat history and document metadata.
"""
from datetime import datetime
from typing import Optional
from models.schemas import SessionMessage


class SessionStore:
    """
    Thread-safe* in-memory store for:
      - Chat message history   (session_id → [SessionMessage])
      - Document metadata      (session_id → {doc_id, filename, ...})

    *Single-process only. For multi-worker deployments, swap with Redis.
    """

    def __init__(self):
        # chat history
        self._messages:  dict[str, list[SessionMessage]] = {}
        # document info per session
        self._documents: dict[str, dict]                 = {}

    # ── Message history ───────────────────────────────────────────────────────

    def add_message(
        self,
        session_id: str,
        role:       str,
        content:    str,
    ) -> None:
        """
        Append a message to the session history.

        Args:
            session_id : unique session identifier
            role       : "user" or "assistant"
            content    : message text
        """
        if not content or not content.strip():
            return                              # never store empty messages

        if session_id not in self._messages:
            self._messages[session_id] = []

        self._messages[session_id].append(
            SessionMessage(
                role=role,
                content=content.strip(),
                timestamp=datetime.now(),
            )
        )

    def get_history(
        self,
        session_id: str,
        limit:      int = 20,
    ) -> list[dict]:
        """
        Return last `limit` messages as plain dicts.

        Returns:
            [{"role": str, "content": str, "timestamp": str}, ...]

        Note: Returns dicts (not SessionMessage objects) so analyzer can
        build LangChain message objects directly without extra conversion.
        """
        messages = self._messages.get(session_id, [])
        recent   = messages[-limit:] if len(messages) > limit else messages
        return [_message_to_dict(m) for m in recent]

    def get_message_count(self, session_id: str) -> int:
        """Return total number of messages stored for a session."""
        return len(self._messages.get(session_id, []))

    def clear_history(self, session_id: str) -> None:
        """Wipe message history but keep document metadata."""
        if session_id in self._messages:
            self._messages[session_id] = []

    # ── Document metadata ─────────────────────────────────────────────────────

    def set_document(
        self,
        session_id: str,
        doc_id:     str,
        filename:   str,
        metadata:   Optional[dict] = None,
    ) -> None:
        """
        Associate a processed document with a session.
        Called by upload route after successful graph invocation.
        """
        self._documents[session_id] = {
            "doc_id":     doc_id,
            "filename":   filename,
            "uploaded_at": datetime.now().isoformat(),
            **(metadata or {}),
        }

    def get_document(self, session_id: str) -> Optional[dict]:
        """
        Return document metadata for session, or None if not uploaded yet.
        """
        return self._documents.get(session_id)

    def get_doc_id(self, session_id: str) -> Optional[str]:
        """Convenience — return just the doc_id for a session."""
        doc = self._documents.get(session_id)
        return doc["doc_id"] if doc else None

    # ── Session lifecycle ─────────────────────────────────────────────────────

    def delete_session(self, session_id: str) -> None:
        """Remove all data for a session (history + document metadata)."""
        self._messages.pop(session_id, None)
        self._documents.pop(session_id, None)

    def session_exists(self, session_id: str) -> bool:
        """True if session has any history or document attached."""
        return (
            session_id in self._messages or
            session_id in self._documents
        )

    def list_sessions(self) -> list[dict]:
        """
        Return summary of all active sessions — useful for /sessions API route.
        """
        all_ids = set(self._messages) | set(self._documents)
        result  = []
        for sid in all_ids:
            doc = self._documents.get(sid, {})
            result.append({
                "session_id":    sid,
                "message_count": len(self._messages.get(sid, [])),
                "doc_id":        doc.get("doc_id"),
                "filename":      doc.get("filename"),
                "uploaded_at":   doc.get("uploaded_at"),
            })
        return sorted(result, key=lambda s: s["uploaded_at"] or "", reverse=True)

    # ── Legacy compat ─────────────────────────────────────────────────────────

    def clear_session(self, session_id: str) -> None:
        """Alias for clear_history — kept for backward compatibility."""
        self.clear_history(session_id)

    def format_history_for_context(self, session_id: str) -> str:
        """
        Legacy string formatter — kept so old callers don't break.
        Analyzer now uses get_history() + LangChain message objects instead.
        """
        messages = self.get_history(session_id)
        lines    = [f"{m['role'].upper()}: {m['content']}" for m in messages]
        return "\n\n".join(lines)


# ── Helper ────────────────────────────────────────────────────────────────────

def _message_to_dict(msg: SessionMessage) -> dict:
    return {
        "role":      msg.role,
        "content":   msg.content,
        "timestamp": msg.timestamp.isoformat() if msg.timestamp else "",
    }


# ── Global singleton ──────────────────────────────────────────────────────────
session_store = SessionStore()