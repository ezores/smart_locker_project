#!/bin/bash

# Smart Locker System - Download Executables Script
# This script helps users download and set up executable builds

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if GitHub CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed. Please install it first:"
        echo "  macOS: brew install gh"
        echo "  Ubuntu: sudo apt install gh"
        echo "  Windows: winget install GitHub.cli"
        exit 1
    fi
}

# Check if user is authenticated with GitHub
check_gh_auth() {
    if ! gh auth status &> /dev/null; then
        print_error "You are not authenticated with GitHub. Please run:"
        echo "  gh auth login"
        exit 1
    fi
}

# Detect operating system
detect_os() {
    local osname
    osname=$(uname -s)
    case "$osname" in
        Darwin*)    echo "macos";;
        Linux*)     echo "linux";;
        CYGWIN*|MINGW32*|MSYS*|MINGW*) echo "windows";;
        *)          echo "unknown";;
    esac
}

# Download latest artifacts
download_artifacts() {
    local os="$1"
    local repo="ezores/smart_locker_project"

    print_status "Detecting your operating system..."
    local detected_os
    detected_os=$(detect_os)

    if [[ "$detected_os" == "unknown" ]]; then
        print_error "Could not detect your operating system. Please specify manually:"
        echo "  ./scripts/download_executables.sh macos"
        echo "  ./scripts/download_executables.sh linux"
        echo "  ./scripts/download_executables.sh windows"
        exit 1
    fi

    print_status "Your OS detected as: $detected_os"

    # Override with user-specified OS if provided
    if [[ -n "$os" ]]; then
        detected_os="$os"
        print_status "Using specified OS: $detected_os"
    fi

    print_status "Finding latest build artifacts for $detected_os..."

    # Get the latest workflow run
    local run_id
    run_id=$(gh api repos/"$repo"/actions/runs --jq '.workflow_runs[0].id')

    if [[ -z "$run_id" ]]; then
        print_error "No workflow runs found. Make sure the repository has been set up with CI/CD."
        exit 1
    fi

    print_status "Found workflow run: $run_id"

    # Get artifacts for this run
    local artifacts
    artifacts=$(gh api repos/"$repo"/actions/runs/"$run_id"/artifacts)
    local artifact_name="smart-locker-executables-${detected_os}-latest"

    print_status "Looking for artifact: $artifact_name"

    # Check if artifact exists
    local artifact_id
    artifact_id=$(echo "$artifacts" | jq -r ".artifacts[] | select(.name == \"$artifact_name\") | .id")

    if [[ -z "$artifact_id" || "$artifact_id" == "null" ]]; then
        print_error "No executable build found for $detected_os."
        echo "Available artifacts:"
        echo "$artifacts" | jq -r '.artifacts[].name'
        exit 1
    fi

    print_status "Found artifact ID: $artifact_id"

    # Create downloads directory
    mkdir -p downloads
    cd downloads || exit 1

    # Download artifact
    print_status "Downloading executable build..."
    if gh api repos/"$repo"/actions/artifacts/"$artifact_id"/zip > "smart_locker_${detected_os}.zip"; then
        print_success "Download completed!"

        # Extract the zip file
        print_status "Extracting files..."
        unzip -o "smart_locker_${detected_os}.zip"

        # Make startup script executable
        if [[ -f "start_smart_locker.sh" ]]; then
            chmod +x start_smart_locker.sh
            print_success "Startup script made executable"
        fi

        print_success "Setup complete!"
        echo ""
        echo "To start the Smart Locker System:"
        if [[ "$detected_os" == "windows" ]]; then
            echo "  start_smart_locker.bat"
        else
            echo "  ./start_smart_locker.sh"
        fi
        echo ""
        echo "The system will be available at:"
        echo "  Backend: http://localhost:5172"
        echo "  Frontend: http://localhost:5173"
        echo "  Admin Dashboard: http://localhost:5173/admin"
        echo ""
        echo "Default credentials:"
        echo "  Admin: admin / admin123"
        echo "  Student: student1 / student123"
        echo "  Manager: manager / manager123"
        echo "  Supervisor: supervisor / supervisor123"
    else
        print_error "Download failed. Please check your internet connection and try again."
        exit 1
    fi
}

# Main function
main() {
    echo "Smart Locker System - Download Executables"
    echo "=========================================="
    echo ""

    # Check prerequisites
    check_gh_cli
    check_gh_auth

    # Download artifacts
    download_artifacts "$1"
}

# Run main function
main "$@" 