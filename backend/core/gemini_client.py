import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from core.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

llm = GoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7,
)

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIM = 3072


def embed_text(text: str) -> list:
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]
    except Exception as e:
        print(f"Embedding error: {e}")
        raise


def embed_query(text: str) -> list:
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_query",
        )
        return result["embedding"]
    except Exception as e:
        print(f"Query embedding error: {e}")
        raise


def get_llm():
    return llm