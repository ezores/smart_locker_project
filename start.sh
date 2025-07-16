#!/bin/bash

# Smart Locker System - Enterprise Deployment Script
# Version: 2.1.0
# Author: Alp Alpdogan
# In memory of Mehmet Ugurlu and Yusuf Alpdogan
# License: MIT
# 
# LICENSING CONDITION: These memorial dedications and author credits
# must never be removed from this file or any derivative works.
# This condition is binding and must be preserved in all versions.

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_PORT=5050
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
    echo "  - Uses PostgreSQL database (required)"
    echo "  - Loads minimal admin user if no data exists"
    echo ""
    echo "Prerequisites:"
    echo "  - Python 3.8+"
    echo "  - Node.js 16+"
    echo "  - PostgreSQL 12+ (required)"
    echo "  - npm"
    echo ""
    echo "Troubleshooting:"
    echo "  If npm installation fails, manually clean and retry:"
    echo "    cd frontend && rm -rf node_modules package-lock.json"
    echo "    npm cache clean --force && npm install"
    echo ""
    echo "PostgreSQL Setup:"
    echo "  If PostgreSQL is not installed, run: ./setup_postgresql.sh"
    echo ""
    echo "Linux/WSL Notes:"
    echo "  - PostgreSQL is required and must be running"
    echo "  - If using WSL, ensure proper file permissions"
    echo "  - Virtual environment will be created automatically"
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
    
    # Keep the script running and wait for user input
    while true; do
        sleep 1
    done
}

# Check system prerequisites
check_prerequisites() {
    log_info "Checking system prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        log_info "Install Python 3: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        log_info "Install Node.js: https://nodejs.org/"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is required but not installed"
        log_info "Install npm: https://www.npmjs.com/get-npm"
        exit 1
    fi
    
    # Check PostgreSQL - Required, not optional
    if ! command -v psql &> /dev/null; then
        log_error "PostgreSQL is required but not installed"
        log_info "Install PostgreSQL: https://www.postgresql.org/download/"
        log_info "Or run: ./setup_postgresql.sh"
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
    
    # Activate virtual environment - handle different shell types
    log_info "Activating virtual environment..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    else
        log_error "Virtual environment activation script not found"
        exit 1
    fi
    
    # Verify virtual environment is active
    if [ -z "$VIRTUAL_ENV" ]; then
        log_error "Failed to activate virtual environment"
        exit 1
    fi
    
    log_success "Virtual environment activated: $VIRTUAL_ENV"
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    
    # Install Node.js dependencies
    log_info "Installing Node.js dependencies..."
    cd frontend
    
    # Handle npm cache issues on WSL/Windows
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || -n "$WSL_DISTRO_NAME" ]]; then
        log_info "Detected WSL/Windows environment, using npm with --force..."
        npm_force_flag="--force"
    else
        npm_force_flag=""
    fi
    
    # Only clean node_modules if there are issues or if --reset-db is specified
    if [ "$RESET_DB" = true ] || [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
        if [ -d "node_modules" ]; then
            log_info "Cleaning existing node_modules..."
            rm -rf node_modules package-lock.json
        fi
        
        # Clear npm cache with error handling
        log_info "Clearing npm cache..."
        npm cache clean --force 2>/dev/null || log_warning "npm cache clean failed, continuing..."
        
        # Install dependencies with retry logic
        local npm_retries=3
        local npm_success=false
        
        for ((i=1; i<=npm_retries; i++)); do
            log_info "Installing Node.js dependencies (attempt $i/$npm_retries)..."
            if npm install $npm_force_flag; then
                npm_success=true
                break
            else
                log_warning "npm install failed (attempt $i/$npm_retries)"
                if [ $i -lt $npm_retries ]; then
                    log_info "Cleaning and retrying..."
                    rm -rf node_modules package-lock.json
                    npm cache clean --force 2>/dev/null || true
                    sleep 2
                fi
            fi
        done
        
        if [ "$npm_success" = false ]; then
            log_error "Failed to install Node.js dependencies after $npm_retries attempts"
            log_info "Try manually: cd frontend && npm install --force"
            exit 1
        fi
    else
        log_info "Node.js dependencies already installed, skipping..."
    fi
    
    # Ensure Puppeteer is available for testing
    if ! npm list puppeteer > /dev/null 2>&1; then
        log_info "Installing Puppeteer for automated testing..."
        npm install puppeteer $npm_force_flag
    fi
    
    cd ..
    
    # Setup database
    setup_database
    
    log_success "Environment setup completed"
}

# Setup database
setup_database() {
    log_info "Setting up database..."
    
    # Check if PostgreSQL is available
    if ! command -v psql &> /dev/null; then
        log_error "PostgreSQL not available. This script cannot function without PostgreSQL."
        exit 1
    fi
    
    # Start PostgreSQL service based on OS
    if command -v brew &> /dev/null; then
        # macOS
        log_info "Starting PostgreSQL on macOS..."
        brew services start postgresql@14 2>/dev/null || brew services start postgresql 2>/dev/null || true
    elif command -v systemctl &> /dev/null; then
        # Linux with systemd
        log_info "Starting PostgreSQL on Linux..."
        sudo systemctl start postgresql 2>/dev/null || sudo systemctl start postgresql@14 2>/dev/null || true
    elif command -v service &> /dev/null; then
        # Linux with service command
        log_info "Starting PostgreSQL with service command..."
        sudo service postgresql start 2>/dev/null || true
    else
        log_warning "Could not start PostgreSQL service automatically"
        log_info "Please ensure PostgreSQL is running manually"
    fi
    
    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    local pg_attempts=0
    while [ $pg_attempts -lt 30 ]; do
        if pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U postgres > /dev/null 2>&1; then
            log_success "PostgreSQL is ready!"
            break
        fi
        sleep 1
        pg_attempts=$((pg_attempts + 1))
    done
    
    if [ $pg_attempts -eq 30 ]; then
        log_error "PostgreSQL not ready after 30 seconds. Exiting."
        exit 1
    fi
    
    # Create database and user
    log_info "Creating database and user..."
    
    # Create user if it doesn't exist
    psql -U postgres -c "CREATE USER $DATABASE_USER WITH PASSWORD '$DATABASE_PASSWORD';" 2>/dev/null || true
    
    # Create database if it doesn't exist
    psql -U postgres -c "CREATE DATABASE $DATABASE_NAME OWNER $DATABASE_USER;" 2>/dev/null || true
    
    # Grant privileges
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $DATABASE_USER;" 2>/dev/null || true
    psql -U postgres -c "ALTER USER $DATABASE_USER CREATEDB;" 2>/dev/null || true
    
    # Set DATABASE_URL environment variable
    export DATABASE_URL="postgresql://$DATABASE_USER:$DATABASE_PASSWORD@$DATABASE_HOST:$DATABASE_PORT/$DATABASE_NAME"
    log_info "DATABASE_URL set to: $DATABASE_URL"
    
    # Run database migration for enhanced logging
    log_info "Running database migration for enhanced logging..."
    cd backend
    if python db_migration.py; then
        log_success "Database migration completed successfully"
    else
        log_warning "Database migration failed, but continuing..."
    fi
    cd ..
    
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
    local pid=$(lsof -ti:$port 2>/dev/null || ss -tulpn 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1)
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
    
    log_info "Initializing in-memory compilation for frontend assets..."
    
    # Memorial message during compilation
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}                 In memory of Mehmet Ugurlu and Yusuf Alpdogan${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Start frontend in background
    if [ "$VERBOSE" = true ]; then
        log_info "Starting Vite dev server..."
        npm run dev &
    else
        log_info "Starting Vite dev server..."
        npm run dev > /dev/null 2>&1 &
    fi
    
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    log_info "Waiting for frontend to start..."
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            log_success "Frontend compilation completed and server is healthy!"
            log_success "In-memory assets are ready and being served"
            break
        fi
        sleep 1
        attempts=$((attempts + 1))
        
        # Show progress every 5 seconds
        if [ $((attempts % 5)) -eq 0 ]; then
            log_info "Still compiling... (${attempts}s elapsed)"
        fi
    done
    
    if [ $attempts -eq 30 ]; then
        log_error "Frontend compilation failed or timed out after 30 seconds"
        exit 1
    fi
}

# Run comprehensive tests
run_tests() {
    log_info "Running comprehensive test suite..."
    
    # Wait a bit for services to fully initialize
    sleep 5
    
    # Run backend authentication tests
    log_info "Running comprehensive authentication tests..."
    cd backend
    if python test_auth_comprehensive.py; then
        log_success "Authentication tests passed!"
    else
        log_warning "Some authentication tests failed. Check the output above for details."
    fi
    cd ..
    
    # Run logging system tests
    log_info "Running logging system tests..."
    cd backend
    if python test_logging.py; then
        log_success "Logging system tests passed!"
    else
        log_warning "Some logging tests failed. Check the output above for details."
    fi
    cd ..
    
    # Check if frontend tests directory exists
    if [ -d "tests" ]; then
        log_info "Running frontend tests..."
        if node tests/run_all_tests.js; then
            log_success "Frontend tests passed!"
        else
            log_warning "Some frontend tests failed. Check the output above for details."
        fi
    else
        log_info "Frontend tests directory not found. Skipping frontend tests."
    fi
    
    log_success "Test suite completed!"
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