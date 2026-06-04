import chromadb
from chromadb.config import Settings
from core.config import CHROMA_PERSIST_PATH

client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_PATH,
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(
    name='contracts',
    metadata={'hnsw:space': 'cosine'},
    embedding_function=None,
)


def add_documents(documents: list, ids: list, metadatas: list, embeddings: list):
    try:
        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
        )
    except Exception as e:
        print(f'ChromaDB add error: {e}')
        raise


def query_documents(query_text: str, n: int = 5, where_filter: dict = None):
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n,
            where=where_filter,
        )
        return results
    except Exception as e:
        print(f'ChromaDB query error: {e}')
        raise


def get_collection():
    return collection


def clear_collection():
    try:
        all_items = collection.get()
        if all_items['ids']:
            collection.delete(ids=all_items['ids'])
    except Exception as e:
        print(f'ChromaDB clear error: {e}')
        raise
