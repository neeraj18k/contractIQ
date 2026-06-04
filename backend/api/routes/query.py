"""
POST /api/query  — RAG query over uploaded contract with SSE streaming.
"""
import json
import re
import traceback
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from agents.contract_agent import invoke_query_graph
from models.schemas        import QueryRequest, SourceRef
from models.session_store  import session_store

router = APIRouter(prefix="/api", tags=["query"])


@router.post("/query")
async def query_contract(request: QueryRequest):
    session_id = request.session_id.strip() if request.session_id else ""

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    doc_id = (request.doc_id or "").strip()
    if not doc_id:
        doc_id = session_store.get_doc_id(session_id) or ""

    if not doc_id:
        raise HTTPException(
            status_code=404,
            detail=f"No document found for session '{session_id}'. Please upload a contract first.",
        )

    if not session_store.get_document(session_id):
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' has no uploaded document.",
        )

    print(f"[QUERY] session='{session_id}' doc_id='{doc_id}' query='{request.query[:80]}'")

    try:
        result = invoke_query_graph(
            query      = request.query,
            doc_id     = doc_id,
            session_id = session_id,
            n_results  = request.n_results,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Query pipeline error: {e}")

    print(f"[QUERY] Graph done — error={result.get('error')} "
          f"response_len={len(result.get('final_response', ''))}")

    if result.get("error") and not result.get("final_response", "").strip():
        raise HTTPException(status_code=400, detail=f"Query failed: {result['error']}")

    return StreamingResponse(
        _sse_stream(result),
        media_type="text/event-stream",
        headers={
            "Cache-Control":      "no-cache",
            "X-Accel-Buffering":  "no",
            "Connection":         "keep-alive",
        },
    )


async def _sse_stream(result: dict) -> AsyncGenerator[str, None]:
    final_response = result.get("final_response", "")
    sources        = result.get("sources", [])
    error          = result.get("error")

    if error:
        yield _sse_event(json.dumps({"warning": error}))

    if final_response:
        # ── SPACING FIX ───────────────────────────────────────────────────────
        # split(" ") breaks on \n — words merge across lines.
        # re.split(r'(\s+)') keeps whitespace tokens too → spaces preserved.
        tokens = re.split(r'(\s+)', final_response)
        for token in tokens:
            if token:                   # skip empty strings from split
                yield _sse_event(token)
    else:
        yield _sse_event("No response generated.")

    yield _sse_event("__DONE__")

    sources_payload = _build_sources_payload(sources, result.get("session_id", ""))
    yield _sse_event(json.dumps(sources_payload))


def _sse_event(data: str) -> str:
    return f"data: {data}\n\n"


def _build_sources_payload(sources: list[dict], session_id: str) -> dict:
    serialized = []
    for s in sources:
        serialized.append({
            "page_num":        s.get("page_num"),
            "chunk_index":     s.get("chunk_index"),
            "source_filename": s.get("source_filename", ""),
            # send BOTH preview and text — frontend handles either
            "preview":         s.get("preview", s.get("text", "")),
            "relevance_score": round(s.get("relevance_score", 0), 4),
        })
    return {"sources": serialized, "session_id": session_id}


@router.get("/query/test")
async def test_query():
    return {"status": "ok", "message": "Query route is working."}