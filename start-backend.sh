#!/bin/bash
cd backend
source venv/bin/activate
export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"
echo "🚀 Starting backend server on http://localhost:8000"
echo "📚 API docs will be available at http://localhost:8000/docs"
echo ""
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
