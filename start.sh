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

# Function to print output
print_success() {
    echo "[SUCCESS] $1"
}

print_error() {
    echo "[ERROR] $1"
}

print_warning() {
    echo "[WARNING] $1"
}

print_info() {
    echo "[INFO] $1"
}

# Create .env file if it doesn't exist with database configuration
if [ ! -f ".env" ]; then
    print_info "Creating .env file with database configuration..."
    cat > .env << EOF
# Database Configuration
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASS=$DB_PASS
DB_PORT=$DB_PORT
DB_HOST=$DB_HOST
DATABASE_URL=$DATABASE_URL

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
EOF
    print_success "Created .env file with default configuration"
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Dependency checks
missing_deps=()
for dep in python3 pip3 node npm psql; do
    if ! command_exists $dep; then
        missing_deps+=("$dep")
    fi
    done
if [ ${#missing_deps[@]} -ne 0 ]; then
    print_error "Missing dependencies: ${missing_deps[*]}"
    echo "Please install the missing dependencies before running this script."
    echo "Python: https://www.python.org/downloads/"
    echo "Node.js: https://nodejs.org/en/download/"
    echo "PostgreSQL: https://www.postgresql.org/download/"
    exit 1
fi

# Check for tmux (optional, only warn)
if ! command_exists tmux; then
    print_warning "tmux not found. For best experience, install tmux: https://github.com/tmux/tmux/wiki"
fi

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

# Function to start backend
start_backend() {
    print_info "Starting backend server..."
    export DATABASE_URL="$DATABASE_URL"
    export FLASK_ENV=development
    pushd backend > /dev/null
    source ../.venv/bin/activate
    pkill -f "python.*app.py" 2>/dev/null || true
    sleep 2
    
    # Build backend command with appropriate flags
    BACKEND_CMD="python app.py --port 5172 --verbose"
    if [ "$DEMO_MODE" = true ]; then
        BACKEND_CMD="$BACKEND_CMD --demo"
    fi
    if [ "$RESET_DB" = true ]; then
        BACKEND_CMD="$BACKEND_CMD --reset-db"
    fi
    if [ "$MINIMAL" = true ]; then
        BACKEND_CMD="$BACKEND_CMD --minimal"
    fi
    
    $BACKEND_CMD &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    popd > /dev/null
    print_info "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5172/api/health >/dev/null 2>&1; then
            print_success "Backend is healthy!"
            return 0
        fi
        sleep 1
    done
    print_error "Backend failed to start. Check backend/app.py logs for details."
    echo "Troubleshooting tips:"
    echo "- Ensure PostgreSQL is running and accessible."
    echo "- Check DATABASE_URL in .env or script."
    echo "- Run 'psql $DATABASE_URL' to test DB connection."
    return 1
}

# Function to start frontend
start_frontend() {
    print_info "Starting frontend server..."
    pkill -f "node.*vite" 2>/dev/null || true
    sleep 2
    if [ ! -d "frontend" ]; then
        print_error "frontend directory not found!"
        exit 1
    fi
    pushd frontend > /dev/null
    npm install
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    popd > /dev/null
    print_info "Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 >/dev/null 2>&1; then
            print_success "Frontend is healthy!"
            return 0
        fi
        sleep 1
    done
    print_error "Frontend failed to start. Check frontend logs for details."
    echo "Troubleshooting tips:"
    echo "- Ensure Node.js and npm are installed."
    echo "- Try running 'npm install' and 'npm run dev' in the frontend directory manually."
    return 1
}

# Function to run comprehensive tests
run_tests() {
    print_info "Running comprehensive system tests..."
    
    # Test 1: Backend API health check
    print_info "Test 1: Backend API health check"
    if curl -s http://localhost:5172/api/health | grep -q "healthy"; then
        print_success "Backend API is healthy"
    else
        print_error "Backend API health check failed"
        return 1
    fi
    
    # Test 2: Database connection
    print_info "Test 2: Database connection test"
    if python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('$DATABASE_URL')
    conn.close()
    print('Database connection successful!')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"; then
        print_success "Database connection test passed"
    else
        print_error "Database connection test failed"
        return 1
    fi
    
    # Test 3: Frontend accessibility
    print_info "Test 3: Frontend accessibility test"
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend accessibility test failed"
        return 1
    fi
    
    # Test 4: Authentication endpoints
    print_info "Test 4: Authentication endpoints test"
    if curl -s -X POST http://localhost:5172/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin123"}' | grep -q "token"; then
        print_success "Authentication endpoints working"
    else
        print_error "Authentication endpoints test failed"
        return 1
    fi
    
    # Test 5: Reservations API
    print_info "Test 5: Reservations API test"
    if curl -s http://localhost:5172/api/reservations >/dev/null 2>&1; then
        print_success "Reservations API is accessible"
    else
        print_error "Reservations API test failed"
        return 1
    fi
    
    # Test 6: Run Python test script
    print_info "Test 6: Running Python test script"
    if [ -f "test_reservations.py" ]; then
        if python3 test_reservations.py; then
            print_success "Python test script passed"
        else
            print_error "Python test script failed"
            return 1
        fi
    else
        print_warning "test_reservations.py not found, skipping"
    fi
    
    print_success "All tests completed successfully!"
    return 0
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
trap cleanup EXIT

# Main execution
echo "[INFO] Smart Locker System - Automated Setup and Testing"
echo "=================================================="

# Parse arguments
TEST_MODE=false
DEMO_MODE=false
VERBOSE=false
RESET_DB=false
MINIMAL=false
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
        --reset-db)
            RESET_DB=true
            shift
            ;;
        --minimal)
            MINIMAL=true
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
    print('Attempting to create database and user...')
    exit(1)
" || {
    print_warning "Database connection failed, attempting to create database..."
    
    # Try to create database and user with postgres superuser
    if psql -U postgres -h localhost -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>/dev/null; then
        print_success "Created database user: $DB_USER"
    else
        print_info "Database user already exists or creation failed"
    fi
    
    if psql -U postgres -h localhost -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null; then
        print_success "Created database: $DB_NAME"
    else
        print_info "Database already exists or creation failed"
    fi
    
    # Test connection again
    if python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('$DATABASE_URL')
    conn.close()
    print('Database connection successful after setup!')
except Exception as e:
    print(f'Database connection still failed: {e}')
    exit(1)
"; then
        print_success "Database connection test passed after setup!"
    else
        print_error "Database connection test failed even after setup"
        print_error "Please check PostgreSQL installation and configuration"
        exit 1
    fi
}

# Install Node.js dependencies
print_info "Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Kill any existing processes
kill_port_processes 5172
kill_port_processes 5173

if [ "$TEST_MODE" = true ]; then
    print_info "Starting servers for testing..."
    if start_backend && start_frontend; then
        print_success "Both servers started successfully"
        
        # Wait a bit for servers to fully initialize
        sleep 5
        
        # Run comprehensive tests
        if run_tests; then
            print_success "All tests passed! System is working correctly."
            print_info "Backend running on http://localhost:5172"
            print_info "Frontend running on http://localhost:5173"
            print_info "Demo credentials:"
            print_info "  Admin: admin/admin123"
            print_info "  Student: student1/student123"
            print_info "  Manager: manager/manager123"
            print_info "  Supervisor: supervisor/supervisor123"
        else
            print_error "Some tests failed. Check the logs above for details."
            exit 1
        fi
    else
        print_error "Failed to start servers for testing"
        exit 1
    fi
else
    print_info "Starting servers in normal mode..."
    if start_backend && start_frontend; then
        print_success "Both servers started successfully!"
        print_info "Backend running on http://localhost:5172"
        print_info "Frontend running on http://localhost:5173"
        print_info "Press Ctrl+C to stop all servers"
        wait
    else
        print_error "Failed to start servers"
        exit 1
    fi
fi 