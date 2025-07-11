#!/bin/bash

# Setup Branch Protection for Smart Locker Project
# This script helps configure branch protection rules using GitHub CLI

set -e

echo "Setting up branch protection for Smart Locker Project..."

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

# Get repository name
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "Configuring branch protection for repository: $REPO"

# Function to setup branch protection
setup_branch_protection() {
    local branch=$1
    local strict=$2
    
    echo "Setting up protection for $branch branch..."
    
    # Enable branch protection
    gh api repos/:owner/:repo/branches/$branch/protection \
        --method PUT \
        --field required_status_checks='{"strict":'$strict',"contexts":["Backend Tests","Frontend Tests","Integration Tests","Security Scan","Code Quality"]}' \
        --field enforce_admins=true \
        --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"require_last_push_approval":false}' \
        --field restrictions='{"users":[],"teams":[]}' \
        --field allow_force_pushes=false \
        --field allow_deletions=false \
        --field block_creations=false \
        --field required_conversation_resolution=true
    
    echo "Branch protection configured for $branch"
}

# Setup main branch protection
setup_branch_protection "main" "true"

# Setup develop branch protection (if it exists)
if git show-ref --verify --quiet refs/remotes/origin/develop; then
    setup_branch_protection "develop" "false"
    echo "Develop branch protection configured"
else
    echo "Warning: Develop branch not found, skipping develop protection"
fi

echo ""
echo "Branch protection setup complete!"
echo ""
echo "Summary of protection rules:"
echo "- Main branch: Requires all CI checks to pass"
echo "- Pull requests: Require at least 1 approval"
echo "- Force pushes: Disabled"
echo "- Branch deletions: Disabled"
echo "- Conversation resolution: Required"
echo ""
echo "Note: Only repository owners can bypass these rules" 