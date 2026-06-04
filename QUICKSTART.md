# ContractIQ - Quick Start Guide

## 🎯 5-Minute Setup

### 1. Get Gemini API Key (2 minutes)
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API key"
3. Copy the key

### 2. Configure Backend (1 minute)
```bash
cd contractiq/backend
echo "GEMINI_API_KEY=<YOUR_API_KEY>" > .env
echo "CHROMA_PERSIST_PATH=./chroma_data" >> .env
echo "PORT=8000" >> .env
```

### 3. Run Services (2 minutes)

**Option A: Using Docker (Recommended)**
```bash
cd contractiq
GEMINI_API_KEY=your_api_key docker-compose up --build
```

**Option B: Manual Setup**

**Terminal 1 - Backend:**
```bash
cd contractiq/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd contractiq/frontend
npm install
npm run dev
```

### 4. Access the App
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📋 Test Flow

1. **Open** http://localhost:5173
2. **Upload** a PDF contract (use sample_contract.txt converted to PDF)
3. **Ask** a question like:
   - "What is the termination notice period?"
   - "What are the confidentiality obligations?"
   - "What non-compete restrictions exist?"

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.11+)
python --version

# Check Gemini API key
cat .env  # Verify GEMINI_API_KEY is set

# Check dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check Node version (need 20+)
node --version

# Clear node_modules
rm -rf node_modules
npm install

# Clear npm cache
npm cache clean --force
```

### ChromaDB permission error
```bash
# Create chroma_data directory with permissions
mkdir -p backend/chroma_data
chmod 755 backend/chroma_data
```

### Port already in use
```bash
# Change ports in .env and frontend/.env
# Or kill existing processes:
# Linux/Mac: lsof -i :8000 | kill -9
# Windows: netstat -ano | findstr :8000, taskkill /PID <PID>
```

## 📚 Example Queries

Try these on the sample NDA contract:

### Legal Clauses
- "List all the main sections and what they cover"
- "What are the party's obligations?"
- "What happens if someone breaches this agreement?"

### Risk Analysis
- "What are the risk clauses I should know about?"
- "Are there any unusual or strict requirements?"
- "What could go wrong with this contract?"

### Specific Terms
- "What is the duration of this agreement?"
- "What are the termination conditions?"
- "Are there any renewal options?"
- "What jurisdiction applies?"

## 🗂️ File Structure Quick Reference

```
contractiq/
├── backend/              # FastAPI + LangGraph
│   ├── agents/          # LangGraph workflows
│   ├── api/             # REST endpoints
│   ├── core/            # Configuration & clients
│   ├── models/          # Pydantic schemas
│   ├── utils/           # PDF parsing & chunking
│   └── .env             # Configuration
├── frontend/            # React + Vite
│   ├── src/
│   │   ├── api/        # Axios client
│   │   ├── components/ # UI components
│   │   ├── pages/      # React pages
│   │   └── hooks/      # Custom hooks
│   └── .env            # Frontend config
└── README.md           # Full documentation
```

## 🚀 Next Steps

1. **Upload Sample Contract**: Use `generate_sample_pdf.py` to create a test PDF
2. **Explore Chat Interface**: Try different questions
3. **Review API Documentation**: Visit http://localhost:8000/docs
4. **Check Source Citations**: See where answers come from in the contract
5. **Deploy with Docker**: Use docker-compose for production

## 📖 Learn More

- [Full README](./README.md) - Complete documentation
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/) - Workflow orchestration
- [ChromaDB Docs](https://docs.trychroma.com/) - Vector database
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Backend framework
- [Gemini API](https://ai.google.dev/) - LLM & embeddings

## 💡 Tips

- Use clear, specific questions for better answers
- Check source citations to verify claims
- PDFs under 50 pages work best (faster processing)
- Session history is preserved until you clear it
- Multiple uploads create separate document spaces

---

**Happy analyzing! 📄✨**
