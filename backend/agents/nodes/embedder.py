from core.chromadb_client import collection
from core.gemini_client import embed_text


def embed_and_store(state: dict) -> dict:
    try:
        chunks = state.get('chunks', [])
        doc_id = state.get('doc_id')

        if not chunks:
            return {**state, 'chunk_count': 0, 'error': 'No chunks to embed'}

        documents = [chunk['text'] for chunk in chunks]
        ids = [f'{doc_id}_{i}' for i in range(len(chunks))]
        metadatas = [chunk['metadata'] for chunk in chunks]

        print(f'[EMBEDDER] Embedding {len(documents)} chunks...')
        embeddings = [embed_text(doc) for doc in documents]
        print(f'[EMBEDDER] Embeddings done, storing in ChromaDB...')

        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
        )

        print(f'[EMBEDDER] Stored {len(chunks)} chunks successfully')
        return {**state, 'chunk_count': len(chunks), 'error': None}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {**state, 'chunk_count': 0, 'error': str(e)}
