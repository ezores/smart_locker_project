#!/bin/bash

# Smart Locker System Development Startup Script
# @author Alp
# @date 2024-12-XX
# @description Starts both backend and frontend for development

set -e

# Get the directory of this script and the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Parse command line arguments
DEMO_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --demo)
            DEMO_MODE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --demo    Load demo data for testing"
            echo "  --help    Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0              # Start without demo data"
            echo "  $0 --demo       # Start with demo data"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🚀 Starting Smart Locker System Development Environment..."

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
fi

# Activate virtual environment and install Python dependencies
echo "📦 Installing Python dependencies..."
source "$PROJECT_ROOT/.venv/bin/activate" || { echo "❌ Failed to activate virtual environment. Exiting."; exit 1; }
pip install -r "$PROJECT_ROOT/requirements.txt"

# Always install Node.js dependencies to ensure up-to-date
echo "📦 Installing Node.js dependencies..."
cd "$PROJECT_ROOT/frontend"
npm install
cd "$PROJECT_ROOT"

# Prepare backend command
BACKEND_CMD="python backend/app.py --port 5050"
if [ "$DEMO_MODE" = true ]; then
    BACKEND_CMD="$BACKEND_CMD --demo"
    echo "📊 Demo mode enabled - loading test data..."
fi

# Start Flask backend in background
echo "🔧 Starting Flask backend on port 5050..."
source "$PROJECT_ROOT/.venv/bin/activate"
$BACKEND_CMD &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start React frontend on port 5173
echo "⚛️  Starting React frontend on port 5173..."
cd "$PROJECT_ROOT/frontend"
npm run dev -- --port 5173 &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

# Print summary
sleep 2
echo "\n✅ Development environment started!"
echo "   Backend:  http://localhost:5050"
echo "   Frontend: http://localhost:5173"

if [ "$DEMO_MODE" = true ]; then
    echo "   📊 Demo data loaded - use admin/admin123 or any student with password123"
fi

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