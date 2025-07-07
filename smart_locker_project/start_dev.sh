#!/bin/bash

# Smart Locker System Development Startup Script

set -e

echo "🚀 Starting Smart Locker System Development Environment..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment and install Python dependencies
echo "📦 Installing Python dependencies..."
source .venv/bin/activate || { echo "❌ Failed to activate virtual environment. Exiting."; exit 1; }
pip install -r requirements.txt

# Always install Node.js dependencies to ensure up-to-date
echo "📦 Installing Node.js dependencies..."
npm install

# Start Flask backend in background
echo "🔧 Starting Flask backend on port 5050..."
source .venv/bin/activate
python app.py --port 5050 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start React frontend on port 5173
echo "⚛️  Starting React frontend on port 5173..."
npm run dev -- --port 5173 &
FRONTEND_PID=$!

# Print summary
sleep 2
echo "\n✅ Development environment started!"
echo "   Backend:  http://localhost:5050"
echo "   Frontend: http://localhost:5173"
echo "\nPress Ctrl+C to stop both servers."

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