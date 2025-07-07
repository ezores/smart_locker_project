#!/bin/bash

# Smart Locker System Development Startup Script

echo "🚀 Starting Smart Locker System Development Environment..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment and install Python dependencies
echo "📦 Installing Python dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start Flask backend in background
echo "🔧 Starting Flask backend on port 5050..."
source .venv/bin/activate
python app.py --port 5050 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start React frontend
echo "⚛️  Starting React frontend on port 5173..."
npm run dev &
FRONTEND_PID=$!

echo "✅ Development environment started!"
echo "   Backend: http://localhost:5050"
echo "   Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait 