#!/bin/bash
set -e

# --- CONFIG ---
# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "[INFO] Loading environment variables from .env file"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Database credentials - can be overridden by environment variables
DB_NAME="${DB_NAME:-smart_locker_db}"
DB_USER="${DB_USER:-smart_locker_user}"
DB_PASS="${DB_PASS:-smartlockerpass123}"
DB_PORT="${DB_PORT:-5432}"
DB_HOST="${DB_HOST:-localhost}"
DATABASE_URL="postgresql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill processes using a port
kill_port_processes() {
    local port=$1
    if port_in_use $port; then
        print_warning "Port $port is in use. Killing existing processes..."
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to check if tmux is available
check_tmux() {
    command_exists tmux
}

# Function to start backend
start_backend() {
    print_info "Starting backend server..."
    export DATABASE_URL="$DATABASE_URL"
    export FLASK_ENV=development
    
    # Enter backend directory
    pushd backend > /dev/null
    source ../.venv/bin/activate
    
    # Kill any existing backend processes
    pkill -f "python.*app.py" 2>/dev/null || true
    sleep 2
    
    # Start backend with proper environment
    python app.py --port 5172 --demo --reset-db --verbose &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    popd > /dev/null
    
    # Wait for backend to start
    print_info "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5172/api/health >/dev/null 2>&1; then
            print_success "Backend is healthy!"
            return 0
        fi
        sleep 1
    done
    
    print_error "Backend failed to start"
    return 1
}

# Function to start frontend
start_frontend() {
    print_info "Starting frontend server..."
    
    # Print current working directory and contents for debugging
    echo "[DEBUG] Current directory: $(pwd)"
    echo "[DEBUG] Directory contents:"
    ls -l
    
    # Kill any existing frontend processes
    pkill -f "node.*vite" 2>/dev/null || true
    sleep 2
    
    # Check if frontend directory exists
    if [ ! -d "frontend" ]; then
        print_error "frontend directory not found!"
        exit 1
    fi
    
    # Change to frontend directory and start
    pushd frontend > /dev/null
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    popd > /dev/null
    
    # Wait for frontend to start
    print_info "Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 >/dev/null 2>&1; then
            print_success "Frontend is healthy!"
            return 0
        fi
        sleep 1
    done
    
    print_error "Frontend failed to start"
    return 1
}

# Function to run tests
run_tests() {
    print_info "Running backend tests..."
    cd backend
    source ../.venv/bin/activate
    export DATABASE_URL="$DATABASE_URL"
    
    # Run backend tests
    python -m pytest tests/ -v || {
        print_error "Backend tests failed"
        return 1
    }
    
    print_info "Running frontend tests..."
    cd ../frontend
    npm test -- --watchAll=false || {
        print_error "Frontend tests failed"
        return 1
    }
    
    print_success "All tests passed!"
}

# Function to cleanup
cleanup() {
    print_info "Cleaning up..."
    if [ -f "backend.pid" ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm -f backend.pid
    fi
    if [ -f "frontend.pid" ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm -f frontend.pid
    fi
    pkill -f "python.*app.py" 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
}

# Set up trap for cleanup
trap cleanup EXIT

# Main execution
echo "[INFO] Smart Locker System - Automated Setup and Testing"
echo "=================================================="

# Parse arguments
TEST_MODE=false
DEMO_MODE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --test)
            TEST_MODE=true
            shift
            ;;
        --demo)
            DEMO_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ "$TEST_MODE" = true ]; then
    print_info "Running in TEST mode..."
fi

# Check and install PostgreSQL
if ! command_exists psql; then
    print_info "Installing PostgreSQL..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install postgresql@14
    else
        sudo apt-get update && sudo apt-get install -y postgresql postgresql-contrib
    fi
else
    print_info "PostgreSQL is already installed"
fi

# Start PostgreSQL service
print_info "Starting PostgreSQL service..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start postgresql@14
else
    sudo systemctl start postgresql
fi

# Wait for PostgreSQL to be ready
for i in {1..30}; do
    if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        print_success "PostgreSQL is running"
        break
    fi
    sleep 1
done

# Set up database
print_info "Setting up database and user..."
echo "DATABASE_URL set to: $DATABASE_URL"

# Create database user and database
psql -U postgres -h localhost -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>/dev/null || echo "[INFO] Database user already exists: $DB_USER"
psql -U postgres -h localhost -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || echo "[INFO] Database already exists: $DB_NAME"
psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
psql -U postgres -h localhost -c "ALTER ROLE $DB_USER CREATEDB;" 2>/dev/null || true

# Set up Python environment
print_info "Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Test database connection
print_info "Testing database connection..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('$DATABASE_URL')
    conn.close()
    print('Database connection successful!')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" || {
    print_error "Database connection test failed"
    exit 1
}
print_success "Database connection test passed!"

# Install Node.js dependencies
print_info "Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Kill any existing processes
kill_port_processes 5172
kill_port_processes 5173

if [ "$TEST_MODE" = true ]; then
    # Test mode: start both servers, run tests, then stop
    print_info "Starting servers for testing..."
    
    if start_backend && start_frontend; then
        print_success "Both servers started successfully"
        
        # Run tests
        run_tests
        
        # Show server logs
        print_info "Backend logs:"
        tail -n 20 backend.log 2>/dev/null || echo "No backend logs found"
        
        print_info "Frontend logs:"
        tail -n 20 frontend.log 2>/dev/null || echo "No frontend logs found"
        
        print_success "Test mode completed successfully!"
    else
        print_error "Failed to start servers for testing"
        exit 1
    fi
else
    # Normal mode: start servers and keep running
    print_info "Starting servers in normal mode..."
    
    if check_tmux; then
        # Use tmux for split-pane view
        print_info "Using tmux for split-pane view..."
        tmux new-session -d -s smart_locker
        
        # Start backend in first pane
        tmux send-keys -t smart_locker "cd $(pwd) && source .venv/bin/activate && export DATABASE_URL='$DATABASE_URL' && cd backend && python app.py --port 5172 --demo --reset-db --verbose" C-m
        
        # Split and start frontend in second pane
        tmux split-window -h -t smart_locker
        tmux send-keys -t smart_locker "cd $(pwd)/frontend && npm run dev" C-m
        
        # Attach to tmux session
        print_success "Servers started in tmux session 'smart_locker'"
        print_info "Use 'tmux attach -t smart_locker' to view both servers"
        print_info "Press Ctrl+B, then D to detach from tmux"
    else
        # Fallback: start servers in background
        print_info "tmux not available, starting servers in background..."
        
        if start_backend && start_frontend; then
            print_success "Both servers started successfully!"
            print_info "Backend running on http://localhost:5172"
            print_info "Frontend running on http://localhost:5173"
            print_info "Press Ctrl+C to stop all servers"
            
            # Keep script running
            wait
        else
            print_error "Failed to start servers"
            exit 1
        fi
    fi
fi 