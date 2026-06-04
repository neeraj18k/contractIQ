# ContractIQ - Agentic Legal Contract Intelligence Platform

A full-stack AI-powered legal contract analysis platform built with React, FastAPI, LangGraph, and Google Gemini API.

## 🎯 Overview

ContractIQ is an intelligent contract analysis system that uses agentic AI workflows to:
- **Extract & Analyze**: Automatically extract clauses and key terms from PDFs
- **Risk Detection**: Identify potential legal risks and red flags
- **Smart Q&A**: Answer natural language questions about contract terms
- **Source Citations**: Provide exact page references for all analyses

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   React Frontend (5173)                      │
│  UploadZone → Chat Interface → Clause Highlights            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    HTTP REST API
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              FastAPI Backend (8000)                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │       LangGraph Agentic Workflows                  │    │
│  │                                                      │    │
│  │  UPLOAD FLOW:                                       │    │
│  │  PDF → [Ingestor] → [Embedder] → ChromaDB         │    │
│  │                                                      │    │
│  │  QUERY FLOW:                                        │    │
│  │  Query → [Retriever] → [Analyzer] → [Summarizer] │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────┐      │
│  │  Google Gemini API (LLM + Embeddings)            │      │
│  └────────────────────────┬──────────────────────────┘      │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────┐      │
│  │       ChromaDB (Vector Database)                 │      │
│  │  - Persistent Storage of Embeddings              │      │
│  │  - Semantic Search via Cosine Distance           │      │
│  └────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- [Free Gemini API Key](https://aistudio.google.com)
- Docker & Docker Compose (optional)

### Setup Backend

1. **Clone and navigate**:
   ```bash
   cd contractiq/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   # Edit .env file
   GEMINI_API_KEY=your_gemini_api_key_here
   CHROMA_PERSIST_PATH=./chroma_data
   PORT=8000
   ```

5. **Run backend**:
   ```bash
   uvicorn api.main:app --reload
   ```
   Backend runs at `http://localhost:8000`

### Setup Frontend

1. **Navigate to frontend**:
   ```bash
   cd contractiq/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   # .env file
   VITE_API_URL=http://localhost:8000
   ```

4. **Run frontend**:
   ```bash
   npm run dev
   ```
   Frontend runs at `http://localhost:5173`

### Docker Deployment

```bash
cd contractiq

# Configure API key
export GEMINI_API_KEY="your_api_key_here"

# Build and run
docker-compose up --build

# Access:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

## 📋 Project Structure

```
contractiq/
├── backend/
│   ├── agents/
│   │   ├── contract_agent.py        # LangGraph graph definitions
│   │   └── nodes/
│   │       ├── ingestor.py          # PDF extraction & chunking
│   │       ├── embedder.py          # Vector embedding & storage
│   │       ├── retriever.py         # Semantic search
│   │       ├── analyzer.py          # Legal analysis
│   │       └── summarizer.py        # Response formatting
│   ├── api/
│   │   ├── main.py                  # FastAPI entry point
│   │   └── routes/
│   │       ├── upload.py            # PDF upload endpoint
│   │       ├── query.py             # Query endpoint
│   │       └── sessions.py          # Session management
│   ├── core/
│   │   ├── config.py                # Configuration
│   │   ├── gemini_client.py         # Gemini API setup
│   │   └── chromadb_client.py       # ChromaDB setup
│   ├── models/
│   │   ├── schemas.py               # Pydantic models
│   │   └── session_store.py         # Chat history
│   ├── utils/
│   │   ├── pdf_parser.py            # PDF text extraction
│   │   └── chunker.py               # Text chunking
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadZone.jsx       # Drag-drop upload
│   │   │   ├── ChatWindow.jsx       # Main chat interface
│   │   │   ├── MessageBubble.jsx    # Message rendering
│   │   │   ├── ClauseHighlight.jsx  # Source display
│   │   │   ├── SourceCitation.jsx   # Citation badges
│   │   │   └── Sidebar.jsx          # Doc & history sidebar
│   │   ├── pages/
│   │   │   ├── Home.jsx             # Landing page
│   │   │   └── Chat.jsx             # Chat interface
│   │   ├── hooks/
│   │   │   └── useStream.js         # Streaming responses
│   │   ├── api/
│   │   │   └── axios.js             # API client
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── .env
│   ├── 
│   └── public/
│
├── 
└── README.md
```

## 🔄 How It Works

### Upload Flow
1. User uploads PDF via drag-drop interface
2. Backend **Ingestor** extracts text page-by-page using PyMuPDF
3. Text is split into overlapping chunks (500 tokens, 50-token overlap)
4. **Embedder** converts chunks to vectors using Gemini embeddings
5. Vectors stored in ChromaDB with metadata (page, chunk index, source)
6. System returns `doc_id` for querying

### Query Flow
1. User asks question about contract
2. **Retriever** embeds query and searches ChromaDB
3. Top 5 relevant chunks retrieved with metadata
4. **Analyzer** sends chunks + query to Gemini LLM
   - System prompt guides legal analysis
   - LLM extracts clauses, identifies risks
5. **Summarizer** formats response with citations
6. Response streamed to frontend with source page references

### State Management
```python
# LangGraph State Types
UploadState {
  file_path, doc_id, filename
  chunks[], chunk_count
  error
}

QueryState {
  query, doc_id, session_id
  chat_history, retrieved_chunks[]
  analysis, sources[], final_response
  error
}
```

## 🧪 Example Queries

Try these questions on the sample NDA:

1. **"What is the notice period for termination?"**
   - Answer: 30 days notice required (Section 2.2)

2. **"What are the confidentiality obligations?"**
   - Answer: Maintain same care as own secrets, limit access, secure storage (Section 1.2)

3. **"Are there any non-compete restrictions?"**
   - Answer: 2-year non-compete within India (Section 3.1)

4. **"What are the indemnification requirements?"**
   - Answer: Indemnify against claims from breach or unauthorized disclosure (Section 4.1)

5. **"What is the governing jurisdiction?"**
   - Answer: Karnataka High Court, India (Section 5.4)
  
   - ## Sample Contract

A sample contract is included for testing.

Location:

sample-files/SampleNDA.pdf

Try these questions:

- What is the termination notice period?
- What are the confidentiality obligations?
- Are there any risk clauses?
- When does the agreement expire?

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload PDF for analysis |
| `POST` | `/api/query` | Query contract (streaming) |
| `GET` | `/api/sessions/{id}` | Get chat history |
| `DELETE` | `/api/sessions/{id}` | Delete session |
| `GET` | `/api/health` | Health check |

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, Vite, Tailwind CSS | Modern UI with streaming |
| **Backend** | FastAPI, Uvicorn | High-performance API |
| **AI/LLM** | Google Gemini API, LangChain | LLM & embeddings |
| **Workflow** | LangGraph | Agentic graph orchestration |
| **RAG** | ChromaDB, PyMuPDF | Vector DB + PDF parsing |
| **Deployment** | Docker, Docker Compose | Container orchestration |

## 🔐 Security & Privacy

- ✅ CORS configured for local development
- ✅ Gemini API key in environment variables (not in code)
- ✅ ChromaDB persistent storage isolated per deployment
- ✅ Session-based chat history (server-side)
- ✅ PDFs processed locally, not sent to external services

## 📈 Performance Notes

- **Chunk Size**: 500 tokens with 50-token overlap (optimized for legal docs)
- **Embeddings**: Gemini embedding-001 (768 dimensions)
- **Similarity Metric**: Cosine distance (default for ChromaDB)
- **Top-K Retrieval**: 5 chunks per query
- **LLM Model**: gemini-1.5-flash (fast, cost-effective)

## 🚀 Future Enhancements

- [ ] Multi-document comparison
- [ ] Clause templates & clause library
- [ ] Integration with document signing platforms
- [ ] Batch contract processing
- [ ] Compliance checklist generation
- [ ] Contract negotiation tracking

## 📝 Resume Bullet Points

- **Built full-stack agentic legal AI platform** using React, FastAPI, LangGraph, and Google Gemini API
- **Implemented RAG pipeline** with ChromaDB vector database and semantic search for legal document analysis
- **Designed LangGraph workflows** with 5 specialized agent nodes (ingestor, embedder, retriever, analyzer, summarizer)
- **Created streaming response architecture** using FastAPI StreamingResponse for real-time LLM output
- **Implemented PDF processing** using PyMuPDF with recursive text chunking and metadata tracking
- **Built React chat interface** with message history, session management, and source citation display
is

## 📞 Support

For issues or questions:
1.
2. Verify Gemini API key is configured
3. Ensure ChromaDB directory has write permissions
4. Check frontend console for API errors

## 📄 License

MIT License - see LICENSE file

---

**Built with ❤️ using LangChain, LangGraph, and Google Gemini API**
