#!/bin/bash
# Quick development startup script for ContractIQ

set -e

echo "🚀 Starting ContractIQ Development Environment"
echo "================================================"

# Check if .env exists in backend
if [ ! -f backend/.env ]; then
    echo "⚠️  backend/.env not found!"
    echo "Please create backend/.env with:"
    echo "  GEMINI_API_KEY=your_api_key_here"
    echo "  CHROMA_PERSIST_PATH=./chroma_data"
    echo "  PORT=8000"
    exit 1
fi

echo "✅ Backend .env configured"

# Backend setup
echo ""
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ Virtual environment created"
fi

source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

pip install -q -r requirements.txt
echo "✅ Backend dependencies installed"

# Start backend in background
echo ""
echo "🔧 Starting FastAPI backend on http://localhost:8000"
uvicorn api.main:app --reload &
BACKEND_PID=$!

# Frontend setup
echo ""
echo "🎨 Setting up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    npm install -q
    echo "✅ Frontend dependencies installed"
fi

echo ""
echo "🌐 Starting React frontend on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "================================================"
echo "✨ ContractIQ is running!"
echo "================================================"
echo "📱 Frontend:  http://localhost:5173"
echo "🔌 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for interrupt
wait
