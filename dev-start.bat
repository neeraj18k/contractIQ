@echo off
REM Quick development startup script for ContractIQ (Windows)

echo 🚀 Starting ContractIQ Development Environment
echo ================================================

REM Check if .env exists
if not exist backend\.env (
    echo ⚠️  backend\.env not found!
    echo Please create backend\.env with:
    echo   GEMINI_API_KEY=your_api_key_here
    echo   CHROMA_PERSIST_PATH=./chroma_data
    echo   PORT=8000
    exit /b 1
)

echo ✅ Backend .env configured

REM Backend setup
echo.
echo 📦 Setting up backend...
cd backend

if not exist venv (
    python -m venv venv
    echo ✅ Virtual environment created
)

call venv\Scripts\activate.bat

pip install -q -r requirements.txt
echo ✅ Backend dependencies installed

echo.
echo 🔧 Starting FastAPI backend on http://localhost:8000
start cmd /k "uvicorn api.main:app --reload"

REM Frontend setup
echo.
echo 🎨 Setting up frontend...
cd ..\frontend

if not exist node_modules (
    call npm install
    echo ✅ Frontend dependencies installed
)

echo.
echo 🌐 Starting React frontend on http://localhost:5173
start cmd /k "npm run dev"

echo.
echo ================================================
echo ✨ ContractIQ is running!
echo ================================================
echo 📱 Frontend:  http://localhost:5173
echo 🔌 Backend:   http://localhost:8000
echo 📚 API Docs:  http://localhost:8000/docs
echo.
echo Close these windows to stop the services
echo.

cd ..\..
