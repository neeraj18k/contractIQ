"""
Pydantic v2 schemas for ContractIQ API request/response models.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Shared / internal ─────────────────────────────────────────────────────────

class SessionMessage(BaseModel):
    """Single chat message — stored in SessionStore."""
    role:      str               # "user" | "assistant"
    content:   str
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("user", "assistant"):
            raise ValueError(f"role must be 'user' or 'assistant', got '{v}'")
        return v


# ── Upload ────────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    """
    Returned after successful PDF upload + embedding.
    Matches invoke_upload_graph() state keys.
    """
    doc_id:      str
    session_id:  str
    filename:    str
    chunk_count: int
    page_count:  int  = 0
    status:      str  = "success"
    message:     str  = ""


class UploadErrorResponse(BaseModel):
    """Returned when upload pipeline fails."""
    status:  str = "error"
    message: str
    doc_id:  Optional[str] = None


# ── Query ─────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    """
    POST /query request body.
    doc_id is optional — server resolves it from session_id if omitted.
    """
    query:      str            = Field(..., min_length=1, max_length=2000)
    session_id: str            = Field(..., min_length=1)
    doc_id:     Optional[str]  = None    # resolved from session_store if missing
    n_results:  int            = Field(default=5, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query cannot be blank")
        return v.strip()


class SourceRef(BaseModel):
    """
    One cited source chunk — returned in QueryResponse.
    Matches keys set by analyzer node + summarizer node.
    """
    page_num:         Optional[int]   = None
    chunk_index:      Optional[int]   = None
    source_filename:  str             = ""
    preview:          str             = ""     # first ~120 chars of chunk text
    relevance_score:  float           = 0.0


class QueryResponse(BaseModel):
    """POST /query response."""
    answer:     str
    sources:    list[SourceRef] = []
    session_id: str
    doc_id:     Optional[str]   = None


# ── Session ───────────────────────────────────────────────────────────────────

class SessionInfo(BaseModel):
    """One entry in GET /sessions response."""
    session_id:    str
    doc_id:        Optional[str] = None
    filename:      Optional[str] = None
    message_count: int           = 0
    uploaded_at:   Optional[str] = None


class SessionListResponse(BaseModel):
    """GET /sessions response."""
    sessions: list[SessionInfo] = []
    count:    int               = 0


class SessionHistoryResponse(BaseModel):
    """GET /sessions/{session_id}/history response."""
    session_id: str
    messages:   list[SessionMessage] = []
    count:      int                  = 0


class DeleteSessionResponse(BaseModel):
    """DELETE /sessions/{session_id} response."""
    status:     str = "deleted"
    session_id: str


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """GET /health response."""
    status:       str = "ok"
    chroma_ok:    bool
    gemini_ok:    bool
    session_count: int = 0