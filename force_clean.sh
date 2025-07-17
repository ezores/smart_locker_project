#!/bin/bash

echo "=== Force Cleaning Frontend ==="
echo "Current directory: $(pwd)"

# Kill any stuck processes
echo "1. Killing all related processes..."
pkill -f "npm" 2>/dev/null || true
pkill -f "node" 2>/dev/null || true
pkill -f "rm" 2>/dev/null || true

# Go to frontend
echo "2. Entering frontend directory..."
cd frontend
echo "Current directory: $(pwd)"

# Force delete with different methods
echo "3. Force deleting node_modules..."

# Method 1: Try with sudo if available
if command -v sudo &> /dev/null; then
    echo "   Trying sudo rm -rf node_modules..."
    sudo rm -rf node_modules 2>/dev/null && echo "   ✓ Deleted with sudo" || echo "   ✗ Sudo method failed"
else
    echo "   Sudo not available, trying alternative methods..."
fi

# Method 2: Try with find and delete
if [ -d "node_modules" ]; then
    echo "   Trying find method..."
    find node_modules -delete 2>/dev/null && echo "   ✓ Deleted with find" || echo "   ✗ Find method failed"
fi

# Method 3: Try with rsync (creates empty directory then removes)
if [ -d "node_modules" ]; then
    echo "   Trying rsync method..."
    mkdir -p /tmp/empty_dir
    rsync -a --delete /tmp/empty_dir/ node_modules/ 2>/dev/null && rmdir node_modules 2>/dev/null && echo "   ✓ Deleted with rsync" || echo "   ✗ Rsync method failed"
    rmdir /tmp/empty_dir 2>/dev/null || true
fi

# Method 4: Try with unlink (for symlinks)
if [ -L "node_modules" ]; then
    echo "   Trying unlink method..."
    unlink node_modules 2>/dev/null && echo "   ✓ Deleted symlink" || echo "   ✗ Unlink method failed"
fi

# Check if node_modules still exists
if [ -d "node_modules" ]; then
    echo "   ⚠ node_modules still exists, trying to rename and delete..."
    mv node_modules node_modules_old 2>/dev/null && echo "   ✓ Renamed to node_modules_old" || echo "   ✗ Rename failed"
    rm -rf node_modules_old 2>/dev/null && echo "   ✓ Deleted renamed directory" || echo "   ✗ Delete of renamed directory failed"
fi

# Delete package-lock.json
echo "4. Deleting package-lock.json..."
rm -f package-lock.json 2>/dev/null && echo "   ✓ package-lock.json deleted" || echo "   ✗ package-lock.json delete failed"

# Clear npm cache
echo "5. Clearing npm cache..."
npm cache clean --force 2>/dev/null && echo "   ✓ npm cache cleared" || echo "   ✗ npm cache clear failed"

# Verify cleanup
echo "6. Verifying cleanup..."
echo "   Current directory contents:"
ls -la

if [ ! -d "node_modules" ] && [ ! -f "package-lock.json" ]; then
    echo "   ✓ Cleanup successful - node_modules and package-lock.json removed"
else
    echo "   ⚠ Some files may still exist"
    if [ -d "node_modules" ]; then
        echo "   - node_modules directory still exists"
    fi
    if [ -f "package-lock.json" ]; then
        echo "   - package-lock.json still exists"
    fi
fi

echo ""
echo "=== Force Clean Completed ==="
echo "You can now try: ./restore_frontend.sh"
echo "Or manually: npm install --force --no-audit --no-fund" 