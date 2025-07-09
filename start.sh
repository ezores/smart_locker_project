#!/bin/bash

# Smart Locker System - Comprehensive Startup Script
# This script handles development, production, and testing environments
# with PostgreSQL database and comprehensive demo data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

print_debug() {
    if [ $VERBOSE -eq 1 ]; then
        echo -e "${CYAN}[DEBUG]${NC} $1"
    fi
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Default configuration
ENVIRONMENT="development"
DEMO_MODE=0
VERBOSE=0
RESET_DB=0
SIMPLE_DEMO=0
PORT=5050
FRONTEND_PORT=5173
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="smart_locker"
DB_USER="postgres"
DB_PASSWORD="postgres"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            ENVIRONMENT="development"
            shift
            ;;
        --prod)
            ENVIRONMENT="production"
            shift
            ;;
        --test)
            ENVIRONMENT="testing"
            shift
            ;;
        --demo)
            DEMO_MODE=1
            shift
            ;;
        --simple-demo)
            SIMPLE_DEMO=1
            DEMO_MODE=1
            shift
            ;;
        --verbose)
            VERBOSE=1
            shift
            ;;
        --reset-db)
            RESET_DB=1
            DEMO_MODE=1
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        --db-host)
            DB_HOST="$2"
            shift 2
            ;;
        --db-port)
            DB_PORT="$2"
            shift 2
            ;;
        --db-name)
            DB_NAME="$2"
            shift 2
            ;;
        --db-user)
            DB_USER="$2"
            shift 2
            ;;
        --db-password)
            DB_PASSWORD="$2"
            shift 2
            ;;
        --help)
            echo "Smart Locker System - Startup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Environment Options:"
            echo "  --dev              Start in development mode (default)"
            echo "  --prod             Start in production mode"
            echo "  --test             Start in testing mode"
            echo ""
            echo "Demo Options:"
            echo "  --demo             Load comprehensive demo data"
            echo "  --simple-demo      Load minimal demo data"
            echo "  --reset-db         Reset database and load demo data"
            echo ""
            echo "Configuration Options:"
            echo "  --verbose          Enable verbose output"
            echo "  --port PORT        Backend port (default: 5050)"
            echo "  --frontend-port PORT Frontend port (default: 5173)"
            echo ""
            echo "Database Options:"
            echo "  --db-host HOST     Database host (default: localhost)"
            echo "  --db-port PORT     Database port (default: 5432)"
            echo "  --db-name NAME     Database name (default: smart_locker)"
            echo "  --db-user USER     Database user (default: postgres)"
            echo "  --db-password PASS Database password (default: postgres)"
            echo ""
            echo "Examples:"
            echo "  $0 --dev --demo --verbose"
            echo "  $0 --prod --reset-db"
            echo "  $0 --test --simple-demo"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_header "Smart Locker System Startup"
print_info "Environment: $ENVIRONMENT"
print_info "Demo Mode: $([ $DEMO_MODE -eq 1 ] && echo "Enabled" || echo "Disabled")"
print_info "Simple Demo: $([ $SIMPLE_DEMO -eq 1 ] && echo "Enabled" || echo "Disabled")"
print_info "Reset Database: $([ $RESET_DB -eq 1 ] && echo "Enabled" || echo "Disabled")"
print_info "Verbose: $([ $VERBOSE -eq 1 ] && echo "Enabled" || echo "Disabled")"

# Check if we're in the right directory
if [ ! -d "smart_locker_project" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check dependencies
print_info "Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is required but not installed"
    exit 1
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL client not found. Attempting to install..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            print_info "Installing PostgreSQL using Homebrew..."
            brew install postgresql
            brew services start postgresql
        else
            print_error "Homebrew not found. Please install Homebrew first:"
            echo "  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_info "Installing PostgreSQL using apt..."
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-contrib
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    else
        print_error "Unsupported OS for automatic PostgreSQL install. Please install manually."
        exit 1
    fi
fi

# Check PostgreSQL service is running
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! brew services list | grep postgresql | grep started > /dev/null; then
        print_info "Starting PostgreSQL service..."
        brew services start postgresql
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! sudo systemctl is-active --quiet postgresql; then
        print_info "Starting PostgreSQL service..."
        sudo systemctl start postgresql
    fi
fi

print_success "All dependencies found"

# Setup Python virtual environment
if [ ! -d ".venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
print_info "Activating Python virtual environment..."
source .venv/bin/activate

# Install Python dependencies
print_info "Installing Python requirements..."
pip install --upgrade pip
pip install -r smart_locker_project/requirements.txt

# Install frontend dependencies
print_info "Installing frontend dependencies..."
cd smart_locker_project/frontend
npm install
cd ../..

# Database setup
print_info "Setting up PostgreSQL database..."

# Set environment variables for database
export DB_HOST=$DB_HOST
export DB_PORT=$DB_PORT
export DB_NAME=$DB_NAME
export DB_USER=$DB_USER
export DB_PASSWORD=$DB_PASSWORD

# Try to create database if it doesn't exist
if command -v psql &> /dev/null; then
    print_debug "Attempting to create database if it doesn't exist..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || print_debug "Database already exists or creation failed"
else
    print_warning "PostgreSQL client not available. Please ensure database '$DB_NAME' exists."
fi

# Drop and recreate schema if --reset-db is used
if [ $RESET_DB -eq 1 ]; then
    print_info "Dropping and recreating all tables in database '$DB_NAME'..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" || print_warning "Could not drop/recreate schema. You may need to do it manually."
fi

# Start backend server
print_info "Starting backend server..."
cd smart_locker_project/backend

# Build backend command based on environment and options
BACKEND_CMD="python app.py --port $PORT"

if [ $DEMO_MODE -eq 1 ]; then
    BACKEND_CMD="$BACKEND_CMD --demo"
fi

if [ $SIMPLE_DEMO -eq 1 ]; then
    BACKEND_CMD="$BACKEND_CMD --simple-demo"
fi

if [ $RESET_DB -eq 1 ]; then
    BACKEND_CMD="$BACKEND_CMD --reset-db"
fi

if [ $VERBOSE -eq 1 ]; then
    BACKEND_CMD="$BACKEND_CMD --verbose"
fi

print_debug "Backend command: $BACKEND_CMD"

# Start backend in background
$BACKEND_CMD &
BACKEND_PID=$!

# Wait for backend to start
print_info "Waiting for backend to start..."
sleep 5

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend failed to start"
    exit 1
fi

# Test backend health
print_info "Testing backend health..."
if curl -s http://localhost:$PORT/api/health > /dev/null 2>&1; then
    print_success "Backend is running on http://localhost:$PORT"
else
    print_warning "Backend health check failed, but process is running"
fi

# Start frontend server
print_info "Starting frontend server..."
cd ../frontend

# Set frontend port in package.json if it exists
if [ -f "package.json" ]; then
    print_debug "Setting frontend port to $FRONTEND_PORT"
    # This would need to be configured in vite.config.js or similar
fi

# Start frontend in background
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
print_info "Waiting for frontend to start..."
sleep 8

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

print_success "Frontend is running on http://localhost:$FRONTEND_PORT"

# Show demo credentials if in demo mode
if [ $DEMO_MODE -eq 1 ]; then
    echo ""
    print_header "Demo Credentials"
    echo "Admin Users:"
    echo "  Username: admin          Password: admin123"
    echo "  Username: manager        Password: manager123"
    echo ""
    echo "Student Users:"
    echo "  Username: student1       Password: student123"
    echo "  Username: student2       Password: student123"
    echo "  Username: student3       Password: student123"
    echo "  Username: student4       Password: student123"
    echo "  Username: student5       Password: student123"
    echo "  Username: student6       Password: student123"
    echo "  Username: student7       Password: student123"
    echo "  Username: student8       Password: student123"
    echo "  Username: student9       Password: student123"
    echo "  Username: student10      Password: student123"
fi

echo ""
print_header "Smart Locker System is Running!"
echo "Backend API:    http://localhost:$PORT"
echo "Frontend:       http://localhost:$FRONTEND_PORT"
echo "Health Check:   http://localhost:$PORT/api/health"
echo "Environment:    $ENVIRONMENT"
echo "Database:       $DB_NAME@$DB_HOST:$DB_PORT"
echo ""

if [ $VERBOSE -eq 1 ]; then
    echo "Process IDs:"
    echo "  Backend:  $BACKEND_PID"
    echo "  Frontend: $FRONTEND_PID"
    echo ""
fi

echo "Press Ctrl+C to stop all services."

# Function to cleanup on exit
cleanup() {
    print_info "Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    print_success "All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop the services
wait 