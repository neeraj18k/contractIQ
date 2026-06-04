"""
POST /api/upload  — receive PDF, run ingest+embed pipeline, register session.
"""
import os
import traceback
import tempfile
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from agents.contract_agent import invoke_upload_graph
from models.schemas        import UploadResponse, UploadErrorResponse
from models.session_store  import session_store
from utils.pdf_parser      import validate_pdf

router = APIRouter(prefix="/api", tags=["upload"])

# Temp dir for uploaded files (deleted after processing)
_UPLOAD_DIR  = tempfile.gettempdir()
_MAX_SIZE_MB = 50


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={400: {"model": UploadErrorResponse}, 500: {"model": UploadErrorResponse}},
)
async def upload_contract(file: UploadFile = File(...)):
    """
    Upload a PDF contract and run the ingest + embed pipeline.

    Returns:
        UploadResponse with doc_id, session_id, chunk_count, page_count.
        Frontend must store session_id for subsequent /query calls.
    """
    file_path: str | None = None

    try:
        # ── 1. Basic validation ───────────────────────────────────────────────
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided.")

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files are supported. Got: '{file.filename}'",
            )

        # ── 2. Read + size check ──────────────────────────────────────────────
        content = await file.read()
        size_mb = len(content) / (1024 * 1024)

        print(f"[UPLOAD] file='{file.filename}' size={size_mb:.2f} MB")

        if size_mb > _MAX_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large ({size_mb:.1f} MB). Limit is {_MAX_SIZE_MB} MB.",
            )

        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # ── 3. Save to temp dir ───────────────────────────────────────────────
        doc_id    = str(uuid4())
        safe_name = file.filename.replace(" ", "_")
        file_path = os.path.join(_UPLOAD_DIR, f"{doc_id}_{safe_name}")

        with open(file_path, "wb") as f:
            f.write(content)

        # ── 4. Validate PDF structure ─────────────────────────────────────────
        if not validate_pdf(file_path):
            raise HTTPException(
                status_code=400,
                detail="File is not a valid or readable PDF. It may be corrupted.",
            )

        # ── 5. Run ingest + embed pipeline ────────────────────────────────────
        print(f"[UPLOAD] Invoking upload graph doc_id='{doc_id}'...")
        result = invoke_upload_graph(file_path, doc_id, file.filename)
        print(f"[UPLOAD] Graph done — "
              f"chunks={result.get('chunk_count', 0)} "
              f"pages={result.get('page_count', 0)} "
              f"error={result.get('error')}")

        if result.get("error"):
            raise HTTPException(
                status_code=422,
                detail=f"Processing failed: {result['error']}",
            )

        chunk_count = result.get("chunk_count", 0)
        page_count  = result.get("page_count",  0)

        if chunk_count == 0:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Document was parsed but produced no text chunks. "
                    "The PDF may be image-only or have no extractable text."
                ),
            )

        # ── 6. Register session ───────────────────────────────────────────────
        # session_id == doc_id for simplicity
        # Frontend uses this for all subsequent /query calls
        session_id = doc_id
        session_store.set_document(
            session_id = session_id,
            doc_id     = doc_id,
            filename   = file.filename,
            metadata   = {
                "page_count":  page_count,
                "chunk_count": chunk_count,
                **result.get("pdf_metadata", {}),
            },
        )
        print(f"[UPLOAD] Session registered session_id='{session_id}'")

        # ── 7. Return response ────────────────────────────────────────────────
        return UploadResponse(
            doc_id      = doc_id,
            session_id  = session_id,
            filename    = file.filename,
            chunk_count = chunk_count,
            page_count  = page_count,
            status      = "ready",
            message     = (
                f"Successfully processed {page_count} pages "
                f"into {chunk_count} searchable chunks."
            ),
        )

    except HTTPException:
        raise

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected upload error: {str(e)}",
        )

    finally:
        # Always clean up temp file — even on error
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[UPLOAD] Temp file deleted: '{file_path}'")
            except OSError as e:
                print(f"[UPLOAD] Warning: could not delete temp file: {e}")