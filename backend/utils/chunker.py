import re
from core.config import CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_LENGTH


class RecursiveCharacterSplitter:
    """
    Recursive character splitter that tries natural break points first
    (paragraphs → sentences → words → characters) before hard-cutting.
    Mirrors LangChain's RecursiveCharacterTextSplitter behaviour but
    without the extra dependency.
    """

    # Ordered from coarsest to finest — tries each separator in sequence
    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""]

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
        min_chunk_length: int = MIN_CHUNK_LENGTH,
        separators: list[str] | None = None,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) must be < chunk_size ({chunk_size})"
            )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_length = min_chunk_length
        self.separators = separators or self.DEFAULT_SEPARATORS

    # ── Core splitter ──────────────────────────────────────────────────────────

    def split_text(self, text: str) -> list[str]:
        """
        Split text into overlapping chunks using recursive separator strategy.

        Returns:
            List of non-trivial chunk strings.
        """
        if not text or not text.strip():
            return []

        raw_chunks = self._recursive_split(text, self.separators)
        merged = self._merge_with_overlap(raw_chunks)
        return [c for c in merged if self._is_valid_chunk(c)]

    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        """Try each separator; fall back to the next if chunks are still too large."""
        if not text.strip():
            return []

        # Pick the first separator that actually exists in the text
        separator = ""
        remaining_seps = []
        for i, sep in enumerate(separators):
            if sep == "" or sep in text:
                separator = sep
                remaining_seps = separators[i + 1 :]
                break

        if separator == "":
            # Hard split — no natural break found
            return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

        splits = text.split(separator)
        result = []
        for split in splits:
            split = split.strip()
            if not split:
                continue
            if len(split) <= self.chunk_size:
                result.append(split)
            else:
                # Still too large — recurse with finer separators
                result.extend(self._recursive_split(split, remaining_seps))

        return result

    def _merge_with_overlap(self, splits: list[str]) -> list[str]:
        """
        Merge small splits into chunks up to chunk_size,
        then add overlap from the previous chunk's tail.
        """
        chunks: list[str] = []
        current_parts: list[str] = []
        current_len = 0

        for split in splits:
            split_len = len(split)

            if current_len + split_len > self.chunk_size and current_parts:
                # Flush current chunk
                chunk_text = " ".join(current_parts).strip()
                if chunk_text:
                    chunks.append(chunk_text)

                # Build overlap: take tail of current chunk
                overlap_text = chunk_text[-self.chunk_overlap :] if self.chunk_overlap else ""
                current_parts = [overlap_text] if overlap_text.strip() else []
                current_len = len(overlap_text)

            current_parts.append(split)
            current_len += split_len + 1  # +1 for space separator

        # Flush remaining
        if current_parts:
            chunk_text = " ".join(current_parts).strip()
            if chunk_text:
                chunks.append(chunk_text)

        return chunks

    def _is_valid_chunk(self, text: str) -> bool:
        """
        Reject chunks that are too short, whitespace-only,
        or pure punctuation / numbers with no real words.
        """
        if not text or len(text.strip()) < self.min_chunk_length:
            return False
        # Must contain at least one word (2+ alphabetic chars)
        if not re.search(r"[a-zA-Z]{2,}", text):
            return False
        return True

    # ── Document-level splitter ────────────────────────────────────────────────

    def split_documents(
        self,
        pages_data: list[dict],
        source_file: str,
        source_filename: str,
    ) -> list[dict]:
        """
        Split pages into chunks with rich metadata.

        Args:
            pages_data:       Output of pdf_parser.extract_text_from_pdf()
                              [{page_num: int, text: str}, ...]
            source_file:      Unique document / session ID
            source_filename:  Original filename (for display)

        Returns:
            [{text: str, metadata: dict}, ...]
        """
        if not pages_data:
            print("Warning: split_documents received empty pages_data.")
            return []

        chunks_with_metadata: list[dict] = []
        chunk_index = 0
        skipped = 0

        for page_data in pages_data:
            page_num = page_data.get("page_num", 0)
            text = page_data.get("text", "")

            if not text.strip():
                skipped += 1
                continue

            page_chunks = self.split_text(text)

            if not page_chunks:
                print(f"  ⚠ Page {page_num}: no valid chunks after splitting — skipped.")
                skipped += 1
                continue

            for chunk_text in page_chunks:
                chunks_with_metadata.append({
                    "text": chunk_text,
                    "metadata": {
                        "source_file":     source_file,
                        "source_filename": source_filename,
                        "page_num":        page_num,
                        "chunk_index":     chunk_index,
                        "chunk_length":    len(chunk_text),   # useful for debugging
                    },
                })
                chunk_index += 1

        total = len(chunks_with_metadata)
        print(
            f"✓ Chunking complete: {total} chunks from {len(pages_data) - skipped} pages "
            f"({skipped} pages skipped)."
        )

        if total == 0:
            print(
                "⚠ WARNING: 0 chunks produced. Check MIN_CHUNK_LENGTH config "
                f"(currently {self.min_chunk_length}) and PDF text quality."
            )

        return chunks_with_metadata


# ── Convenience function ───────────────────────────────────────────────────────

def split_documents(
    pages_data: list[dict],
    source_file: str,
    source_filename: str,
) -> list[dict]:
    """Module-level convenience wrapper — instantiates default splitter."""
    splitter = RecursiveCharacterSplitter()
    return splitter.split_documents(pages_data, source_file, source_filename)