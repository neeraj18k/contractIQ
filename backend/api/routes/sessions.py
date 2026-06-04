"""
Sessions routes — chat history and document metadata management.

Routes:
    GET    /api/sessions                      — list all sessions
    GET    /api/sessions/{session_id}         — history + doc info
    GET    /api/sessions/{session_id}/history — message history only
    DELETE /api/sessions/{session_id}         — delete session + ChromaDB chunks
    POST   /api/sessions/{session_id}/clear   — clear history only
"""
import traceback

from fastapi import APIRouter, HTTPException

from models.session_store import session_store
from models.schemas import (
    SessionHistoryResponse,
    SessionListResponse,
    SessionInfo,
    DeleteSessionResponse,
)
from core.chromadb_client import clear_collection

router = APIRouter(prefix="/api", tags=["sessions"])


# ── List all sessions ─────────────────────────────────────────────────────────

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    """
    Return summary of all active sessions.
    Useful for frontend sidebar / session picker.
    """
    try:
        raw = session_store.list_sessions()
        sessions = [
            SessionInfo(
                session_id    = s["session_id"],
                doc_id        = s.get("doc_id"),
                filename      = s.get("filename"),
                message_count = s.get("message_count", 0),
                uploaded_at   = s.get("uploaded_at"),
            )
            for s in raw
        ]
        return SessionListResponse(sessions=sessions, count=len(sessions))

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Could not list sessions: {e}")


# ── Get session detail ────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}", response_model=SessionHistoryResponse)
async def get_session(session_id: str):
    """
    Return chat history + document info for a session.

    Raises 404 if session does not exist.
    """
    if not session_store.session_exists(session_id):
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found.",
        )

    try:
        # get_history() returns list[dict] — matches SessionHistoryResponse
        messages_raw = session_store.get_history(session_id)
        doc          = session_store.get_document(session_id) or {}

        # Build response — include doc metadata as extra fields
        return {
            "session_id": session_id,
            "messages":   messages_raw,
            "count":      len(messages_raw),
            # extra context for frontend (not in schema but FastAPI passes through)
            "doc_id":     doc.get("doc_id"),
            "filename":   doc.get("filename"),
            "uploaded_at": doc.get("uploaded_at"),
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {e}")


# ── History only ──────────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """
    Return only the message history for a session (no doc metadata).
    """
    if not session_store.session_exists(session_id):
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found.",
        )

    try:
        messages_raw = session_store.get_history(session_id)
        return SessionHistoryResponse(
            session_id = session_id,
            messages   = messages_raw,
            count      = len(messages_raw),
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {e}")


# ── Delete session ────────────────────────────────────────────────────────────

@router.delete("/sessions/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(session_id: str):
    """
    Delete a session entirely:
      - Remove chat history from session store
      - Remove document metadata from session store
      - Delete all ChromaDB chunks for this session

    Raises 404 if session does not exist.
    """
    if not session_store.session_exists(session_id):
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found.",
        )

    try:
        # Delete ChromaDB chunks for this session
        deleted_chunks = clear_collection(session_id=session_id)
        print(f"[SESSIONS] Deleted {deleted_chunks} ChromaDB chunks "
              f"for session='{session_id}'")

        # Delete session from store
        session_store.delete_session(session_id)

        return DeleteSessionResponse(
            status     = "deleted",
            session_id = session_id,
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting session: {e}")


# ── Clear history only ────────────────────────────────────────────────────────

@router.post("/sessions/{session_id}/clear")
async def clear_session_history(session_id: str):
    """
    Clear chat message history but keep document metadata and ChromaDB chunks.
    User can continue querying the same document after clearing chat.

    Raises 404 if session does not exist.
    """
    if not session_store.session_exists(session_id):
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found.",
        )

    try:
        session_store.clear_history(session_id)
        return {
            "session_id":    session_id,
            "status":        "cleared",
            "message_count": 0,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error clearing session: {e}")