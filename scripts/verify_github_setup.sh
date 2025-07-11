#!/bin/bash

# Smart Locker Project - GitHub Setup Verification Script
# This script verifies that the GitHub repository setup is working correctly

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

# Check if GitHub CLI is installed and authenticated
check_gh_setup() {
    print_status "Checking GitHub CLI setup..."
    
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed"
        return 1
    fi
    
    if ! gh auth status &> /dev/null; then
        print_error "GitHub CLI is not authenticated"
        return 1
    fi
    
    print_success "GitHub CLI is properly set up"
    return 0
}

# Check repository settings
check_repository_settings() {
    print_status "Checking repository settings..."
    
    # Get repository info
    repo_info=$(gh repo view --json name,description,topics,defaultBranchRef)
    
    # Check description
    description=$(echo "$repo_info" | jq -r '.description')
    if [[ "$description" == "Smart Locker Management System with Flask backend and React frontend" ]]; then
        print_success "Repository description is correct"
    else
        print_warning "Repository description may need updating"
    fi
    
    # Check topics
    topics=$(echo "$repo_info" | jq -r '.topics[]' | tr '\n' ' ')
    if [[ "$topics" == *"smart-locker"* ]]; then
        print_success "Repository topics are set"
    else
        print_warning "Repository topics may need updating"
    fi
    
    # Check default branch
    default_branch=$(echo "$repo_info" | jq -r '.defaultBranchRef.name')
    if [[ "$default_branch" == "main" ]]; then
        print_success "Default branch is main"
    else
        print_warning "Default branch is not main: $default_branch"
    fi
}

# Check branch protection
check_branch_protection() {
    print_status "Checking branch protection rules..."
    
    # Check main branch protection
    main_protection=$(gh api repos/:owner/:repo/branches/main/protection 2>/dev/null || echo "{}")
    
    if [[ "$main_protection" != "{}" ]]; then
        print_success "Main branch protection is enabled"
        
        # Check required status checks
        required_checks=$(echo "$main_protection" | jq -r '.required_status_checks.contexts[]?' 2>/dev/null || echo "")
        if [[ "$required_checks" == *"backend-tests"* ]]; then
            print_success "Required status checks are configured"
        else
            print_warning "Required status checks may not be fully configured"
        fi
        
        # Check required reviews
        review_count=$(echo "$main_protection" | jq -r '.required_pull_request_reviews.required_approving_review_count' 2>/dev/null || echo "0")
        if [[ "$review_count" -ge 1 ]]; then
            print_success "Required reviews are configured (minimum $review_count)"
        else
            print_warning "Required reviews may not be configured"
        fi
    else
        print_error "Main branch protection is not enabled"
    fi
    
    # Check develop branch protection
    develop_protection=$(gh api repos/:owner/:repo/branches/develop/protection 2>/dev/null || echo "{}")
    
    if [[ "$develop_protection" != "{}" ]]; then
        print_success "Develop branch protection is enabled"
    else
        print_warning "Develop branch protection is not enabled"
    fi
}

# Check Actions workflows
check_actions_workflows() {
    print_status "Checking GitHub Actions workflows..."
    
    workflows=$(gh api repos/:owner/:repo/actions/workflows 2>/dev/null || echo "{}")
    workflow_count=$(echo "$workflows" | jq -r '.workflows | length' 2>/dev/null || echo "0")
    
    if [[ "$workflow_count" -gt 0 ]]; then
        print_success "GitHub Actions workflows are configured ($workflow_count workflows)"
        
        # List workflows
        echo "$workflows" | jq -r '.workflows[].name' 2>/dev/null || echo "Could not list workflows"
    else
        print_warning "No GitHub Actions workflows found"
    fi
}

# Check security features
check_security_features() {
    print_status "Checking security features..."
    
    security_settings=$(gh api repos/:owner/:repo/security-and-analysis 2>/dev/null || echo "{}")
    
    # Check secret scanning
    secret_scanning=$(echo "$security_settings" | jq -r '.secret_scanning.status' 2>/dev/null || echo "disabled")
    if [[ "$secret_scanning" == "enabled" ]]; then
        print_success "Secret scanning is enabled"
    else
        print_warning "Secret scanning is not enabled"
    fi
    
    # Check Dependabot
    dependabot_security=$(echo "$security_settings" | jq -r '.dependabot_security_updates.status' 2>/dev/null || echo "disabled")
    if [[ "$dependabot_security" == "enabled" ]]; then
        print_success "Dependabot security updates are enabled"
    else
        print_warning "Dependabot security updates are not enabled"
    fi
}

# Check Actions permissions
check_actions_permissions() {
    print_status "Checking Actions permissions..."
    
    actions_permissions=$(gh api repos/:owner/:repo/actions/permissions 2>/dev/null || echo "{}")
    allowed_actions=$(echo "$actions_permissions" | jq -r '.allowed_actions' 2>/dev/null || echo "all")
    
    if [[ "$allowed_actions" == "selected" ]]; then
        print_success "Actions permissions are restricted to selected actions"
    else
        print_warning "Actions permissions are not restricted (currently: $allowed_actions)"
    fi
}

# Check for required files
check_required_files() {
    print_status "Checking for required configuration files..."
    
    files_to_check=(
        ".github/workflows/ci-cd.yml"
        ".github/pull_request_template.md"
        ".github/CODEOWNERS"
        ".github/dependabot.yml"
        ".github/ISSUE_TEMPLATE/bug_report.md"
        ".github/ISSUE_TEMPLATE/feature_request.md"
    )
    
    missing_files=()
    
    for file in "${files_to_check[@]}"; do
        if [[ -f "$file" ]]; then
            print_success "Found $file"
        else
            missing_files+=("$file")
            print_warning "Missing $file"
        fi
    done
    
    if [[ ${#missing_files[@]} -eq 0 ]]; then
        print_success "All required configuration files are present"
    else
        print_warning "Missing ${#missing_files[@]} configuration files"
    fi
}

# Main verification function
main() {
    echo "Smart Locker Project - GitHub Setup Verification"
    echo "==============================================="
    echo ""
    
    # Check all components
    check_gh_setup
    check_repository_settings
    check_branch_protection
    check_actions_workflows
    check_security_features
    check_actions_permissions
    check_required_files
    
    echo ""
    print_status "Verification complete!"
    echo ""
    echo "Next steps:"
    echo "1. Push the .github directory to your repository"
    echo "2. Create a test pull request to verify CI/CD"
    echo "3. Check that all status checks pass"
    echo "4. Verify that branch protection is working"
    echo ""
    echo "If any issues were found, run the setup script again:"
    echo "  ./scripts/setup_github_repo.sh"
}

# Run main function
main "$@" 