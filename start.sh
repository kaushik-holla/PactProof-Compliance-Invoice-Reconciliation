#!/bin/bash

# Script starts both backend and frontend servers

set -e

echo "Starting PactProof - Compliance Invoice Reconciliation"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is required but not installed."
    echo "    Frontend will not start automatically."
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "   ⚠️  Edit .env and add your API keys (or use STUB mode with empty keys)"
fi

# Install backend dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt 2>/dev/null || pip install -r requirements.txt

# Create uploads directory (cache dirs auto-created by app)
mkdir -p uploads

# Start backend in background
echo ""
echo "Starting FastAPI backend server on http://localhost:8000"
cd backend
python -c "import uvicorn; uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)" &
BACKEND_PID=$!
cd ..

sleep 2

# Check if backend started
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Failed to start backend"
    exit 1
fi

echo "Backend started with (PID: $BACKEND_PID)"

# Start frontend if Node is available
if command -v node &> /dev/null; then
    echo ""
    echo "Starting React frontend server on http://localhost:5173..."
    cd ui
    npm install --quiet 2>/dev/null || npm install
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend started (PID: $FRONTEND_PID)"
else
    FRONTEND_PID=""
fi

echo "PactProof is running!"
echo ""
echo "Frontend:  http://localhost:5173"
echo "API:       http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop servers"

# Wait for signals
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo 'Stopped PactProof.'; exit 0" INT TERM

wait

