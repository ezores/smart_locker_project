#!/bin/bash

# PostgreSQL Setup Script for Smart Locker System
# Author: Alp Alpdogan
# In memory of Mehmet Ugurlu and Yusuf Alpdogan

set -e

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

# Configuration
DATABASE_NAME="smart_locker_db"
DATABASE_USER="smart_locker_user"
DATABASE_PASSWORD="smartlockerpass123"

log_info "PostgreSQL Setup for Smart Locker System"
log_info "========================================"
log_info "PostgreSQL is REQUIRED for the Smart Locker System to function properly."
log_info "This script will install and configure PostgreSQL automatically."

# Detect OS and install PostgreSQL
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        log_info "Detected Debian/Ubuntu system"
        log_info "Installing PostgreSQL..."
        
        # Update package list
        sudo apt-get update
        
        # Install PostgreSQL
        sudo apt-get install -y postgresql postgresql-contrib
        
        # Start PostgreSQL service
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL/Fedora
        log_info "Detected CentOS/RHEL/Fedora system"
        log_info "Installing PostgreSQL..."
        
        # Install PostgreSQL
        sudo yum install -y postgresql postgresql-server postgresql-contrib
        
        # Initialize database
        sudo postgresql-setup initdb
        
        # Start PostgreSQL service
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        
    elif command -v dnf &> /dev/null; then
        # Fedora (newer versions)
        log_info "Detected Fedora system"
        log_info "Installing PostgreSQL..."
        
        # Install PostgreSQL
        sudo dnf install -y postgresql postgresql-server postgresql-contrib
        
        # Initialize database
        sudo postgresql-setup initdb
        
        # Start PostgreSQL service
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        
    else
        log_error "Unsupported Linux distribution"
        log_info "Please install PostgreSQL manually: https://www.postgresql.org/download/linux/"
        exit 1
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    log_info "Detected macOS system"
    
    if command -v brew &> /dev/null; then
        log_info "Installing PostgreSQL via Homebrew..."
        brew install postgresql@14
        
        # Start PostgreSQL service
        brew services start postgresql@14
        
        # Add to PATH
        echo 'export PATH="/usr/local/opt/postgresql@14/bin:$PATH"' >> ~/.zshrc
        echo 'export PATH="/usr/local/opt/postgresql@14/bin:$PATH"' >> ~/.bash_profile
        export PATH="/usr/local/opt/postgresql@14/bin:$PATH"
        
    else
        log_error "Homebrew not found"
        log_info "Please install Homebrew first: https://brew.sh/"
        log_info "Or install PostgreSQL manually: https://www.postgresql.org/download/macosx/"
        exit 1
    fi
    
else
    log_error "Unsupported operating system: $OSTYPE"
    log_info "Please install PostgreSQL manually: https://www.postgresql.org/download/"
    exit 1
fi

# Wait for PostgreSQL to be ready
log_info "Waiting for PostgreSQL to be ready..."
local pg_attempts=0
while [ $pg_attempts -lt 30 ]; do
    if pg_isready -h localhost -p 5432 -U postgres > /dev/null 2>&1; then
        log_success "PostgreSQL is ready!"
        break
    fi
    sleep 1
    pg_attempts=$((pg_attempts + 1))
done

if [ $pg_attempts -eq 30 ]; then
    log_error "PostgreSQL failed to start within 30 seconds"
    exit 1
fi

# Create database user and database
log_info "Setting up database and user..."

# Switch to postgres user to create database and user
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - use sudo -u postgres
    sudo -u postgres psql -c "CREATE USER $DATABASE_USER WITH PASSWORD '$DATABASE_PASSWORD';" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE DATABASE $DATABASE_NAME OWNER $DATABASE_USER;" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $DATABASE_USER;" 2>/dev/null || true
    sudo -u postgres psql -c "ALTER USER $DATABASE_USER CREATEDB;" 2>/dev/null || true
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - postgres user might not exist, use current user
    psql -U postgres -c "CREATE USER $DATABASE_USER WITH PASSWORD '$DATABASE_PASSWORD';" 2>/dev/null || true
    psql -U postgres -c "CREATE DATABASE $DATABASE_NAME OWNER $DATABASE_USER;" 2>/dev/null || true
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $DATABASE_USER;" 2>/dev/null || true
    psql -U postgres -c "ALTER USER $DATABASE_USER CREATEDB;" 2>/dev/null || true
fi

log_success "PostgreSQL setup completed!"
log_info "Database: $DATABASE_NAME"
log_info "User: $DATABASE_USER"
log_info "Password: $DATABASE_PASSWORD"
log_info "Connection URL: postgresql://$DATABASE_USER:$DATABASE_PASSWORD@localhost:5432/$DATABASE_NAME"

# Test connection
log_info "Testing database connection..."
if psql -h localhost -U $DATABASE_USER -d $DATABASE_NAME -c "SELECT version();" > /dev/null 2>&1; then
    log_success "Database connection test successful!"
else
    log_warning "Database connection test failed. You may need to configure pg_hba.conf"
    log_info "For development, you can edit pg_hba.conf to allow local connections:"
    log_info "  local   all             all                                     trust"
fi

log_success "PostgreSQL is now ready for use with the Smart Locker System!"
log_info "PostgreSQL is REQUIRED - the system will not function without it."
log_info "Run './start.sh --demo --reset-db --verbose' to start the system." 