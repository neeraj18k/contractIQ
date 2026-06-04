def summarize_response(state: dict) -> dict:
    try:
        analysis = state.get('analysis', '')
        sources = state.get('sources', [])

        # Sources ko final response se alag rakho — frontend handle karega
        final_response = analysis

        print(f'[SUMMARIZER] Response ready')
        return {**state, 'final_response': final_response, 'error': None}

    except Exception as e:
        return {**state, 'final_response': f'Error: {str(e)}', 'error': str(e)}