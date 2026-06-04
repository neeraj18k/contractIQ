import os
import traceback

from utils.pdf_parser import extract_text_from_pdf, validate_pdf, get_pdf_metadata
from utils.chunker import split_documents
from core.config import MIN_CHUNK_LENGTH


def ingest_contract(state: dict) -> dict:
    """
    LangGraph node: PDF → pages → chunks.

    Expects state keys:
        file_path  (str)  : absolute path to uploaded PDF
        doc_id     (str)  : unique document / session identifier
        filename   (str)  : original filename for metadata

    Returns state with added keys:
        chunks       (list[dict]) : [{text, metadata}, ...]
        chunk_count  (int)
        page_count   (int)
        pdf_metadata (dict)
        error        (str | None)
    """
    file_path = state.get("file_path", "")
    doc_id    = state.get("doc_id", "")
    filename  = state.get("filename", "unknown.pdf")

    print(f"[INGESTOR] Starting — file='{filename}' doc_id='{doc_id}'")

    # ── 1. Input validation ───────────────────────────────────────────────────
    if not file_path:
        return _error(state, "No file_path provided in state.")

    if not doc_id:
        return _error(state, "No doc_id provided in state.")

    if not os.path.exists(file_path):
        return _error(state, f"File not found on disk: '{file_path}'")

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > 50:
        return _error(state, f"File too large ({file_size_mb:.1f} MB). Limit is 50 MB.")

    if not validate_pdf(file_path):
        return _error(state, f"File '{filename}' is not a valid / readable PDF.")

    # ── 2. PDF metadata (non-fatal) ───────────────────────────────────────────
    pdf_metadata = {}
    try:
        pdf_metadata = get_pdf_metadata(file_path)
        print(
            f"[INGESTOR] PDF info — pages={pdf_metadata.get('page_count', '?')} "
            f"size={pdf_metadata.get('file_size_kb', '?')} KB "
            f"title='{pdf_metadata.get('title', '')}'"
        )
    except Exception:
        print("[INGESTOR] Warning: could not read PDF metadata (non-fatal).")

    # ── 3. Text extraction ────────────────────────────────────────────────────
    try:
        pages_data = extract_text_from_pdf(file_path)
    except FileNotFoundError as e:
        return _error(state, str(e))
    except ValueError as e:
        # "No extractable text" — scanned PDF
        return _error(state, str(e))
    except RuntimeError as e:
        traceback.print_exc()
        return _error(state, str(e))

    page_count = len(pages_data)
    print(f"[INGESTOR] Extracted {page_count} non-empty pages.")

    if page_count == 0:
        return _error(state, "PDF parsed but all pages were empty — possible scanned PDF.")

    # Debug: show first 200 chars of page 1
    if pages_data:
        preview = pages_data[0]["text"][:200].replace("\n", " ")
        print(f"[INGESTOR] Page 1 preview: '{preview}'")

    # ── 4. Chunking ───────────────────────────────────────────────────────────
    try:
        chunks = split_documents(pages_data, doc_id, filename)
    except Exception as e:
        traceback.print_exc()
        return _error(state, f"Chunking failed: {e}")

    chunk_count = len(chunks)
    print(f"[INGESTOR] Chunks created={chunk_count}")

    if chunk_count == 0:
        return _error(
            state,
            f"Chunking produced 0 chunks. "
            f"Check MIN_CHUNK_LENGTH={MIN_CHUNK_LENGTH} and PDF text quality. "
            f"Pages extracted={page_count}.",
        )

    # Debug: show first chunk
    first_chunk = chunks[0]["text"][:200].replace("\n", " ")
    print(f"[INGESTOR] First chunk preview: '{first_chunk}'")

    # ── 5. Success ────────────────────────────────────────────────────────────
    return {
        **state,
        "chunks":       chunks,
        "chunk_count":  chunk_count,
        "page_count":   page_count,
        "pdf_metadata": pdf_metadata,
        "error":        None,
    }


# ── Helper ────────────────────────────────────────────────────────────────────

def _error(state: dict, message: str) -> dict:
    """Return a consistent error state dict."""
    print(f"[INGESTOR] ✗ Error: {message}")
    return {
        **state,
        "chunks":       [],
        "chunk_count":  0,
        "page_count":   state.get("page_count", 0),
        "pdf_metadata": state.get("pdf_metadata", {}),
        "error":        message,
    }