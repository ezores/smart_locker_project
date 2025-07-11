#!/bin/bash

# Smart Locker Project - GitHub Repository Setup Script
# This script helps configure GitHub repository settings, branch protection, and CI/CD

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

# Setup repository settings
setup_repository() {
    print_status "Setting up repository settings..."
    
    # Update repository description and topics
    gh repo edit --description "Smart Locker Management System with Flask backend and React frontend" \
                  --add-topic smart-locker,iot,flask,react,postgresql,management-system
    
    print_success "Repository settings updated"
}

# Setup branch protection for main branch
setup_branch_protection() {
    print_status "Setting up branch protection for main branch..."
    
    # Enable branch protection for main branch
    gh api repos/:owner/:repo/branches/main/protection \
        --method PUT \
        --field required_status_checks='{"strict":true,"contexts":["backend-tests","frontend-tests","integration-tests","security-scan","code-quality","build-and-test"]}' \
        --field enforce_admins=false \
        --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"require_last_push_approval":false}' \
        --field restrictions='{"users":[],"teams":[],"apps":[]}' \
        --field required_linear_history=false \
        --field allow_force_pushes=false \
        --field allow_deletions=false \
        --field block_creations=false \
        --field required_conversation_resolution=true
    
    print_success "Branch protection enabled for main branch"
}

# Setup branch protection for develop branch
setup_develop_branch() {
    print_status "Setting up branch protection for develop branch..."
    
    # Create develop branch if it doesn't exist
    if ! git show-ref --verify --quiet refs/remotes/origin/develop; then
        print_status "Creating develop branch..."
        git checkout -b develop
        git push -u origin develop
    fi
    
    # Enable branch protection for develop branch
    gh api repos/:owner/:repo/branches/develop/protection \
        --method PUT \
        --field required_status_checks='{"strict":true,"contexts":["backend-tests","frontend-tests","integration-tests","security-scan","code-quality"]}' \
        --field enforce_admins=false \
        --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"require_last_push_approval":false}' \
        --field restrictions='{"users":[],"teams":[],"apps":[]}' \
        --field required_linear_history=false \
        --field allow_force_pushes=false \
        --field allow_deletions=false \
        --field block_creations=false \
        --field required_conversation_resolution=true
    
    print_success "Branch protection enabled for develop branch"
}

# Setup security features
setup_security() {
    print_status "Setting up security features..."
    
    # Enable secret scanning
    gh api repos/:owner/:repo/security-and-analysis \
        --method PUT \
        --field security_and_analysis='{"secret_scanning":{"status":"enabled"},"secret_scanning_push_protection":{"status":"enabled"},"dependabot_security_updates":{"status":"enabled"},"dependabot_version_updates":{"status":"enabled"}}'
    
    print_success "Security features enabled"
}

# Setup Dependabot
setup_dependabot() {
    print_status "Setting up Dependabot..."
    
    # Create Dependabot configuration
    cat > .github/dependabot.yml << EOF
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "UTC"
    open-pull-requests-limit: 10
    reviewers:
      - "ezores"
    assignees:
      - "ezores"
    commit-message:
      prefix: "deps"
      prefix-development: "deps-dev"
      include: "scope"

  # Node.js dependencies
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "UTC"
    open-pull-requests-limit: 10
    reviewers:
      - "ezores"
    assignees:
      - "ezores"
    commit-message:
      prefix: "deps"
      prefix-development: "deps-dev"
      include: "scope"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "UTC"
    open-pull-requests-limit: 10
    reviewers:
      - "ezores"
    assignees:
      - "ezores"
    commit-message:
      prefix: "deps"
      include: "scope"
EOF
    
    print_success "Dependabot configuration created"
}

# Setup issue templates
setup_issue_templates() {
    print_status "Setting up issue templates..."
    
    # Create issue templates directory
    mkdir -p .github/ISSUE_TEMPLATE
    
    # Bug report template
    cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: ['bug']
assignees: ['ezores']
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. macOS, Windows, Linux]
- Browser: [e.g. Chrome, Safari, Firefox]
- Version: [e.g. 22]

**Additional context**
Add any other context about the problem here.
EOF

    # Feature request template
    cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: ['enhancement']
assignees: ['ezores']
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
EOF
    
    print_success "Issue templates created"
}

# Setup labels
setup_labels() {
    print_status "Setting up repository labels..."
    
    # Create labels
    gh api repos/:owner/:repo/labels --method POST --field name="bug" --field color="d73a4a" --field description="Something isn't working"
    gh api repos/:owner/:repo/labels --method POST --field name="enhancement" --field color="a2eeef" --field description="New feature or request"
    gh api repos/:owner/:repo/labels --method POST --field name="documentation" --field color="0075ca" --field description="Improvements or additions to documentation"
    gh api repos/:owner/:repo/labels --method POST --field name="good first issue" --field color="7057ff" --field description="Good for newcomers"
    gh api repos/:owner/:repo/labels --method POST --field name="help wanted" --field color="008672" --field description="Extra attention is needed"
    gh api repos/:owner/:repo/labels --method POST --field name="priority: high" --field color="ff0000" --field description="High priority issue"
    gh api repos/:owner/:repo/labels --method POST --field name="priority: medium" --field color="ffa500" --field description="Medium priority issue"
    gh api repos/:owner/:repo/labels --method POST --field name="priority: low" --field color="00ff00" --field description="Low priority issue"
    
    print_success "Repository labels created"
}

# Setup Actions permissions
setup_actions_permissions() {
    print_status "Setting up Actions permissions..."
    
    # Set Actions permissions to allow selected actions
    gh api repos/:owner/:repo/actions/permissions \
        --method PUT \
        --field allowed_actions="selected" \
        --field github_owned_allowed=true \
        --field verified_allowed=true
    
    print_success "Actions permissions configured"
}

# Main function
main() {
    echo "Smart Locker Project - GitHub Repository Setup"
    echo "=============================================="
    echo ""
    
    # Check prerequisites
    check_gh_cli
    check_gh_auth
    
    print_status "Starting GitHub repository setup..."
    
    # Setup all components
    setup_repository
    setup_branch_protection
    setup_develop_branch
    setup_security
    setup_dependabot
    setup_issue_templates
    setup_labels
    setup_actions_permissions
    
    echo ""
    print_success "GitHub repository setup completed successfully!"
    echo ""
    echo "What was configured:"
    echo "✅ Repository description and topics"
    echo "✅ Branch protection for main and develop branches"
    echo "✅ Required status checks for CI/CD"
    echo "✅ Required pull request reviews (1 approval minimum)"
    echo "✅ Security scanning and Dependabot"
    echo "✅ Issue templates for bugs and feature requests"
    echo "✅ Repository labels"
    echo "✅ Actions permissions"
    echo ""
    echo "Next steps:"
    echo "1. Push the .github directory to your repository"
    echo "2. Create a pull request to test the CI/CD pipeline"
    echo "3. Review and merge the pull request"
    echo ""
    echo "The CI/CD pipeline will run on every push and pull request."
    echo "All tests must pass before merging to main branch."
}

# Run main function
main "$@" 