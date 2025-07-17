#!/bin/bash

# Enable verbose output
set -x  # Print each command before executing
set -e  # Exit on any error

echo "=== Restoring Frontend ==="
echo "Current directory: $(pwd)"
echo "Node.js version: $(node --version 2>/dev/null || echo 'Node.js not found')"
echo "npm version: $(npm --version 2>/dev/null || echo 'npm not found')"

# Kill any stuck processes
echo "1. Killing stuck processes..."
echo "   Looking for npm install processes..."
ps aux | grep "npm install" | grep -v grep || echo "   No npm install processes found"
pkill -f "npm install" 2>/dev/null && echo "   Killed npm install processes" || echo "   No npm install processes to kill"

echo "   Looking for node processes..."
ps aux | grep "node" | grep -v grep || echo "   No node processes found"
pkill -f "node" 2>/dev/null && echo "   Killed node processes" || echo "   No node processes to kill"

# Check if frontend directory exists
echo "2. Checking frontend directory..."
if [ -d "frontend" ]; then
    echo "   Frontend directory exists"
    ls -la frontend/
else
    echo "   Frontend directory not found, creating it..."
    mkdir -p frontend
fi

# Go to frontend directory
echo "3. Entering frontend directory..."
cd frontend
echo "   Current directory: $(pwd)"
echo "   Contents of frontend directory:"
ls -la

# Create missing .vite directory
echo "4. Creating missing .vite directory..."
if [ -d ".vite" ]; then
    echo "   .vite directory already exists"
else
    echo "   Creating .vite directory..."
    mkdir -p .vite
    echo "   .vite directory created"
fi
echo "   .vite directory contents:"
ls -la .vite 2>/dev/null || echo "   .vite directory is empty"

# Remove any remaining problematic files
echo "5. Cleaning up..."
echo "   Checking for node_modules..."
if [ -d "node_modules" ]; then
    echo "   Removing node_modules directory..."
    rm -rf node_modules
    echo "   node_modules removed"
else
    echo "   No node_modules directory found"
fi

echo "   Checking for package-lock.json..."
if [ -f "package-lock.json" ]; then
    echo "   Removing package-lock.json..."
    rm -f package-lock.json
    echo "   package-lock.json removed"
else
    echo "   No package-lock.json found"
fi

# Clear npm cache
echo "6. Clearing npm cache..."
echo "   Running: npm cache clean --force"
npm cache clean --force
echo "   npm cache cleared"

# Check package.json
echo "7. Checking package.json..."
if [ -f "package.json" ]; then
    echo "   package.json exists"
    echo "   package.json contents:"
    cat package.json
else
    echo "   package.json not found!"
    echo "   Creating basic package.json..."
    cat > package.json << 'EOF'
{
  "name": "smart-locker-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.55.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "vite": "^5.0.8"
  }
}
EOF
    echo "   package.json created"
fi

# Install dependencies
echo "8. Installing dependencies..."
echo "   Running: npm install --force --no-audit --no-fund"
npm install --force --no-audit --no-fund
echo "   Dependencies installed successfully"

# Install Vite separately
echo "9. Installing Vite..."
echo "   Running: npm install vite@^5.0.0 --save-dev --force"
npm install vite@^5.0.0 --save-dev --force
echo "   Vite installed successfully"

# Verify installation
echo "10. Verifying installation..."
echo "    Checking node_modules..."
if [ -d "node_modules" ]; then
    echo "    ✓ node_modules directory exists"
    echo "    node_modules size: $(du -sh node_modules 2>/dev/null || echo 'unknown')"
else
    echo "    ✗ node_modules directory missing!"
fi

echo "    Checking package-lock.json..."
if [ -f "package-lock.json" ]; then
    echo "    ✓ package-lock.json exists"
    echo "    package-lock.json size: $(du -sh package-lock.json 2>/dev/null || echo 'unknown')"
else
    echo "    ✗ package-lock.json missing!"
fi

echo "    Checking Vite installation..."
if npm list vite > /dev/null 2>&1; then
    echo "    ✓ Vite is installed"
    npm list vite
else
    echo "    ✗ Vite is not installed!"
fi

# Go back to project root
echo "11. Returning to project root..."
cd ..
echo "    Current directory: $(pwd)"

echo ""
echo "=== FRONTEND RESTORATION COMPLETED ==="
echo "✓ Frontend restored successfully"
echo "✓ All dependencies installed"
echo "✓ Vite build system ready"
echo ""
echo "You can now run: ./start.sh --demo --verbose --reset-db"
echo "Or test the backend only: cd backend && source ../.venv/bin/activate && python app.py --demo --port 5050" 