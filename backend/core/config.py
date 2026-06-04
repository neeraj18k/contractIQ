import os
from dotenv import load_dotenv

load_dotenv()

# ─── Gemini ───────────────────────────────────────────────
GEMINI_API_KEY        = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL          = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")

# ─── ChromaDB ─────────────────────────────────────────────
CHROMA_PERSIST_PATH   = os.getenv("CHROMA_PERSIST_PATH", "./chroma_data")
CHROMA_COLLECTION     = os.getenv("CHROMA_COLLECTION", "contracts")

# ─── Server ───────────────────────────────────────────────
PORT                  = int(os.getenv("PORT", 8000))
HOST                  = os.getenv("HOST", "0.0.0.0")

# ─── Chunking ─────────────────────────────────────────────
CHUNK_SIZE            = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP         = int(os.getenv("CHUNK_OVERLAP", 50))
MIN_CHUNK_LENGTH      = int(os.getenv("MIN_CHUNK_LENGTH", 50))  # skip tiny chunks

# ─── LangGraph ────────────────────────────────────────────
DEFAULT_THREAD_ID     = "default-thread"   # fallback thread_id for LangGraph config

# ─── Validation ───────────────────────────────────────────
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

os.makedirs(CHROMA_PERSIST_PATH, exist_ok=True)