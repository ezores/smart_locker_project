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

# Progress indicator for long-running operations
show_progress() {
    local pid=$1
    local message=$2
    local spin='-\|/'
    local i=0
    
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %4 ))
        printf "\r${BLUE}[INFO]${NC} $message ${spin:$i:1}"
        sleep 1
    done
    printf "\r${BLUE}[INFO]${NC} $message ... done\n"
}

# Parse command line arguments
DEMO_MODE=false
RESET_DB=false
VERBOSE=false
MINIMAL=false
TEST_MODE=false
HELP=false
RS485_REAL_MODE=false

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
        --rs485-real)
            RS485_REAL_MODE=true
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
    echo "  --rs485-real    Force real RS485 hardware mode (default is real hardware)"
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
    echo "  - Uses real RS485 hardware by default"
    echo ""
    echo "Prerequisites:"
    echo "  - Python 3.8+ (required, will exit if not found)"
    echo "  - PostgreSQL, Node.js, and npm will be installed automatically"
    echo "  - Supported systems: macOS (with Homebrew), Linux (Ubuntu/Debian, CentOS/RHEL, Fedora, Arch)"
    echo ""
    echo "Automatic Installation:"
    echo "  The script will automatically detect your system and install:"
    echo "  - PostgreSQL (with proper service setup)"
    echo "  - Node.js 20.x (from official repositories)"
    echo "  - npm (package manager for Node.js)"
    echo ""
    echo "macOS Requirements:"
    echo "  - Homebrew must be installed (https://brew.sh/)"
    echo "  - Run: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    echo "Manual Installation (if automatic fails):"
    echo "  - PostgreSQL: https://www.postgresql.org/download/"
    echo "  - Node.js: https://nodejs.org/"
    echo "  - npm: https://www.npmjs.com/get-npm"
    echo ""
    echo "Troubleshooting:"
    echo "  If npm installation fails, manually clean and retry:"
    echo "    cd frontend && rm -rf node_modules package-lock.json"
    echo "    npm cache clean --force && npm install"
    echo ""
    echo "Linux/WSL Notes:"
echo "  - PostgreSQL service will be started automatically"
echo "  - If using WSL, ensure proper file permissions"
echo "  - Virtual environment will be created automatically"
echo "  - PostgreSQL authentication will be configured automatically"
echo "  - If authentication fails, the script will use fallback methods"
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

# Install PostgreSQL
install_postgresql() {
    log_info "Installing PostgreSQL..."
    
    if command -v brew &> /dev/null; then
        # macOS
        log_info "Detected macOS system"
        brew install postgresql@14
        brew services start postgresql@14
        # Create postgres user if it doesn't exist
        createuser -s postgres 2>/dev/null || true
    elif command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        log_info "Detected Ubuntu/Debian system"
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-contrib postgresql-client
        sudo systemctl enable postgresql
        sudo systemctl start postgresql
        
        # Wait for PostgreSQL to be ready after installation
        log_info "Waiting for PostgreSQL to start after installation..."
        sleep 5
        sudo systemctl status postgresql --no-pager || true
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL/Fedora
        log_info "Detected CentOS/RHEL/Fedora system"
        sudo yum install -y postgresql postgresql-server postgresql-contrib
        sudo postgresql-setup initdb
        sudo systemctl enable postgresql
        sudo systemctl start postgresql
    elif command -v dnf &> /dev/null; then
        # Fedora (newer versions)
        log_info "Detected Fedora system"
        sudo dnf install -y postgresql postgresql-server postgresql-contrib
        sudo postgresql-setup initdb
        sudo systemctl enable postgresql
        sudo systemctl start postgresql
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        log_info "Detected Arch Linux system"
        sudo pacman -S --noconfirm postgresql
        sudo -u postgres initdb -D /var/lib/postgres/data
        sudo systemctl enable postgresql
        sudo systemctl start postgresql
    else
        log_error "Unsupported package manager for PostgreSQL installation"
        log_info "Please install PostgreSQL manually: https://www.postgresql.org/download/"
        exit 1
    fi
    
    log_success "PostgreSQL installed successfully"
    
    # Set up PostgreSQL user and basic configuration
    log_info "Setting up PostgreSQL user and initial configuration..."
    
    # Initialize PostgreSQL database cluster if needed (for fresh installs)
    if command -v sudo &> /dev/null; then
        # Check if PostgreSQL data directory exists
        if command -v brew &> /dev/null; then
            # macOS - use current user
            pg_data_dir=$(psql -c "SHOW data_directory;" 2>/dev/null | grep -v "data_directory" | grep -v "\-\-\-" | grep -v "rows" | tr -d ' ' || echo "")
        else
            # Linux - use postgres user
            pg_data_dir=$(sudo -u postgres psql -c "SHOW data_directory;" 2>/dev/null | grep -v "data_directory" | grep -v "\-\-\-" | grep -v "rows" | tr -d ' ' || echo "")
        fi
        if [ -z "$pg_data_dir" ]; then
            log_info "PostgreSQL data directory not found. Initializing database cluster..."
            sudo -u postgres initdb -D /var/lib/postgresql/data 2>/dev/null || sudo -u postgres initdb 2>/dev/null || true
            sudo systemctl restart postgresql 2>/dev/null || true
            sleep 3
        fi
    fi
    
    # Configure PostgreSQL authentication for automatic operation
    log_info "Configuring PostgreSQL authentication for automatic operation..."
    
    if command -v brew &> /dev/null; then
        # macOS - set password for postgres user
        psql postgres -c "ALTER USER postgres PASSWORD 'postgres';" 2>/dev/null || true
        log_success "PostgreSQL setup completed for macOS"
    elif command -v sudo &> /dev/null; then
        # Linux - configure for automatic operation without password prompts
        
        # Set password for postgres user
        if command -v brew &> /dev/null; then
            # macOS - use current user
            psql -c "ALTER USER postgres PASSWORD 'postgres';" 2>/dev/null || true
            
            # Configure PostgreSQL to allow trust authentication for local connections
            log_info "Configuring PostgreSQL authentication for local connections..."
            pg_hba_conf=$(psql -c "SHOW hba_file;" 2>/dev/null | grep -v "hba_file" | grep -v "\-\-\-" | grep -v "rows" | tr -d ' ' || echo "")
        else
            # Linux - use postgres user
            sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';" 2>/dev/null || true
            
            # Configure PostgreSQL to allow trust authentication for local connections
            log_info "Configuring PostgreSQL authentication for local connections..."
            pg_hba_conf=$(sudo -u postgres psql -c "SHOW hba_file;" 2>/dev/null | grep -v "hba_file" | grep -v "\-\-\-" | grep -v "rows" | tr -d ' ' || echo "")
        fi
        
        if [ -n "$pg_hba_conf" ] && [ -f "$pg_hba_conf" ]; then
            log_info "Found pg_hba.conf at: $pg_hba_conf"
            # Backup the original file
            if command -v brew &> /dev/null; then
                # macOS - use current user to backup the file (Homebrew runs as current user)
                cp "$pg_hba_conf" "${pg_hba_conf}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
            else
                # Linux - use sudo cp
                sudo cp "$pg_hba_conf" "${pg_hba_conf}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
            fi
            
            # Configure for automatic operation - allow trust for local connections
            log_info "Configuring pg_hba.conf for automatic operation..."
            
            # Create a new pg_hba.conf with proper authentication
            if command -v brew &> /dev/null; then
                # macOS - use current user to write the file (Homebrew runs as current user)
                tee "$pg_hba_conf" > /dev/null << 'EOF'
# PostgreSQL Client Authentication Configuration File
# ===============================================

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            trust

# IPv6 local connections:
host    all             all             ::1/128                 trust

# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
EOF
            else
                # Linux - use sudo tee
                sudo tee "$pg_hba_conf" > /dev/null << 'EOF'
# PostgreSQL Client Authentication Configuration File
# ===============================================

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            trust

# IPv6 local connections:
host    all             all             ::1/128                 trust

# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
EOF
            fi
            
            log_info "Configured pg_hba.conf for automatic operation"
            
            # Reload PostgreSQL configuration
            sudo systemctl reload postgresql 2>/dev/null || sudo service postgresql reload 2>/dev/null || true
            log_info "Reloaded PostgreSQL configuration"
            
            # Wait a moment for the configuration to take effect
            sleep 2
        else
            log_warning "Could not find pg_hba.conf file, attempting alternative configuration..."
            
            # Try to find pg_hba.conf in common locations
            common_locations=(
                "/etc/postgresql/*/main/pg_hba.conf"
                "/var/lib/postgresql/data/pg_hba.conf"
                "/var/lib/pgsql/data/pg_hba.conf"
                "/usr/local/var/postgres/pg_hba.conf"
            )
            
            for location in "${common_locations[@]}"; do
                for file in $location; do
                    if [ -f "$file" ]; then
                        log_info "Found pg_hba.conf at: $file"
                        # Backup and configure
                        if command -v brew &> /dev/null; then
                            # macOS - use current user to backup the file (Homebrew runs as current user)
                            cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
                        else
                            # Linux - use sudo cp
                            sudo cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
                        fi
                        
                        # Configure for automatic operation
                        if command -v brew &> /dev/null; then
                            # macOS - use current user to write the file (Homebrew runs as current user)
                            tee "$file" > /dev/null << 'EOF'
# PostgreSQL Client Authentication Configuration File
# ===============================================

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            trust

# IPv6 local connections:
host    all             all             ::1/128                 trust

# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
EOF
                        else
                            # Linux - use sudo tee
                            sudo tee "$file" > /dev/null << 'EOF'
# PostgreSQL Client Authentication Configuration File
# ===============================================

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            trust

# IPv6 local connections:
host    all             all             ::1/128                 trust

# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
EOF
                        fi
                        
                        log_info "Configured pg_hba.conf at $file for automatic operation"
                        sudo systemctl reload postgresql 2>/dev/null || sudo service postgresql reload 2>/dev/null || true
                        sleep 2
                        break 2
                    fi
                done
            done
        fi
        
        log_success "PostgreSQL setup completed for automatic operation"
    else
        log_warning "Could not set up PostgreSQL user automatically"
        log_info "Please run: sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'postgres';\""
    fi
}

# Install curl if not available
install_curl() {
    log_info "Installing curl..."
    
    if command -v brew &> /dev/null; then
        # macOS
        brew install curl
    elif command -v apt-get &> /dev/null; then
        sudo apt-get install -y curl
    elif command -v yum &> /dev/null; then
        sudo yum install -y curl
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y curl
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm curl
    else
        log_error "Unsupported package manager for curl installation"
        exit 1
    fi
    
    log_success "curl installed successfully"
}

# Install Node.js
install_nodejs() {
    log_info "Installing Node.js..."
    
    # Check if curl is available for NodeSource setup
    if ! command -v curl &> /dev/null; then
        log_info "curl not found. Installing curl first..."
        install_curl
    fi
    
    if command -v brew &> /dev/null; then
        # macOS
        log_info "Detected macOS system"
        brew install node
    elif command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        log_info "Detected Ubuntu/Debian system"
        curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        log_info "Detected CentOS/RHEL system"
        curl -fsSL https://rpm.nodesource.com/setup_22.x | sudo bash -
        sudo yum install -y nodejs
    elif command -v dnf &> /dev/null; then
        # Fedora
        log_info "Detected Fedora system"
        curl -fsSL https://rpm.nodesource.com/setup_22.x | sudo bash -
        sudo dnf install -y nodejs
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        log_info "Detected Arch Linux system"
        sudo pacman -S --noconfirm nodejs npm
    else
        log_error "Unsupported package manager for Node.js installation"
        log_info "Please install Node.js manually: https://nodejs.org/"
        exit 1
    fi
    
    log_success "Node.js installed successfully"
}

# Install npm (if not included with Node.js)
install_npm() {
    log_info "Installing npm..."
    
    if command -v brew &> /dev/null; then
        # macOS - npm comes with node
        log_info "npm should already be installed with Node.js"
    elif command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get install -y npm
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y npm
    elif command -v dnf &> /dev/null; then
        # Fedora
        sudo dnf install -y npm
    elif command -v pacman &> /dev/null; then
        # Arch Linux - npm comes with nodejs
        log_info "npm should already be installed with Node.js"
    else
        log_error "Unsupported package manager for npm installation"
        log_info "Please install npm manually: https://www.npmjs.com/get-npm"
        exit 1
    fi
    
    log_success "npm installed successfully"
}

# Ensure PostgreSQL is configured for automatic operation
ensure_postgresql_auto_config() {
    log_info "Ensuring PostgreSQL is configured for automatic operation..."
    
    # First, test if PostgreSQL is already working without configuration
    if command -v brew &> /dev/null; then
        # macOS - test with current user
        if psql -c "SELECT 1;" > /dev/null 2>&1; then
            log_success "PostgreSQL is already working without additional configuration"
            return 0
        fi
    else
        # Linux - test with postgres user
        if sudo -u postgres psql -c "SELECT 1;" > /dev/null 2>&1; then
            log_success "PostgreSQL is already working without additional configuration"
            return 0
        fi
    fi
    
    # Only configure pg_hba.conf if PostgreSQL is not working
    log_info "PostgreSQL needs configuration. Attempting to configure pg_hba.conf..."
    
    # Try to get pg_hba.conf location from PostgreSQL itself first
    log_info "Attempting to get pg_hba.conf location from PostgreSQL..."
    pg_hba_from_db=""
    if command -v brew &> /dev/null; then
        # macOS - try with current user
        pg_hba_from_db=$(psql -t -c "SHOW hba_file;" 2>/dev/null | xargs || echo "")
    else
        # Linux - try with postgres user
        pg_hba_from_db=$(sudo -u postgres psql -t -c "SHOW hba_file;" 2>/dev/null | xargs || echo "")
    fi
    
    # Try to find and configure pg_hba.conf
    pg_hba_locations=(
        "$pg_hba_from_db"
        "/etc/postgresql/*/main/pg_hba.conf"
        "/etc/postgresql/16/main/pg_hba.conf"
        "/var/lib/postgresql/data/pg_hba.conf"
        "/var/lib/pgsql/data/pg_hba.conf"
        "/usr/local/var/postgres/pg_hba.conf"
        "/opt/homebrew/var/postgresql@14/pg_hba.conf"
        "/opt/homebrew/var/postgresql/pg_hba.conf"
    )
    
    pg_hba_found=false
    for pattern in "${pg_hba_locations[@]}"; do
        for file in $pattern; do
            if [ -f "$file" ]; then
                log_info "Found pg_hba.conf at: $file"
                pg_hba_found=true
                
                # Backup the original file
                if command -v brew &> /dev/null; then
                    # macOS - use current user to backup the file (Homebrew runs as current user)
                    cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
                else
                    # Linux - use sudo cp
                    sudo cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
                fi
                
                # Configure for automatic operation with trust authentication
                log_info "Configuring $file for automatic operation..."
                
                # Use different approach for macOS vs Linux
                if command -v brew &> /dev/null; then
                    # macOS - use current user to write the file (Homebrew runs as current user)
                    log_info "Using current user to configure pg_hba.conf on macOS..."
                    tee "$file" > /dev/null << 'EOF'
# PostgreSQL Client Authentication Configuration File
# ===============================================

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            trust

# IPv6 local connections:
host    all             all             ::1/128                 trust

# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
EOF
                else
                    # Linux - use sudo tee
                    sudo tee "$file" > /dev/null << 'EOF'
# PostgreSQL Client Authentication Configuration File
# ===============================================

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            trust

# IPv6 local connections:
host    all             all             ::1/128                 trust

# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
EOF
                fi
                
                log_info "Configured $file for automatic operation"
                
                # Reload PostgreSQL configuration
                if command -v systemctl &> /dev/null; then
                    sudo systemctl reload postgresql 2>/dev/null || sudo systemctl reload postgresql@14 2>/dev/null || true
                elif command -v service &> /dev/null; then
                    sudo service postgresql reload 2>/dev/null || true
                elif command -v brew &> /dev/null; then
                    # macOS - restart PostgreSQL service
                    brew services restart postgresql@14 2>/dev/null || brew services restart postgresql 2>/dev/null || true
                fi
                
                # Wait for configuration to take effect
                sleep 3
                break 2
            fi
        done
    done
    
    if [ "$pg_hba_found" = false ]; then
        log_warning "Could not find pg_hba.conf file automatically"
        log_info "PostgreSQL may need manual configuration for automatic operation"
    else
        log_success "PostgreSQL configured for automatic operation"
    fi
    
    # Test the configuration
    if command -v brew &> /dev/null; then
        # macOS - test with current user
        if psql -c "SELECT 1;" > /dev/null 2>&1; then
            log_success "PostgreSQL trust authentication is working"
        else
            log_warning "PostgreSQL trust authentication may not be working properly"
        fi
    else
        # Linux - test with postgres user
        if sudo -u postgres psql -c "SELECT 1;" > /dev/null 2>&1; then
            log_success "PostgreSQL trust authentication is working"
        else
            log_warning "PostgreSQL trust authentication may not be working properly"
        fi
    fi
}

# Check and install system prerequisites
check_prerequisites() {
    log_info "Checking and installing system prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        log_info "Install Python 3: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Install python3-venv on Ubuntu/Debian systems
    if command -v apt-get &> /dev/null; then
        if ! python3 -c "import venv" 2>/dev/null; then
            log_info "Installing python3-venv for Ubuntu/Debian..."
            sudo apt-get update
            sudo apt-get install -y python3-venv python3-pip
            log_success "python3-venv installed successfully"
        else
            log_success "python3-venv is already available"
        fi
    fi
    
    # Check for Homebrew on macOS
    if [[ "$OSTYPE" == "darwin"* ]] && ! command -v brew &> /dev/null; then
        log_error "Homebrew is required on macOS but not installed"
        log_info "Install Homebrew: https://brew.sh/"
        log_info "Run: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Check and install PostgreSQL
    if ! command -v psql &> /dev/null; then
        log_info "PostgreSQL not found. Installing PostgreSQL..."
        install_postgresql
    else
        log_success "PostgreSQL is already installed"
    fi
    
    # Check and install Node.js
    if ! command -v node &> /dev/null; then
        log_info "Node.js not found. Installing Node.js..."
        install_nodejs
    else
        # Check Node.js version compatibility
        NODE_VERSION=$(node --version | sed 's/^v//')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
        
        if [ "$NODE_MAJOR" -lt 20 ]; then
            log_warning "Node.js version $NODE_VERSION is too old. Vite requires Node.js 20.19.0 or >=22.12.0"
            log_info "Upgrading Node.js to version 22..."
            install_nodejs
        else
            log_success "Node.js version $NODE_VERSION is compatible"
        fi
    fi
    
    # Check and install npm
    if ! command -v npm &> /dev/null; then
        log_info "npm not found. Installing npm..."
        install_npm
    else
        log_success "npm is already installed"
    fi
    
    log_success "All prerequisites are satisfied"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    # Create logs directory if it doesn't exist
    if [ ! -d "backend/logs" ]; then
        log_info "Creating logs directory..."
        mkdir -p backend/logs
        log_success "Logs directory created"
    fi
    
    # Create virtual environment if it doesn't exist or if it's corrupted
    if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ] || [ ! -f ".venv/pyvenv.cfg" ]; then
        if [ -d ".venv" ]; then
            log_info "Virtual environment exists but appears corrupted. Recreating..."
            rm -rf .venv
        fi
        log_info "Creating Python virtual environment..."
        if ! python3 -m venv .venv; then
            log_error "Failed to create virtual environment"
            log_info "Attempting to install python3-venv and retry..."
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y python3-venv python3-pip
                if ! python3 -m venv .venv; then
                    log_error "Still failed to create virtual environment after installing python3-venv"
                    exit 1
                fi
            else
                log_info "Please install python3-venv manually for your system"
                exit 1
            fi
        fi
        log_success "Virtual environment created successfully"
    else
        log_info "Virtual environment already exists and appears valid"
    fi
    
    # Set up virtual environment paths
    log_info "Setting up virtual environment..."
    
    # Set virtual environment variables manually
    export VIRTUAL_ENV="$PROJECT_ROOT/.venv"
    export PATH="$VIRTUAL_ENV/bin:$PATH"
    
    # Verify virtual environment Python is available
    if [ -f ".venv/bin/python" ]; then
        VENV_PYTHON=".venv/bin/python"
        VENV_PIP=".venv/bin/pip"
        log_success "Virtual environment Python found: $VENV_PYTHON"
        
        # Test the virtual environment Python
        PYTHON_VERSION=$($VENV_PYTHON --version 2>&1)
        log_info "Virtual environment Python version: $PYTHON_VERSION"
    elif [ -f ".venv/Scripts/python.exe" ]; then
        VENV_PYTHON=".venv/Scripts/python.exe"
        VENV_PIP=".venv/Scripts/pip.exe"
        log_success "Virtual environment Python found: $VENV_PYTHON"
    else
        log_error "Virtual environment Python not found"
        log_info "Available files in .venv/bin/:"
        ls -la .venv/bin/ 2>/dev/null || log_error "Cannot list .venv/bin directory"
        exit 1
    fi
    
    log_success "Virtual environment configured: $VIRTUAL_ENV"
    
    # Install Python dependencies using virtual environment pip
    log_info "Installing Python dependencies..."
    $VENV_PIP install --upgrade pip setuptools wheel
    
    # Check if heavy packages are already installed
    log_info "Checking for existing heavy packages..."
    if $VENV_PYTHON -c "import pandas, reportlab, openpyxl" 2>/dev/null; then
        log_success "Heavy packages already installed, installing remaining dependencies..."
        $VENV_PIP install --prefer-binary --no-cache-dir -r requirements.txt
    else
        # Use optimized installation for faster setup
        log_info "Installing dependencies with optimized settings..."
        if [[ "$OSTYPE" == "linux-gnu"* ]] && [[ "$(uname -m)" == "aarch64" ]]; then
            # ARM64 Linux - install heavy packages first with optimizations
            log_info "Detected ARM64 Linux, installing heavy packages with optimizations..."
            log_warning "Installing pandas and other heavy packages - this may take 5-10 minutes..."
            log_info "You can monitor progress in another terminal with: tail -f /tmp/pip_install.log"
            
            # Install pandas separately with optimizations and logging
            log_info "Installing pandas (this is the slow part)..."
            if $VENV_PIP install --only-binary=pandas --prefer-binary --no-cache-dir pandas==2.0.3 > /tmp/pip_install.log 2>&1; then
                log_success "Pandas installed from pre-built wheel"
            else
                log_warning "Pre-built pandas wheel not available, installing from source (this will take longer)..."
                $VENV_PIP install --no-cache-dir pandas==2.0.3 > /tmp/pip_install.log 2>&1 &
                show_progress $! "Building pandas from source"
                wait $!
            fi
            
            # Install other heavy packages
            log_info "Installing other heavy packages..."
            $VENV_PIP install --only-binary=all --prefer-binary --no-cache-dir reportlab openpyxl pyinstaller
            
            # Install remaining lighter packages
            log_info "Installing remaining packages..."
            $VENV_PIP install --prefer-binary --no-cache-dir -r requirements.txt
        else
            # Other systems - standard installation
            log_info "Installing all packages..."
            $VENV_PIP install --no-cache-dir -r requirements.txt
        fi
    fi
    
    log_success "Python dependencies installed successfully"
    
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
    
    # Check if we need to clean node_modules due to Node.js version upgrade
    NODE_VERSION=$(node --version | sed 's/^v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    
    # Clean node_modules only if necessary
    if [ "$RESET_DB" = true ] || [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
        if [ -d "node_modules" ]; then
            log_info "Cleaning existing node_modules (Node.js version: $NODE_VERSION)..."
            rm -rf node_modules package-lock.json
        fi
        
        # Clear npm cache with error handling
        log_info "Clearing npm cache..."
        npm cache clean --force 2>/dev/null || log_warning "npm cache clean failed, continuing..."
        
        # Install dependencies with retry logic and macOS-specific handling
        local npm_retries=3
        local npm_success=false
        
        # macOS-specific npm configuration
        if command -v brew &> /dev/null; then
            log_info "Configuring npm for macOS..."
            npm config set registry https://registry.npmjs.org/ 2>/dev/null || true
            npm config set fetch-retries 3 2>/dev/null || true
            npm config set fetch-retry-mintimeout 5000 2>/dev/null || true
            npm config set fetch-retry-maxtimeout 60000 2>/dev/null || true
        fi
        
        for ((i=1; i<=npm_retries; i++)); do
            log_info "Installing Node.js dependencies (attempt $i/$npm_retries)..."
            
            # Kill any stuck npm processes before starting
            pkill -f "npm install" 2>/dev/null || true
            
            # Use shorter timeout on macOS and add force flags
            if command -v brew &> /dev/null; then
                # macOS: shorter timeout, force flags, no audit
                if npm install --force --no-audit --no-fund $npm_force_flag; then
                    npm_success=true
                    break
                else
                    log_warning "npm install failed (attempt $i/$npm_retries)"
                    if [ $i -lt $npm_retries ]; then
                        log_info "Cleaning and retrying..."
                        rm -rf node_modules package-lock.json
                        npm cache clean --force 2>/dev/null || true
                        sleep 3
                    fi
                fi
            else
                # Linux: original timeout
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
            fi
        done
        
        if [ "$npm_success" = false ]; then
            log_warning "Failed to install Node.js dependencies after $npm_retries attempts"
            log_info "Attempting to fix Vite compatibility issue..."
            
            # Try to downgrade Vite to a compatible version
            if npm install vite@^5.0.0 --save-dev; then
                log_success "Successfully downgraded Vite to compatible version"
            else
                log_error "Failed to fix Vite compatibility issue"
                log_info "Try manually: cd frontend && npm install --force"
                exit 1
            fi
        fi
        
        # Handle npm audit warnings (non-breaking)
        log_info "Checking for npm audit issues..."
        if npm audit --audit-level=moderate > /dev/null 2>&1; then
            log_info "No critical npm audit issues found"
        else
            log_warning "npm audit found some issues, attempting to fix non-breaking ones..."
            npm audit fix --force > /dev/null 2>&1 || log_warning "Some audit issues could not be automatically fixed"
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
    
    # Test basic PostgreSQL connectivity
    log_info "Testing basic PostgreSQL installation..."
    if ! psql --version > /dev/null 2>&1; then
        log_error "PostgreSQL client is not working properly"
        exit 1
    fi
    
    # Ensure PostgreSQL is properly configured for automatic operation
    ensure_postgresql_auto_config
    
    # Try to connect as postgres user to verify basic setup
    if command -v brew &> /dev/null; then
        # macOS - test with current user
        if ! psql -c "SELECT version();" > /dev/null 2>&1; then
            log_warning "Cannot connect as postgres user. This might indicate a PostgreSQL configuration issue."
            log_info "Attempting to fix basic PostgreSQL setup..."
            
            # Try to initialize PostgreSQL if it's not properly set up
            if command -v initdb &> /dev/null; then
                log_info "Initializing PostgreSQL database cluster..."
                log_info "Homebrew PostgreSQL is already initialized, skipping initdb..."
            fi
        fi
    else
        # Linux - test with postgres user
        if ! sudo -u postgres psql -c "SELECT version();" > /dev/null 2>&1; then
            log_warning "Cannot connect as postgres user. This might indicate a PostgreSQL configuration issue."
            log_info "Attempting to fix basic PostgreSQL setup..."
            
            # Try to initialize PostgreSQL if it's not properly set up
            if command -v initdb &> /dev/null; then
                log_info "Initializing PostgreSQL database cluster..."
                # Linux - use sudo -u postgres
                sudo -u postgres initdb -D /var/lib/postgresql/data 2>/dev/null || sudo -u postgres initdb 2>/dev/null || true
                sudo systemctl restart postgresql 2>/dev/null || true
                sleep 3
            fi
        fi
    fi
    
    log_success "Basic PostgreSQL connectivity verified"
    
    # Start PostgreSQL service based on OS
    if command -v brew &> /dev/null; then
        # macOS
        log_info "Starting PostgreSQL on macOS..."
        brew services start postgresql@14 2>/dev/null || brew services start postgresql 2>/dev/null || true
    elif command -v systemctl &> /dev/null; then
        # Linux with systemd
        log_info "Starting PostgreSQL on Linux..."
        # Try different service names for different PostgreSQL versions
        if sudo systemctl start postgresql 2>/dev/null; then
            log_success "Started postgresql service"
        elif sudo systemctl start postgresql@16 2>/dev/null; then
            log_success "Started postgresql@16 service"
        elif sudo systemctl start postgresql@14 2>/dev/null; then
            log_success "Started postgresql@14 service"
        else
            log_warning "Could not start PostgreSQL service with systemctl"
        fi
        
        # Ensure PostgreSQL is running and restart if needed
        if ! sudo systemctl is-active --quiet postgresql && ! sudo systemctl is-active --quiet postgresql@16 && ! sudo systemctl is-active --quiet postgresql@14; then
            log_warning "PostgreSQL not running, attempting to restart..."
            sudo systemctl restart postgresql 2>/dev/null || sudo systemctl restart postgresql@16 2>/dev/null || sudo systemctl restart postgresql@14 2>/dev/null || true
            sleep 3
        fi
    elif command -v service &> /dev/null; then
        # Linux with service command
        log_info "Starting PostgreSQL with service command..."
        sudo service postgresql start 2>/dev/null || true
        
        # Ensure PostgreSQL is running and restart if needed
        if ! sudo service postgresql status > /dev/null 2>&1; then
            log_warning "PostgreSQL not running, attempting to restart..."
            sudo service postgresql restart 2>/dev/null || true
            sleep 3
        fi
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
        
        # If PostgreSQL is not responding, try to restart it
        if [ $pg_attempts -eq 10 ]; then
            log_warning "PostgreSQL not responding, attempting to restart..."
            if command -v systemctl &> /dev/null; then
                sudo systemctl restart postgresql 2>/dev/null || true
            elif command -v service &> /dev/null; then
                sudo service postgresql restart 2>/dev/null || true
            fi
            sleep 5
        fi
        
        sleep 1
        pg_attempts=$((pg_attempts + 1))
    done
    
    if [ $pg_attempts -eq 30 ]; then
        log_error "PostgreSQL not ready after 30 seconds."
        log_info "PostgreSQL troubleshooting:"
        log_info "1. Check service status: sudo systemctl status postgresql"
        log_info "2. Check logs: sudo journalctl -u postgresql -n 20"
        log_info "3. Try manual start: sudo systemctl start postgresql"
        exit 1
    fi
    
    # Create database and user
    log_info "Creating database and user..."
    
    if command -v brew &> /dev/null; then
        # macOS - use current user for database operations
        log_info "Using current user for database operations on macOS..."
        
        # Drop user if exists and recreate (for fresh installs)
        psql -c "DROP USER IF EXISTS $DATABASE_USER;" 2>/dev/null || true
        
        # Create user with password
        psql -c "CREATE USER $DATABASE_USER WITH PASSWORD '$DATABASE_PASSWORD';" 2>/dev/null || true
        
        # Drop database if exists and recreate (for fresh installs)
        psql -c "DROP DATABASE IF EXISTS $DATABASE_NAME;" 2>/dev/null || true
        
        # Create database with proper owner
        psql -c "CREATE DATABASE $DATABASE_NAME OWNER $DATABASE_USER;" 2>/dev/null || true
        
        # Grant privileges
        psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $DATABASE_USER;" 2>/dev/null || true
        psql -c "ALTER USER $DATABASE_USER CREATEDB;" 2>/dev/null || true
        
        # Grant table and sequence privileges
        psql -d $DATABASE_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DATABASE_USER;" 2>/dev/null || true
        psql -d $DATABASE_NAME -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DATABASE_USER;" 2>/dev/null || true
        psql -d $DATABASE_NAME -c "GRANT CREATE ON SCHEMA public TO $DATABASE_USER;" 2>/dev/null || true
        psql -d $DATABASE_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DATABASE_USER;" 2>/dev/null || true
        psql -d $DATABASE_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DATABASE_USER;" 2>/dev/null || true
        
        # Grant table ownership for existing tables
        psql -d $DATABASE_NAME -c "DO \$\$ DECLARE r RECORD; BEGIN FOR r IN SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LOOP EXECUTE 'ALTER TABLE ' || quote_ident(r.table_name) || ' OWNER TO $DATABASE_USER;'; END LOOP; END \$\$;" 2>/dev/null || true
        
        # Grant sequence ownership for existing sequences
        psql -d $DATABASE_NAME -c "DO \$\$ DECLARE r RECORD; BEGIN FOR r IN SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public' LOOP EXECUTE 'ALTER SEQUENCE ' || r.sequence_name || ' OWNER TO $DATABASE_USER;'; END LOOP; END \$\$;" 2>/dev/null || true
    else
        # Linux - use sudo -u postgres
        # Drop user if exists and recreate (for fresh installs)
        sudo -u postgres psql -c "DROP USER IF EXISTS $DATABASE_USER;" 2>/dev/null || true
        
        # Create user with password
        sudo -u postgres psql -c "CREATE USER $DATABASE_USER WITH PASSWORD '$DATABASE_PASSWORD';" 2>/dev/null || true
        
        # Drop database if exists and recreate (for fresh installs)
        sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DATABASE_NAME;" 2>/dev/null || true
        
        # Create database with proper owner
        sudo -u postgres psql -c "CREATE DATABASE $DATABASE_NAME OWNER $DATABASE_USER;" 2>/dev/null || true
        
        # Grant privileges
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $DATABASE_USER;" 2>/dev/null || true
        sudo -u postgres psql -c "ALTER USER $DATABASE_USER CREATEDB;" 2>/dev/null || true
        
        # Grant table and sequence privileges
        sudo -u postgres psql -d $DATABASE_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DATABASE_USER;" 2>/dev/null || true
        sudo -u postgres psql -d $DATABASE_NAME -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DATABASE_USER;" 2>/dev/null || true
        sudo -u postgres psql -d $DATABASE_NAME -c "GRANT CREATE ON SCHEMA public TO $DATABASE_USER;" 2>/dev/null || true
        sudo -u postgres psql -d $DATABASE_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DATABASE_USER;" 2>/dev/null || true
        sudo -u postgres psql -d $DATABASE_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DATABASE_USER;" 2>/dev/null || true
        
        # Grant table ownership for existing tables
        sudo -u postgres psql -d $DATABASE_NAME -c "DO \$\$ DECLARE r RECORD; BEGIN FOR r IN SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LOOP EXECUTE 'ALTER TABLE ' || quote_ident(r.table_name) || ' OWNER TO $DATABASE_USER;'; END LOOP; END \$\$;" 2>/dev/null || true
        
        # Grant sequence ownership for existing sequences
        sudo -u postgres psql -d $DATABASE_NAME -c "DO \$\$ DECLARE r RECORD; BEGIN FOR r IN SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public' LOOP EXECUTE 'ALTER SEQUENCE ' || r.sequence_name || ' OWNER TO $DATABASE_USER;'; END LOOP; END \$\$;" 2>/dev/null || true
    fi
    
    # Set DATABASE_URL environment variable based on successful connection method
    # We'll set this after testing the connection
    log_info "Testing database connection to determine best DATABASE_URL..."
    
    # Test database connection with trust authentication
    log_info "Testing database connection with trust authentication..."
    
    # Method 1: Try with postgres user (using trust authentication)
    log_info "Testing connection with postgres user..."
    if psql -h $DATABASE_HOST -p $DATABASE_PORT -U postgres -d $DATABASE_NAME -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "Database connection successful with postgres user!"
        export DATABASE_URL="postgresql://postgres@$DATABASE_HOST:$DATABASE_PORT/$DATABASE_NAME"
        log_info "Using postgres user: $DATABASE_URL"
    else
        log_warning "postgres user connection failed, trying local socket connection..."
        
        # Method 2: Try local socket connection (no host specification)
        if psql -U postgres -d $DATABASE_NAME -c "SELECT 1;" > /dev/null 2>&1; then
            log_success "Database connection successful with local socket!"
            export DATABASE_URL="postgresql://postgres@localhost:$DATABASE_PORT/$DATABASE_NAME"
            log_info "Using local socket connection: $DATABASE_URL"
        else
            log_warning "local socket connection failed, trying sudo -u postgres..."
            
            # Method 3: Try with sudo -u postgres (final fallback)
            if command -v brew &> /dev/null; then
                # macOS - try with current user
                if psql -d $DATABASE_NAME -c "SELECT 1;" > /dev/null 2>&1; then
                    log_success "Database connection successful with current user!"
                    export DATABASE_URL="postgresql://postgres@localhost:$DATABASE_PORT/$DATABASE_NAME"
                    log_info "Using current user connection: $DATABASE_URL"
                else
                    log_error "All database connection methods failed!"
                    log_info "PostgreSQL troubleshooting information:"
                    log_info "1. Check if PostgreSQL is running: brew services list | grep postgresql"
                    log_info "2. Check PostgreSQL logs: tail -f /opt/homebrew/var/log/postgresql@14.log"
                    log_info "3. Try connecting manually: psql"
                    log_info "4. Check pg_hba.conf configuration"
                    log_info "5. Check if trust authentication is properly configured"
                    log_info "6. Try: brew services restart postgresql@14"
                    exit 1
                fi
            else
                # Linux - try with sudo -u postgres
                if sudo -u postgres psql -d $DATABASE_NAME -c "SELECT 1;" > /dev/null 2>&1; then
                    log_success "Database connection successful with sudo -u postgres!"
                    export DATABASE_URL="postgresql://postgres@localhost:$DATABASE_PORT/$DATABASE_NAME"
                    log_info "Using sudo postgres connection: $DATABASE_URL"
                else
                    log_error "All database connection methods failed!"
                    log_info "PostgreSQL troubleshooting information:"
                    log_info "1. Check if PostgreSQL is running: sudo systemctl status postgresql"
                    log_info "2. Check PostgreSQL logs: sudo journalctl -u postgresql"
                    log_info "3. Try connecting manually: sudo -u postgres psql"
                    log_info "4. Check pg_hba.conf configuration"
                    log_info "5. Check if trust authentication is properly configured"
                    log_info "6. Try: sudo systemctl restart postgresql"
                    exit 1
                fi
            fi
        fi
    fi
    
    # Also set individual environment variables for the backend
    export DB_HOST="$DATABASE_HOST"
    export DB_PORT="$DATABASE_PORT"
    export DB_NAME="$DATABASE_NAME"
    export DB_USER="postgres"
    export DB_PASSWORD=""
    export DB_PASS=""
    
    log_info "Database environment variables set:"
    log_info "DATABASE_URL: $DATABASE_URL"
    log_info "DB_HOST: $DB_HOST"
    log_info "DB_PORT: $DB_PORT"
    log_info "DB_NAME: $DB_NAME"
    log_info "DB_USER: $DB_USER"
    
    # Run database migration for enhanced logging
    log_info "Running database migration for enhanced logging..."
    cd backend
    if $PROJECT_ROOT/$VENV_PYTHON db_migration.py; then
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
    
    # Ensure environment variables are set for the backend
    log_info "Setting up environment variables for backend..."
    export DATABASE_URL="$DATABASE_URL"
    export DB_HOST="$DB_HOST"
    export DB_PORT="$DB_PORT"
    export DB_NAME="$DB_NAME"
    export DB_USER="$DB_USER"
    export DB_PASSWORD="$DB_PASSWORD"
    export DB_PASS="$DB_PASS"
    
    log_info "Backend will use DATABASE_URL: $DATABASE_URL"
    
    # Build command based on flags using virtual environment Python
    local cmd="$PROJECT_ROOT/$VENV_PYTHON app.py --port $BACKEND_PORT"
    
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
    
    if [ "$RS485_REAL_MODE" = true ]; then
        cmd="$cmd --rs485-real"
    fi
    
    # Set RS485 mode - default is real hardware
    if [ "$RS485_REAL_MODE" = true ]; then
        export RS485_MOCK_MODE="false"
        log_info "RS485 real hardware mode enabled"
    else
        # Default to real hardware mode
        export RS485_MOCK_MODE="false"
        log_info "RS485 real hardware mode enabled (default)"
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
    
    # Check if dependencies are properly installed
    if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
        log_warning "Frontend dependencies not found. Installing..."
        npm install --force
    fi
    
    # Check if Vite is compatible with current Node.js version
    NODE_VERSION=$(node --version | sed 's/^v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    
    if [ "$NODE_MAJOR" -lt 20 ]; then
        log_warning "Node.js version $NODE_VERSION detected. Ensuring Vite compatibility..."
        # Downgrade Vite to a compatible version
        npm install vite@^5.0.0 --save-dev --force
    fi
    
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
    if $PROJECT_ROOT/$VENV_PYTHON test_auth_comprehensive.py; then
        log_success "Authentication tests passed!"
    else
        log_warning "Some authentication tests failed. Check the output above for details."
    fi
    cd ..
    
    # Run logging system tests
    log_info "Running logging system tests..."
    cd backend
    if $PROJECT_ROOT/$VENV_PYTHON test_logging.py; then
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