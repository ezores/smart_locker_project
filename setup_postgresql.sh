#!/bin/bash

# Smart Locker System - PostgreSQL Setup Script
# This script helps install and configure PostgreSQL for the Smart Locker project

set -e

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

print_header() {
    echo "========================================"
    echo "$1"
    echo "========================================"
}

# Default configuration
DB_NAME="smart_locker"
DB_USER="postgres"
DB_PASSWORD="postgres"

print_header "PostgreSQL Setup for Smart Locker System"

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

print_info "Detected OS: $OS"

# Check if PostgreSQL is already installed
if command -v psql &> /dev/null; then
    print_success "PostgreSQL client is already installed"
else
    print_info "PostgreSQL client not found. Installing..."
    
    if [ "$OS" = "macos" ]; then
        if command -v brew &> /dev/null; then
            print_info "Installing PostgreSQL using Homebrew..."
            brew install postgresql
            brew services start postgresql
        else
            print_error "Homebrew not found. Please install Homebrew first:"
            echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [ "$OS" = "linux" ]; then
        print_info "Installing PostgreSQL using apt..."
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-contrib
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    fi
fi

# Check if PostgreSQL service is running
print_info "Checking PostgreSQL service status..."

if [ "$OS" = "macos" ]; then
    if brew services list | grep postgresql | grep started > /dev/null; then
        print_success "PostgreSQL service is running"
    else
        print_info "Starting PostgreSQL service..."
        brew services start postgresql
    fi
elif [ "$OS" = "linux" ]; then
    if sudo systemctl is-active --quiet postgresql; then
        print_success "PostgreSQL service is running"
    else
        print_info "Starting PostgreSQL service..."
        sudo systemctl start postgresql
    fi
fi

# Create database and user
print_info "Setting up database and user..."

# Try to connect to PostgreSQL and create database
if PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "PostgreSQL connection successful"
else
    print_warning "Could not connect with default credentials. You may need to:"
    echo "1. Set a password for the postgres user:"
    echo "   sudo -u postgres psql"
    echo "   ALTER USER postgres PASSWORD 'postgres';"
    echo "   \\q"
    echo ""
    echo "2. Or create a new user:"
    echo "   sudo -u postgres createuser --interactive"
    echo ""
    echo "3. Or modify the database configuration in start.sh"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

# Try to create database
print_info "Creating database '$DB_NAME'..."
if PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null; then
    print_success "Database '$DB_NAME' created successfully"
elif PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "Database '$DB_NAME' already exists"
else
    print_warning "Could not create database. You may need to create it manually:"
    echo "  createdb $DB_NAME"
    echo "  or"
    echo "  sudo -u postgres createdb $DB_NAME"
fi

# Test database connection
print_info "Testing database connection..."
if PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1; then
    print_success "Database connection test successful"
else
    print_error "Database connection test failed"
    echo "Please check your PostgreSQL configuration and try again."
    exit 1
fi

print_header "PostgreSQL Setup Complete!"

echo "Database Configuration:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "You can now run the Smart Locker system with:"
echo "  ./start.sh --dev --demo --verbose"
echo ""
echo "Or test the database connection with:"
echo "  PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME" 