#!/bin/bash

# Smart Locker System Development Startup Script
# @author Alp
# @date 2024-12-XX
# @description Starts both backend and frontend for development with enhanced options

set -e

# Get the directory of this script and the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Default values
DEMO_MODE=false
BACKEND_PORT=5050
FRONTEND_PORT=5173
BACKEND_HOST="0.0.0.0"
RESET_DB=false
SKIP_DEPS=false
VERBOSE=false
LOG_LEVEL="INFO"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to show help
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Smart Locker System Development Environment Startup Script

Options:
  -d, --demo              Load demo data for testing
  -p, --backend-port PORT Backend port (default: 5050)
  -f, --frontend-port PORT Frontend port (default: 5173)
  -H, --host HOST         Backend host to bind to (default: 0.0.0.0)
  -r, --reset-db          Reset database before starting
  -s, --skip-deps         Skip dependency installation
  -v, --verbose           Enable verbose output
  -l, --log-level LEVEL   Set log level (DEBUG, INFO, WARNING, ERROR)
  -h, --help              Show this help message

Examples:
  $0                      # Start with default settings
  $0 --demo               # Start with demo data
  $0 -p 8080 -f 3000      # Custom ports
  $0 --reset-db --demo    # Reset DB and load demo data
  $0 --verbose --log-level DEBUG  # Verbose output with debug logging

Environment Variables:
  FLASK_ENV               Set Flask environment (development/production)
  NODE_ENV                Set Node.js environment (development/production)
  PYTHONPATH              Python path for imports

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--demo)
            DEMO_MODE=true
            shift
            ;;
        -p|--backend-port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        -f|--frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        -H|--host)
            BACKEND_HOST="$2"
            shift 2
            ;;
        -r|--reset-db)
            RESET_DB=true
            shift
            ;;
        -s|--skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -l|--log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate ports
if ! [[ "$BACKEND_PORT" =~ ^[0-9]+$ ]] || [ "$BACKEND_PORT" -lt 1024 ] || [ "$BACKEND_PORT" -gt 65535 ]; then
    print_error "Invalid backend port: $BACKEND_PORT (must be 1024-65535)"
    exit 1
fi

if ! [[ "$FRONTEND_PORT" =~ ^[0-9]+$ ]] || [ "$FRONTEND_PORT" -lt 1024 ] || [ "$FRONTEND_PORT" -gt 65535 ]; then
    print_error "Invalid frontend port: $FRONTEND_PORT (must be 1024-65535)"
    exit 1
fi

if [ "$BACKEND_PORT" = "$FRONTEND_PORT" ]; then
    print_error "Backend and frontend ports cannot be the same: $BACKEND_PORT"
    exit 1
fi

# Check if ports are available
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port is already in use by another process"
        read -p "Do you want to terminate the existing process and continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_step "Terminating process using port $port..."
            lsof -ti:$port | xargs kill -9 2>/dev/null
            sleep 2
            print_status "Process terminated, port $port is now available"
        else
            exit 1
        fi
    fi
}

check_port $BACKEND_PORT "Backend"
check_port $FRONTEND_PORT "Frontend"

print_success "Starting Smart Locker System Development Environment..."

# Set environment variables
export FLASK_ENV=development
export NODE_ENV=development
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

if [ "$VERBOSE" = true ]; then
    print_info "Environment variables set:"
    print_info "  FLASK_ENV: $FLASK_ENV"
    print_info "  NODE_ENV: $NODE_ENV"
    print_info "  PYTHONPATH: $PYTHONPATH"
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    print_step "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
    print_status "Virtual environment created"
fi

# Activate virtual environment and install Python dependencies
if [ "$SKIP_DEPS" = false ]; then
    print_step "Installing Python dependencies..."
    source "$PROJECT_ROOT/.venv/bin/activate" || { print_error "Failed to activate virtual environment. Exiting."; exit 1; }
    
    # Check if requirements.txt exists
    if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
        print_error "requirements.txt not found in $PROJECT_ROOT"
        exit 1
    fi
    
    if [ "$VERBOSE" = true ]; then
        pip install -r "$PROJECT_ROOT/requirements.txt" -v
    else
        pip install -r "$PROJECT_ROOT/requirements.txt" > /dev/null 2>&1
    fi
    print_status "Python dependencies installed"
fi

# Always install Node.js dependencies to ensure up-to-date
if [ "$SKIP_DEPS" = false ]; then
    print_step "Installing Node.js dependencies..."
    
    # Check if package.json exists
    if [ ! -f "$PROJECT_ROOT/frontend/package.json" ]; then
        print_error "package.json not found in $PROJECT_ROOT/frontend"
        exit 1
    fi
    
    cd "$PROJECT_ROOT/frontend"
    if [ "$VERBOSE" = true ]; then
        npm install
    else
        npm install > /dev/null 2>&1
    fi
    cd "$PROJECT_ROOT"
    print_status "Node.js dependencies installed"
fi

# Reset database if requested
if [ "$RESET_DB" = true ]; then
    print_step "Resetting database..."
    source "$PROJECT_ROOT/.venv/bin/activate"
    cd "$PROJECT_ROOT/backend"
    if [ -f "db/locker.db" ]; then
        rm -f "db/locker.db"
        print_status "Database file removed"
    fi
    cd "$PROJECT_ROOT"
fi

# Prepare backend command
BACKEND_CMD="python backend/app.py --port $BACKEND_PORT --host $BACKEND_HOST"
if [ "$DEMO_MODE" = true ]; then
    BACKEND_CMD="$BACKEND_CMD --demo"
    print_info "Demo mode enabled - loading test data..."
fi

# Start Flask backend in background
print_step "Starting Flask backend on port $BACKEND_PORT..."
source "$PROJECT_ROOT/.venv/bin/activate"
if [ "$VERBOSE" = true ]; then
    $BACKEND_CMD &
else
    $BACKEND_CMD > /dev/null 2>&1 &
fi
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend failed to start"
    exit 1
fi

print_status "Backend started successfully (PID: $BACKEND_PID)"

# Verify demo data was loaded if requested
if [ "$DEMO_MODE" = true ]; then
    print_step "Verifying demo data..."
    sleep 3
    
    # Test API endpoints to verify demo data
    if curl -s "http://localhost:$BACKEND_PORT/api/items" > /dev/null 2>&1; then
        ITEM_COUNT=$(curl -s "http://localhost:$BACKEND_PORT/api/items" | grep -o '"id"' | wc -l)
        print_status "Demo data verified: $ITEM_COUNT items found"
    else
        print_warning "Could not verify demo data - API not responding yet"
    fi
fi

# Start React frontend on specified port
print_step "Starting React frontend on port $FRONTEND_PORT..."
cd "$PROJECT_ROOT/frontend"
if [ "$VERBOSE" = true ]; then
    npm run dev -- --port $FRONTEND_PORT &
else
    npm run dev -- --port $FRONTEND_PORT > /dev/null 2>&1 &
fi
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

print_status "Frontend started successfully (PID: $FRONTEND_PID)"

# Print summary
sleep 2
echo
print_success "Development environment started!"
echo "   Backend:  http://$BACKEND_HOST:$BACKEND_PORT"
echo "   Frontend: http://localhost:$FRONTEND_PORT"

if [ "$DEMO_MODE" = true ]; then
    echo "   Demo data loaded - use admin/admin123 or any student with password123"
fi

if [ "$RESET_DB" = true ]; then
    echo "   Database reset completed"
fi

echo
print_info "Press Ctrl+C to stop both servers."

# Function to cleanup on exit
cleanup() {
    echo
    print_step "Stopping servers..."
    
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        print_status "Backend stopped"
    fi
    
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        print_status "Frontend stopped"
    fi
    
    print_success "All servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait 