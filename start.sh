#!/bin/bash

# Smart Locker System - Enterprise Deployment Script
# Version: 2.0.0
# Author: Smart Locker Development Team
# License: MIT

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_PORT=5172
FRONTEND_PORT=5173
DATABASE_NAME="smart_locker_db"
DATABASE_USER="smart_locker_user"
DATABASE_PASSWORD="smartlockerpass123"
DATABASE_HOST="localhost"
DATABASE_PORT="5432"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
DEMO_MODE=false
RESET_DB=false
VERBOSE=false
MINIMAL=false
TEST_MODE=false
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --demo)
            DEMO_MODE=true
            shift
            ;;
        --reset-db)
            RESET_DB=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --minimal)
            MINIMAL=true
            shift
            ;;
        --test)
            TEST_MODE=true
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Show help
if [ "$HELP" = true ]; then
    echo "Smart Locker System - Enterprise Deployment Script"
    echo "=================================================="
    echo ""
    echo "Usage: ./start.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --demo          Load demo data (users, lockers, items)"
    echo "  --reset-db      Reset database and recreate tables"
    echo "  --verbose       Enable verbose logging"
    echo "  --minimal       Minimal mode (admin user only, empty lockers)"
    echo "  --test          Run comprehensive test suite after startup"
    echo "  --help, -h      Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./start.sh --demo --reset-db --verbose"
    echo "  ./start.sh --minimal --test"
    echo "  ./start.sh --demo --test"
    echo ""
    echo "Default behavior:"
    echo "  - Starts backend on port $BACKEND_PORT"
    echo "  - Starts frontend on port $FRONTEND_PORT"
    echo "  - Uses PostgreSQL database"
    echo "  - Loads minimal admin user if no data exists"
    echo ""
    echo "Troubleshooting:"
    echo "  If npm installation fails, manually clean and retry:"
    echo "    cd frontend && rm -rf node_modules package-lock.json"
    echo "    npm cache clean --force && npm install"
    exit 0
fi

# Main execution
main() {
    log_info "Smart Locker System - Enterprise Deployment"
    log_info "=========================================="
    
    # Check prerequisites
    check_prerequisites
    
    # Setup environment
    setup_environment
    
    # Start services
    start_services
    
    # Run tests if requested
    if [ "$TEST_MODE" = true ]; then
        run_tests
    fi
    
    log_success "Smart Locker System deployment completed successfully"
    log_info "Backend: http://localhost:$BACKEND_PORT"
    log_info "Frontend: http://localhost:$FRONTEND_PORT"
    log_info "Press Ctrl+C to stop all services"
}

# Check system prerequisites
check_prerequisites() {
    log_info "Checking system prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is required but not installed"
        exit 1
    fi
    
    # Check PostgreSQL
    if ! command -v psql &> /dev/null; then
        log_error "PostgreSQL is required but not installed"
        log_info "Install PostgreSQL: https://www.postgresql.org/download/"
        exit 1
    fi
    
    log_success "All prerequisites are satisfied"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install Node.js dependencies
    log_info "Installing Node.js dependencies..."
    cd frontend
    
    # Clean npm cache and node_modules if there are issues
    if [ -d "node_modules" ]; then
        log_info "Cleaning existing node_modules..."
        rm -rf node_modules package-lock.json
    fi
    
    # Clear npm cache
    npm cache clean --force
    
    # Install dependencies with retry logic
    local npm_retries=3
    local npm_success=false
    
    for ((i=1; i<=npm_retries; i++)); do
        log_info "Installing Node.js dependencies (attempt $i/$npm_retries)..."
        if npm install; then
            npm_success=true
            break
        else
            log_warning "npm install failed (attempt $i/$npm_retries)"
            if [ $i -lt $npm_retries ]; then
                log_info "Cleaning and retrying..."
                rm -rf node_modules package-lock.json
                npm cache clean --force
                sleep 2
            fi
        fi
    done
    
    if [ "$npm_success" = false ]; then
        log_error "Failed to install Node.js dependencies after $npm_retries attempts"
        exit 1
    fi
    
    # Ensure Puppeteer is available for testing
    if ! npm list puppeteer > /dev/null 2>&1; then
        log_info "Installing Puppeteer for automated testing..."
        npm install puppeteer
    fi
    
    cd ..
    
    # Setup database
    setup_database
    
    log_success "Environment setup completed"
}

# Setup database
setup_database() {
    log_info "Setting up database..."
    
    # Start PostgreSQL service
    if command -v brew &> /dev/null; then
        # macOS
        brew services start postgresql@14 2>/dev/null || true
    elif command -v systemctl &> /dev/null; then
        # Linux
        sudo systemctl start postgresql 2>/dev/null || true
    fi
    
    # Create database and user
    log_info "Creating database and user..."
    
    # Create user if it doesn't exist
    psql -U postgres -c "CREATE USER $DATABASE_USER WITH PASSWORD '$DATABASE_PASSWORD';" 2>/dev/null || true
    
    # Create database if it doesn't exist
    psql -U postgres -c "CREATE DATABASE $DATABASE_NAME OWNER $DATABASE_USER;" 2>/dev/null || true
    
    # Grant privileges
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $DATABASE_USER;"
    psql -U postgres -c "ALTER USER $DATABASE_USER CREATEDB;"
    
    # Set DATABASE_URL environment variable
    export DATABASE_URL="postgresql://$DATABASE_USER:$DATABASE_PASSWORD@$DATABASE_HOST:$DATABASE_PORT/$DATABASE_NAME"
    log_info "DATABASE_URL set to: $DATABASE_URL"
    
    log_success "Database setup completed"
}

# Start services
start_services() {
    log_info "Starting Smart Locker System services..."
    
    # Kill existing processes on ports
    kill_process_on_port $BACKEND_PORT
    kill_process_on_port $FRONTEND_PORT
    
    # Start backend
    start_backend
    
    # Start frontend
    start_frontend
    
    log_success "All services started successfully"
}

# Kill process on port
kill_process_on_port() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        log_warning "Port $port is in use. Killing existing process..."
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Start backend service
start_backend() {
    log_info "Starting backend server..."
    
    cd backend
    
    # Build command based on flags
    local cmd="python app.py --port $BACKEND_PORT"
    
    if [ "$DEMO_MODE" = true ]; then
        cmd="$cmd --demo"
    fi
    
    if [ "$RESET_DB" = true ]; then
        cmd="$cmd --reset-db"
    fi
    
    if [ "$VERBOSE" = true ]; then
        cmd="$cmd --verbose"
    fi
    
    if [ "$MINIMAL" = true ]; then
        cmd="$cmd --minimal"
    fi
    
    # Start backend in background
    if [ "$VERBOSE" = true ]; then
        $cmd &
    else
        $cmd > /dev/null 2>&1 &
    fi
    
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    log_info "Waiting for backend to start..."
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null 2>&1; then
            log_success "Backend is healthy!"
            break
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    if [ $attempts -eq 30 ]; then
        log_error "Backend failed to start within 30 seconds"
        exit 1
    fi
}

# Start frontend service
start_frontend() {
    log_info "Starting frontend server..."
    
    cd frontend
    
    # Start frontend in background
    if [ "$VERBOSE" = true ]; then
        npm run dev &
    else
        npm run dev > /dev/null 2>&1 &
    fi
    
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    log_info "Waiting for frontend to start..."
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            log_success "Frontend is healthy!"
            break
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    if [ $attempts -eq 30 ]; then
        log_error "Frontend failed to start within 30 seconds"
        exit 1
    fi
}

# Run comprehensive tests
run_tests() {
    log_info "Running comprehensive test suite..."
    
    # Wait a bit for services to fully initialize
    sleep 5
    
    # Check if tests directory exists
    if [ ! -d "tests" ]; then
        log_warning "Tests directory not found. Skipping tests."
        return
    fi
    
    # Run tests
    if node tests/run_all_tests.js; then
        log_success "All tests passed!"
    else
        log_error "Some tests failed. Check the output above for details."
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes on our ports
    kill_process_on_port $BACKEND_PORT
    kill_process_on_port $FRONTEND_PORT
    
    log_success "Cleanup completed"
}

# Trap cleanup on exit
trap cleanup EXIT

# Run main function
main "$@" 