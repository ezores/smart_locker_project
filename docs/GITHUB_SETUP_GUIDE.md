# GitHub Repository Setup Guide

This guide explains how to configure your GitHub repository with branch protection, CI/CD pipelines, and security features for the Smart Locker Project.

## Overview

The setup includes:

- **Branch Protection**: Prevents direct pushes to main branch, requires PR reviews
- **CI/CD Pipeline**: Automated testing for backend and frontend
- **Security Features**: Secret scanning, Dependabot, vulnerability alerts
- **Code Quality**: Automated linting and code formatting checks
- **Issue Management**: Templates and labels for better project management

## Prerequisites

1. **GitHub CLI**: Install the GitHub CLI tool

   ```bash
   # macOS
   brew install gh

   # Ubuntu/Debian
   sudo apt install gh

   # Windows
   winget install GitHub.cli
   ```

2. **Authentication**: Login to GitHub CLI

   ```bash
   gh auth login
   ```

3. **Repository Access**: Ensure you have admin access to the repository

## Quick Setup

Run the automated setup script:

```bash
./scripts/setup_github_repo.sh
```

This script will configure all the settings described below automatically.

## Manual Setup Process

If you prefer to set up manually or understand each step, follow these sections:

### 1. Repository Settings

Update repository description and topics:

```bash
gh repo edit --description "Smart Locker Management System with Flask backend and React frontend" \
              --add-topic smart-locker,iot,flask,react,postgresql,management-system
```

### 2. Branch Protection Rules

#### Main Branch Protection

Protect the main branch to require:

- Pull request reviews (minimum 1 approval)
- Status checks to pass
- No direct pushes
- Conversation resolution

```bash
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
```

#### Develop Branch Protection

Create and protect a develop branch for feature development:

```bash
# Create develop branch
git checkout -b develop
git push -u origin develop

# Protect develop branch
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
```

### 3. CI/CD Pipeline Configuration

The CI/CD pipeline is defined in `.github/workflows/ci-cd.yml` and includes:

#### Jobs Overview

1. **Backend Tests**: Python tests with PostgreSQL database
2. **Frontend Tests**: React/Node.js tests with coverage
3. **Integration Tests**: End-to-end testing with both servers running
4. **Security Scan**: Bandit for Python, npm audit for Node.js
5. **Code Quality**: Linting and formatting checks
6. **Build and Test**: Production build verification

#### Status Checks Required

For main branch merges, these status checks must pass:

- `backend-tests`
- `frontend-tests`
- `integration-tests`
- `security-scan`
- `code-quality`
- `build-and-test`

For develop branch merges:

- `backend-tests`
- `frontend-tests`
- `integration-tests`
- `security-scan`
- `code-quality`

### 4. Security Features

Enable security scanning and dependency updates:

```bash
gh api repos/:owner/:repo/security-and-analysis \
    --method PUT \
    --field security_and_analysis='{"secret_scanning":{"status":"enabled"},"secret_scanning_push_protection":{"status":"enabled"},"dependabot_security_updates":{"status":"enabled"},"dependabot_version_updates":{"status":"enabled"}}'
```

### 5. Dependabot Configuration

Create `.github/dependabot.yml` for automated dependency updates:

```yaml
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
```

### 6. Issue Templates

Create issue templates for better project management:

#### Bug Report Template

Location: `.github/ISSUE_TEMPLATE/bug_report.md`

#### Feature Request Template

Location: `.github/ISSUE_TEMPLATE/feature_request.md`

### 7. Pull Request Template

Create a comprehensive PR template:
Location: `.github/pull_request_template.md`

### 8. CODEOWNERS File

Define code ownership for automatic review requests:
Location: `.github/CODEOWNERS`

### 9. Repository Labels

Create standard labels for issue management:

```bash
gh api repos/:owner/:repo/labels --method POST --field name="bug" --field color="d73a4a" --field description="Something isn't working"
gh api repos/:owner/:repo/labels --method POST --field name="enhancement" --field color="a2eeef" --field description="New feature or request"
gh api repos/:owner/:repo/labels --method POST --field name="documentation" --field color="0075ca" --field description="Improvements or additions to documentation"
gh api repos/:owner/:repo/labels --method POST --field name="good first issue" --field color="7057ff" --field description="Good for newcomers"
gh api repos/:owner/:repo/labels --method POST --field name="help wanted" --field color="008672" --field description="Extra attention is needed"
gh api repos/:owner/:repo/labels --method POST --field name="priority: high" --field color="ff0000" --field description="High priority issue"
gh api repos/:owner/:repo/labels --method POST --field name="priority: medium" --field color="ffa500" --field description="Medium priority issue"
gh api repos/:owner/:repo/labels --method POST --field name="priority: low" --field color="00ff00" --field description="Low priority issue"
```

### 10. Actions Permissions

Configure Actions to allow selected actions only:

```bash
gh api repos/:owner/:repo/actions/permissions \
    --method PUT \
    --field allowed_actions="selected" \
    --field github_owned_allowed=true \
    --field verified_allowed=true
```

## Workflow Explanation

### Branch Protection Rules

1. **Required Status Checks**: All CI/CD jobs must pass
2. **Required Reviews**: At least 1 approval required
3. **Dismiss Stale Reviews**: Reviews are dismissed when new commits are pushed
4. **Conversation Resolution**: All conversations must be resolved
5. **No Force Pushes**: Prevents destructive operations
6. **No Deletions**: Protects against accidental branch deletion

### CI/CD Pipeline Jobs

#### Backend Tests

- Sets up PostgreSQL database
- Installs Python dependencies
- Runs pytest with coverage
- Uploads coverage reports

#### Frontend Tests

- Installs Node.js dependencies
- Runs Jest tests with coverage
- Uploads coverage reports

#### Integration Tests

- Runs after backend and frontend tests
- Starts both servers
- Runs end-to-end tests
- Tests comprehensive scenarios

#### Security Scan

- Runs Bandit for Python security issues
- Runs npm audit for Node.js vulnerabilities
- Fails on moderate or higher issues

#### Code Quality

- Runs flake8, black, isort for Python
- Runs ESLint for JavaScript
- Ensures code formatting standards

#### Build and Test

- Only runs on PRs to main branch
- Builds production frontend
- Tests production build
- Creates summary report

## Testing the Setup

1. **Push Configuration**: Push the `.github` directory to your repository
2. **Create Test PR**: Create a pull request to test the CI/CD pipeline
3. **Verify Checks**: Ensure all status checks pass
4. **Test Protection**: Try to push directly to main (should be blocked)
5. **Test Reviews**: Ensure PR requires approval

## Troubleshooting

### Common Issues

1. **Status Checks Not Running**

   - Ensure the workflow file is in the correct location
   - Check that the branch protection rules reference the correct check names

2. **Permission Denied**

   - Ensure you have admin access to the repository
   - Check that GitHub CLI is authenticated

3. **Workflow Failures**

   - Check the Actions tab for detailed error messages
   - Verify that all dependencies are correctly specified

4. **Branch Protection Not Working**
   - Ensure the branch exists before applying protection
   - Check that the protection rules are correctly formatted

### Debugging Commands

```bash
# Check repository settings
gh repo view

# Check branch protection
gh api repos/:owner/:repo/branches/main/protection

# Check Actions permissions
gh api repos/:owner/:repo/actions/permissions

# List workflows
gh api repos/:owner/:repo/actions/workflows
```

## Best Practices

1. **Regular Updates**: Keep dependencies updated via Dependabot
2. **Security Monitoring**: Review security alerts regularly
3. **Code Reviews**: Always require at least one review
4. **Testing**: Ensure all tests pass before merging
5. **Documentation**: Keep documentation updated with changes

## Advanced Configuration

### Custom Status Checks

You can add custom status checks by modifying the workflow file and updating branch protection rules.

### Team-Based Reviews

For larger teams, you can configure team-based review requirements:

```bash
gh api repos/:owner/:repo/branches/main/protection \
    --method PUT \
    --field required_pull_request_reviews='{"required_approving_review_count":2,"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"require_last_push_approval":false}'
```

### Environment-Specific Deployments

You can add deployment environments for staging and production:

```yaml
# In workflow file
deploy:
  needs: [build-and-test]
  environment: production
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to production
      run: echo "Deploy to production"
```

## Conclusion

This setup provides a robust foundation for collaborative development with:

- Automated testing and quality checks
- Security scanning and dependency management
- Clear review and approval processes
- Professional project management tools

The configuration ensures code quality and security while maintaining efficient development workflows.
