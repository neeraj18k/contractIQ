from core.chromadb_client import collection
from core.gemini_client import embed_query


def retrieve_relevant_chunks(state: dict) -> dict:
    try:
        query = state.get('query')
        doc_id = state.get('doc_id')

        if not query:
            return {**state, 'retrieved_chunks': [], 'error': 'Query cannot be empty'}

        print(f'[RETRIEVER] Embedding query...')
        query_embedding = embed_query(query)
        print(f'[RETRIEVER] Query embedding dim={len(query_embedding)}')

        where_filter = {'source_file': {'$eq': doc_id}}

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            where=where_filter,
        )

        retrieved_chunks = []
        if results and results.get('documents') and len(results['documents']) > 0:
            docs = results['documents'][0]
            distances = results.get('distances', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]

            for i, doc_text in enumerate(docs):
                retrieved_chunks.append({
                    'text': doc_text,
                    'metadata': metadatas[i] if i < len(metadatas) else {},
                    'relevance_score': 1 - (distances[i] if i < len(distances) else 0),
                })

        print(f'[RETRIEVER] Found {len(retrieved_chunks)} chunks')
        return {**state, 'retrieved_chunks': retrieved_chunks, 'error': None}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {**state, 'retrieved_chunks': [], 'error': str(e)}