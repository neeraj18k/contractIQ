"""
Analyzer node: LLM-powered contract clause analysis with RAG context.
"""
import traceback
from core.gemini_client import get_llm


def analyze_contract(state: dict) -> dict:
    """
    LangGraph node: retrieved chunks + query → LLM analysis.
    """
    query            = state.get("query", "").strip()
    retrieved_chunks = state.get("retrieved_chunks", [])
    chat_history     = state.get("chat_history", "")
    session_id       = state.get("session_id", "")

    print(f"[ANALYZER] query='{query[:80]}' chunks={len(retrieved_chunks)}")

    if not retrieved_chunks:
        return {
            **state,
            "analysis": "I could not find relevant information in the contract. Try rephrasing.",
            "sources":  [],
            "error":    None,
        }

    # ── Build context ─────────────────────────────────────────────────────────
    context = ""
    for i, chunk in enumerate(retrieved_chunks):
        meta      = chunk.get("metadata", {})
        page_num  = meta.get("page_num", "?")
        chunk_idx = meta.get("chunk_index", i)
        text      = chunk.get("text", "").strip()
        score     = chunk.get("relevance_score", 0)
        context  += f"\n[Page {page_num} | Chunk {chunk_idx} | Relevance {score:.2f}]:\n{text}\n"

    # ── Prompt ────────────────────────────────────────────────────────────────
    prompt = f"""You are a friendly contract assistant who explains contracts in simple language.

CRITICAL FORMATTING RULES — FOLLOW EXACTLY:
1. Put a SPACE between EVERY word — never merge words together
2. Each bullet point on its own separate line
3. Use proper spacing after punctuation
4. Write normally like: "This agreement lasts 3 years" NOT "Thisagreementlasts3years"
5. Understand spelling mistakes in the question — answer what they MEANT
6. Answer in plain English like explaining to a friend
7. Start directly with the answer — no preamble
8. Always cite the page number like (Page 2)

USER QUESTION: {query}

CONTRACT SECTIONS:
{context}

PREVIOUS CONVERSATION:
{chat_history}

Answer with proper spacing and formatting:"""

    # ── LLM call ──────────────────────────────────────────────────────────────
    try:
        llm      = get_llm()
        response = llm.invoke(prompt)
        analysis = response if isinstance(response, str) else response.content
    except Exception as e:
        traceback.print_exc()
        return {
            **state,
            "analysis": f"LLM error: {e}",
            "sources":  [],
            "error":    str(e),
        }

    if not analysis or not analysis.strip():
        return {**state, "analysis": "No response generated.", "sources": [], "error": None}

    print(f"[ANALYZER] ✓ {len(analysis)} chars generated.")

    # ── Sources ───────────────────────────────────────────────────────────────
    sources = []
    for chunk in retrieved_chunks:
        meta      = chunk.get("metadata", {})
        text      = chunk.get("text", "")
        sources.append({
            "page_num":        meta.get("page_num"),
            "chunk_index":     meta.get("chunk_index"),
            "source_filename": meta.get("source_filename", ""),
            # PREVIEW FIX: key must be "preview" — ClauseHighlight reads this
            "preview":         text[:200] + ("..." if len(text) > 200 else ""),
            "text":            text[:200] + ("..." if len(text) > 200 else ""),
            "relevance_score": chunk.get("relevance_score", 0),
        })

    # ── Save to session ───────────────────────────────────────────────────────
    if session_id:
        try:
            from models.session_store import session_store
            session_store.add_message(session_id, "user",      query)
            session_store.add_message(session_id, "assistant", analysis)
        except Exception as e:
            print(f"[ANALYZER] Warning: session save failed: {e}")

    return {**state, "analysis": analysis, "sources": sources, "error": None}