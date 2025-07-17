#!/bin/bash

# Quick npm fix for macOS
set -e  # Exit on any error

echo "=== Fixing npm installation on macOS ==="
echo "Current directory: $(pwd)"
echo "Node.js version: $(node --version 2>/dev/null || echo 'Node.js not found')"
echo "npm version: $(npm --version 2>/dev/null || echo 'npm not found')"

# Kill any stuck npm processes
echo "1. Killing stuck npm processes..."
pkill -f "npm install" 2>/dev/null || true
pkill -f "node" 2>/dev/null || true

# Clear npm cache
echo "2. Clearing npm cache..."
npm cache clean --force

# Clear node_modules and package-lock.json
echo "3. Cleaning existing node_modules..."
if [ -d "frontend" ]; then
    cd frontend
    echo "   Found frontend directory, cleaning..."
    rm -rf node_modules package-lock.json 2>/dev/null || echo "   No existing node_modules to clean"
else
    echo "   Frontend directory not found, creating it..."
    mkdir -p frontend
    cd frontend
fi

# Set npm configuration for better performance
echo "4. Configuring npm for better performance..."
npm config set registry https://registry.npmjs.org/
npm config set fetch-retries 3
npm config set fetch-retry-mintimeout 5000
npm config set fetch-retry-maxtimeout 60000

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "   No package.json found, creating basic React app..."
    npm create vite@latest . -- --template react --yes
fi

# Install with force flag and shorter timeout
echo "5. Installing dependencies with force flag..."
npm install --force --no-audit --no-fund

echo "6. Installing Vite separately..."
npm install vite@^5.0.0 --save-dev --force

echo "=== npm installation completed ==="
echo "You can now run: ./start.sh --demo --reset-db --verbose" 