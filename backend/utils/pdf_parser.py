import os
import re
import fitz  # pymupdf — replaces PyPDF2, far better text extraction


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from PDF file page by page using PyMuPDF (fitz).

    Args:
        file_path: Absolute or relative path to the PDF file.

    Returns:
        List of dicts: [{page_num: int, text: str}, ...]
        Only non-empty pages are included.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If no text could be extracted (likely a scanned PDF).
        RuntimeError: On any fitz-level failure.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found: {file_path}")

    pages_data = []

    try:
        doc = fitz.open(file_path)

        for page_num in range(len(doc)):
            page = doc[page_num]

            # get_text("text") gives plain text with newlines preserved
            # get_text("blocks") is an alternative for layout-heavy docs
            raw_text = page.get_text("text")

            cleaned = _clean_text(raw_text)

            if cleaned:                          # skip blank / whitespace-only pages
                pages_data.append({
                    "page_num": page_num + 1,    # 1-indexed
                    "text": cleaned,
                })

        doc.close()

    except fitz.FileDataError as e:
        raise RuntimeError(f"Corrupt or unreadable PDF '{file_path}': {e}") from e
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF '{file_path}': {e}") from e

    if not pages_data:
        raise ValueError(
            f"No extractable text found in '{file_path}'. "
            "This may be a scanned/image-only PDF — OCR support needed."
        )

    print(f"✓ Extracted text from {len(pages_data)} pages in '{os.path.basename(file_path)}'")
    return pages_data


def _clean_text(text: str) -> str:
    """
    Normalise raw PDF text:
    - Collapse excessive whitespace / blank lines
    - Remove null bytes and form-feed characters
    - Strip leading/trailing whitespace
    """
    if not text:
        return ""

    # Remove null bytes and form-feed chars that PyMuPDF occasionally emits
    text = text.replace("\x00", "").replace("\x0c", "\n")

    # Collapse 3+ consecutive newlines → double newline (preserve paragraphs)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse runs of spaces/tabs (but keep newlines)
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Strip
    return text.strip()


def validate_pdf(file_path: str) -> bool:
    """
    Return True if the file exists, is readable by fitz, and has at least one page.
    """
    try:
        if not os.path.exists(file_path):
            return False
        doc = fitz.open(file_path)
        valid = len(doc) > 0
        doc.close()
        return valid
    except Exception:
        return False


def get_pdf_metadata(file_path: str) -> dict:
    """
    Return basic PDF metadata — useful for logging / session store.

    Returns:
        {page_count, title, author, file_size_kb}
    """
    try:
        doc = fitz.open(file_path)
        meta = doc.metadata or {}
        page_count = len(doc)
        doc.close()
        file_size_kb = round(os.path.getsize(file_path) / 1024, 2)
        return {
            "page_count":    page_count,
            "title":         meta.get("title", ""),
            "author":        meta.get("author", ""),
            "file_size_kb":  file_size_kb,
        }
    except Exception as e:
        print(f"Could not read PDF metadata: {e}")
        return {}