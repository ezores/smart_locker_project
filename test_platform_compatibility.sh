#!/bin/bash

# Platform Compatibility Test for Smart Locker System
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

log_info "Smart Locker System - Platform Compatibility Test"
log_info "=================================================="

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get &> /dev/null; then
        PLATFORM="Debian/Ubuntu"
    elif command -v yum &> /dev/null; then
        PLATFORM="CentOS/RHEL"
    elif command -v dnf &> /dev/null; then
        PLATFORM="Fedora"
    else
        PLATFORM="Linux (Unknown)"
    fi
else
    PLATFORM="Unknown ($OSTYPE)"
fi

log_info "Detected Platform: $PLATFORM"

# Check WSL
if [[ -n "$WSL_DISTRO_NAME" ]]; then
    log_info "Running in WSL: $WSL_DISTRO_NAME"
fi

# Check Raspberry Pi
if [[ -f "/proc/cpuinfo" ]] && grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    log_info "Detected Raspberry Pi"
fi

# Test prerequisites
log_info "Testing prerequisites..."

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_success "Python 3: $PYTHON_VERSION"
else
    log_error "Python 3 not found"
    exit 1
fi

# Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    log_success "Node.js: $NODE_VERSION"
else
    log_error "Node.js not found"
    exit 1
fi

# npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version 2>&1)
    log_success "npm: $NPM_VERSION"
else
    log_error "npm not found"
    exit 1
fi

# PostgreSQL
if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version 2>&1 | cut -d' ' -f3)
    log_success "PostgreSQL: $PSQL_VERSION"
else
    log_error "PostgreSQL not found - PostgreSQL is required"
    log_info "Install PostgreSQL: https://www.postgresql.org/download/"
    log_info "Or run: ./setup_postgresql.sh"
    exit 1
fi

# Package managers
log_info "Available package managers:"
if command -v brew &> /dev/null; then
    log_success "Homebrew (macOS)"
fi
if command -v apt-get &> /dev/null; then
    log_success "apt-get (Debian/Ubuntu)"
fi
if command -v yum &> /dev/null; then
    log_success "yum (CentOS/RHEL)"
fi
if command -v dnf &> /dev/null; then
    log_success "dnf (Fedora)"
fi

# Service managers
log_info "Available service managers:"
if command -v systemctl &> /dev/null; then
    log_success "systemctl (systemd)"
fi
if command -v service &> /dev/null; then
    log_success "service (init.d)"
fi

# Memory check
if [[ -f "/proc/meminfo" ]]; then
    TOTAL_MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    TOTAL_MEM_GB=$((TOTAL_MEM / 1024 / 1024))
    log_info "Total Memory: ${TOTAL_MEM_GB}GB"
    
    if [[ $TOTAL_MEM_GB -lt 2 ]]; then
        log_warning "Low memory detected. System may be slow."
    else
        log_success "Sufficient memory for comfortable operation"
    fi
fi

# Disk space check
if command -v df &> /dev/null; then
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    AVAILABLE_SPACE_GB=$((AVAILABLE_SPACE / 1024 / 1024))
    log_info "Available disk space: ${AVAILABLE_SPACE_GB}GB"
    
    if [[ $AVAILABLE_SPACE_GB -lt 5 ]]; then
        log_warning "Low disk space. Ensure at least 5GB available."
    else
        log_success "Sufficient disk space"
    fi
fi

# Test script permissions
if [[ -x "start.sh" ]]; then
    log_success "start.sh is executable"
else
    log_warning "start.sh is not executable - run: chmod +x start.sh"
fi

if [[ -x "setup_postgresql.sh" ]]; then
    log_success "setup_postgresql.sh is executable"
else
    log_warning "setup_postgresql.sh is not executable - run: chmod +x setup_postgresql.sh"
fi

# Platform-specific recommendations
log_info "Platform-specific recommendations:"

case $PLATFORM in
    "macOS")
        log_info "macOS: All features supported"
        log_info "   - PostgreSQL via Homebrew"
        log_info "   - Node.js via Homebrew or official installer"
        log_info "   - Python via system or Homebrew"
        ;;
    "Debian/Ubuntu")
        log_info "Debian/Ubuntu: All features supported"
        log_info "   - PostgreSQL via apt-get"
        log_info "   - Node.js via NodeSource repository"
        log_info "   - Python via system package manager"
        ;;
    "CentOS/RHEL")
        log_info "CentOS/RHEL: All features supported"
        log_info "   - PostgreSQL via yum/dnf"
        log_info "   - Node.js via NodeSource repository"
        log_info "   - Python via system package manager"
        ;;
    "Fedora")
        log_info "Fedora: All features supported"
        log_info "   - PostgreSQL via dnf"
        log_info "   - Node.js via dnf or NodeSource repository"
        log_info "   - Python via system package manager"
        ;;
    *)
        log_warning "Unknown platform: $PLATFORM"
        log_info "Manual installation may be required"
        ;;
esac

# WSL-specific recommendations
if [[ -n "$WSL_DISTRO_NAME" ]]; then
    log_info "WSL-specific notes:"
    log_info "   - Use SQLite for better performance"
    log_info "   - npm may need --force flag"
    log_info "   - File permissions may need adjustment"
fi

# Raspberry Pi-specific recommendations
if [[ -f "/proc/cpuinfo" ]] && grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    log_info "Raspberry Pi-specific notes:"
    log_info "   - Frontend compilation may be slow"
    log_info "   - Consider using --minimal mode for testing"
    log_info "   - Ensure adequate cooling for extended use"
fi

log_success "Platform compatibility test completed!"
log_info "Your system appears ready to run the Smart Locker System."
log_info "Run './start.sh --demo --reset-db --verbose' to start the system." 