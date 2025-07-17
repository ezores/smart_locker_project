#!/bin/bash

echo "=== Quick npm fix ==="

# Kill any stuck processes
echo "1. Killing stuck processes..."
pkill -f "npm install" 2>/dev/null || true
pkill -f "node" 2>/dev/null || true

# Clear npm cache
echo "2. Clearing npm cache..."
npm cache clean --force

# Fix frontend directory permissions and clean
echo "3. Fixing frontend directory..."
cd frontend

# Remove problematic directories with force
echo "   Removing node_modules..."
rm -rf node_modules 2>/dev/null || true
rm -rf "node_modules 2" 2>/dev/null || true
rm -rf ".vite 2" 2>/dev/null || true

# Remove package-lock files
echo "   Removing package-lock files..."
rm -f package-lock.json 2>/dev/null || true
rm -f "package-lock 2.json" 2>/dev/null || true

# Fix permissions
echo "   Fixing permissions..."
chmod -R 755 . 2>/dev/null || true

# Install dependencies
echo "4. Installing dependencies..."
npm install --force --no-audit --no-fund

echo "5. Done! You can now run: ./start.sh --demo --reset-db --verbose" 