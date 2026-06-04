"""
LangGraph contract agent — UPLOAD_GRAPH and QUERY_GRAPH.
Thread-safe, typed, with proper error routing.
"""
import uuid
import traceback
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents.nodes.ingestor   import ingest_contract
from agents.nodes.embedder   import embed_and_store
from agents.nodes.retriever  import retrieve_relevant_chunks
from agents.nodes.analyzer   import analyze_contract
from agents.nodes.summarizer import summarize_response
from core.config             import DEFAULT_THREAD_ID


# ── State schemas ─────────────────────────────────────────────────────────────

class UploadState(TypedDict, total=False):
    # inputs
    file_path:    str
    doc_id:       str
    filename:     str
    # ingestor outputs
    chunks:       list
    chunk_count:  int
    page_count:   int
    pdf_metadata: dict
    # embedder outputs
    embedded:     bool
    # shared
    error:        Optional[str]


class QueryState(TypedDict, total=False):
    # inputs
    query:            str
    doc_id:           str
    session_id:       str
    n_results:        int           # optional — retriever uses this
    # retriever outputs
    retrieved_chunks: list
    # analyzer outputs
    analysis:         str
    sources:          list
    # summarizer outputs
    final_response:   str
    # shared
    error:            Optional[str]


# ── Routing helpers ───────────────────────────────────────────────────────────

def _route_after_ingestor(state: UploadState) -> str:
    """Go to embedder only if ingestor succeeded with real chunks."""
    if state.get("error"):
        return "error"
    if not state.get("chunks"):
        return "error"
    return "embedder"


def _route_after_retriever(state: QueryState) -> str:
    """Go to analyzer only if retrieval succeeded with results."""
    if state.get("error"):
        return "error"
    if not state.get("retrieved_chunks"):
        return "error"
    return "analyzer"


def _route_after_analyzer(state: QueryState) -> str:
    """Go to summarizer even on soft errors — summarizer handles fallback."""
    return "summarizer"


def _error_node(state: dict) -> dict:
    """
    Terminal error node — ensures final_response is always set
    so API routes never get a KeyError.
    """
    error_msg = state.get("error", "An unknown error occurred.")
    print(f"[AGENT:error_node] {error_msg}")
    return {
        **state,
        "final_response": (
            f"⚠ Processing failed: {error_msg}\n\n"
            "Please try re-uploading the document or rephrasing your query."
        ),
    }


# ── Graph factories ───────────────────────────────────────────────────────────

def _create_upload_graph() -> StateGraph:
    g = StateGraph(UploadState)

    g.add_node("ingestor", ingest_contract)
    g.add_node("embedder", embed_and_store)
    g.add_node("error",    _error_node)

    g.add_edge(START, "ingestor")
    g.add_conditional_edges("ingestor", _route_after_ingestor,
                            {"embedder": "embedder", "error": "error"})
    g.add_edge("embedder", END)
    g.add_edge("error",    END)

    return g.compile(checkpointer=MemorySaver())


def _create_query_graph() -> StateGraph:
    g = StateGraph(QueryState)

    g.add_node("retriever", retrieve_relevant_chunks)
    g.add_node("analyzer",  analyze_contract)
    g.add_node("summarizer", summarize_response)
    g.add_node("error",      _error_node)

    g.add_edge(START, "retriever")
    g.add_conditional_edges("retriever", _route_after_retriever,
                            {"analyzer": "analyzer", "error": "error"})
    g.add_conditional_edges("analyzer",  _route_after_analyzer,
                            {"summarizer": "summarizer"})
    g.add_edge("summarizer", END)
    g.add_edge("error",      END)

    return g.compile(checkpointer=MemorySaver())


# ── Singleton graphs (module-level, created once) ─────────────────────────────
upload_graph = _create_upload_graph()
query_graph  = _create_query_graph()


# ── Public invoke functions ───────────────────────────────────────────────────

def invoke_upload_graph(
    file_path: str,
    doc_id:    str,
    filename:  str,
) -> dict:
    """
    Run the upload pipeline: ingest → embed.

    Args:
        file_path : absolute path to the uploaded PDF
        doc_id    : unique document ID (used as ChromaDB session_id)
        filename  : original filename for metadata

    Returns:
        Final LangGraph state dict.
    """
    initial_state: UploadState = {
        "file_path":    file_path,
        "doc_id":       doc_id,
        "filename":     filename,
        "chunks":       [],
        "chunk_count":  0,
        "page_count":   0,
        "pdf_metadata": {},
        "embedded":     False,
        "error":        None,
    }

    # Each upload gets its own thread — no state bleed between uploads
    thread_id = f"upload-{doc_id}-{uuid.uuid4().hex[:8]}"
    config    = {"configurable": {"thread_id": thread_id}}

    print(f"[AGENT] invoke_upload_graph thread_id='{thread_id}'")
    try:
        return upload_graph.invoke(initial_state, config=config)
    except Exception as e:
        traceback.print_exc()
        return {**initial_state, "error": str(e)}


def invoke_query_graph(
    query:      str,
    doc_id:     str,
    session_id: str,
    n_results:  int = 5,
) -> dict:
    """
    Run the query pipeline: retrieve → analyze → summarize.

    Args:
        query      : user's natural language question
        doc_id     : document ID to scope ChromaDB search
        session_id : session ID (used as LangGraph thread_id for memory)
        n_results  : number of chunks to retrieve (default 5)

    Returns:
        Final LangGraph state dict with 'final_response' and 'sources'.
    """
    initial_state: QueryState = {
        "query":            query,
        "doc_id":           doc_id,
        "session_id":       session_id,
        "n_results":        n_results,
        "retrieved_chunks": [],
        "analysis":         "",
        "sources":          [],
        "final_response":   "",
        "error":            None,
    }

    # session_id as thread_id = LangGraph memory persists across turns
    # This is the LangGraph thread_id config fix
    config = {"configurable": {"thread_id": session_id or DEFAULT_THREAD_ID}}

    print(f"[AGENT] invoke_query_graph thread_id='{session_id}' query='{query[:60]}'")
    try:
        return query_graph.invoke(initial_state, config=config)
    except Exception as e:
        traceback.print_exc()
        return {**initial_state, "error": str(e), "final_response": f"Agent error: {e}"}