# Smart Locker System - Testing Guide

This guide provides comprehensive information about testing the Smart Locker System, including automated test suites, manual testing procedures, and troubleshooting techniques.

## Overview

The Smart Locker System includes multiple testing layers to ensure reliability and functionality:

- **Backend Unit Tests**: Python-based unit testing with pytest
- **Backend Integration Tests**: API and database integration testing
- **Model Tests**: Database model validation and testing
- **Automated UI Tests**: Puppeteer-based end-to-end testing
- **API Testing**: Direct endpoint testing with curl
- **Integration Testing**: Full workflow validation

## Backend Testing

### Prerequisites

Before running backend tests, ensure:

1. **Python Environment**: Activate virtual environment

   ```bash
   source .venv/bin/activate
   ```

2. **Test Dependencies**: Install pytest and testing libraries

   ```bash
   pip install pytest pytest-cov requests
   ```

3. **Database Setup**: Ensure PostgreSQL is running with test data
   ```bash
   ./start.sh --demo --reset-db --verbose
   ```

### Running Backend Tests

#### Complete Backend Test Suite

Run all backend tests:

```bash
cd backend
python -m pytest -v --cov=. --cov-report=html
```

This will execute:

- Authentication tests
- API endpoint tests
- Model validation tests
- Integration tests
- Utility function tests

#### Individual Test Modules

Test specific backend functionality:

```bash
# Authentication tests
python test_auth_comprehensive.py

# API tests
python -m pytest tests/test_api.py -v

# Logging tests
python test_logging.py

# Basic functionality tests
python -m pytest tests/test_basic.py -v
```

#### Test with Coverage Report

Generate detailed coverage reports:

```bash
cd backend
python -m pytest --cov=. --cov-report=html --cov-report=term-missing
```

This creates an HTML coverage report in `htmlcov/index.html`

### Backend Test Structure

#### Authentication Tests (`test_auth_comprehensive.py`)

Comprehensive authentication system testing:

```python
# Test user registration
python -c "
import test_auth_comprehensive
test_auth_comprehensive.run_comprehensive_auth_tests()
"
```

**Test Coverage:**

- User registration with valid/invalid data
- Duplicate username/student ID handling
- Login with valid/invalid credentials
- JWT token validation
- Logout functionality
- Session management
- Error handling and logging

#### API Tests (`tests/test_api.py`)

API endpoint testing with pytest:

```bash
# Run specific API test
python -m pytest tests/test_api.py::TestAPI::test_health_check -v

# Run all API tests
python -m pytest tests/test_api.py -v
```

**Test Coverage:**

- Health check endpoint
- Authentication endpoints (login/logout)
- Admin endpoints (stats, users, borrows)
- Locker management endpoints
- Item management endpoints
- Borrow/return workflows
- Security testing (SQL injection, XSS)
- Performance testing
- Error handling

#### Logging Tests (`test_logging.py`)

System logging functionality testing:

```bash
python test_logging.py
```

**Test Coverage:**

- Log file creation and writing
- Log level filtering
- Log rotation
- Error logging
- Activity logging
- Performance logging

#### Basic Tests (`tests/test_basic.py`)

Core functionality testing:

```bash
python -m pytest tests/test_basic.py -v
```

**Test Coverage:**

- Database connection
- Model instantiation
- Basic CRUD operations
- Configuration loading
- Environment variable handling

### Model Testing

#### Database Model Tests

Test database models and relationships:

```python
# Create model test file: backend/tests/test_models.py
import pytest
from models import User, Locker, Item, Log, Borrow, Payment, Reservation

class TestModels:
    def test_user_creation(self):
        """Test user model creation and validation"""
        user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="student"
        )
        user.set_password("password123")
        assert user.username == "testuser"
        assert user.check_password("password123")
        assert user.role == "student"

    def test_locker_creation(self):
        """Test locker model creation"""
        locker = Locker(
            name="Test Locker",
            number="L001",
            location="Test Location",
            status="active"
        )
        assert locker.name == "Test Locker"
        assert locker.status == "active"

    def test_reservation_creation(self):
        """Test reservation model creation"""
        from datetime import datetime, timedelta

        reservation = Reservation(
            reservation_code="RES001",
            user_id=1,
            locker_id=1,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status="active"
        )
        assert reservation.reservation_code == "RES001"
        assert reservation.status == "active"
```

#### Database Integration Tests

Test database operations and relationships:

```python
# Create integration test file: backend/tests/test_database.py
import pytest
from app import app, db
from models import User, Locker, Reservation

class TestDatabaseIntegration:
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_user:test_pass@localhost/test_db'

        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()

    def test_user_locker_reservation_workflow(self, client):
        """Test complete user-locker-reservation workflow"""
        # Create user
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Create locker
        locker = Locker(name="Test Locker", number="L001")
        db.session.add(locker)
        db.session.commit()

        # Create reservation
        reservation = Reservation(
            user_id=user.id,
            locker_id=locker.id,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=1)
        )
        db.session.add(reservation)
        db.session.commit()

        # Verify relationships
        assert user.reservations[0].locker_id == locker.id
        assert locker.reservations[0].user_id == user.id
```

### Utility Function Testing

#### Export Function Tests

Test data export functionality:

```python
# Create utility test file: backend/tests/test_utils.py
import pytest
from utils.export import export_data_csv, export_data_excel, export_data_pdf

class TestExportUtils:
    def test_csv_export(self):
        """Test CSV export functionality"""
        test_data = [
            {"name": "Test User", "email": "test@example.com"},
            {"name": "Another User", "email": "another@example.com"}
        ]

        csv_content = export_data_csv(test_data)
        assert "Test User" in csv_content
        assert "test@example.com" in csv_content
        assert csv_content.startswith("name,email")

    def test_excel_export(self):
        """Test Excel export functionality"""
        test_data = [
            {"name": "Test User", "email": "test@example.com"}
        ]

        excel_content = export_data_excel(test_data)
        assert len(excel_content) > 0
        # Excel files start with specific bytes
        assert excel_content.startswith(b'PK')

    def test_pdf_export(self):
        """Test PDF export functionality"""
        test_data = [
            {"name": "Test User", "email": "test@example.com"}
        ]

        pdf_content = export_data_pdf("Test Report", [{"title": "Users", "content": test_data}])
        assert len(pdf_content) > 0
        # PDF files start with specific bytes
        assert pdf_content.startswith(b'%PDF')
```

#### RS485 Communication Tests

Test hardware communication:

```python
# Create RS485 test file: backend/tests/test_rs485.py
import pytest
from utils.rs485 import open_locker, close_locker, get_locker_status

class TestRS485:
    def test_open_locker_command(self):
        """Test locker open command"""
        result = open_locker(1, address=1, locker_number=1)
        assert isinstance(result, dict)
        assert "status" in result

    def test_close_locker_command(self):
        """Test locker close command"""
        result = close_locker(1, address=1, locker_number=1)
        assert isinstance(result, dict)
        assert "status" in result

    def test_get_locker_status(self):
        """Test locker status retrieval"""
        result = get_locker_status(1)
        assert isinstance(result, dict)
        assert "status" in result
```

### Backend Test Configuration

#### pytest Configuration

Create `backend/pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

#### Test Environment Setup

Create `backend/conftest.py`:

```python
import pytest
import os
import tempfile
from app import app, db
from models import User, Locker

@pytest.fixture(scope='session')
def app_config():
    """Configure test application"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_user:test_pass@localhost/test_db'
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture(scope='function')
def client(app_config):
    """Create test client"""
    with app_config.test_client() as client:
        with app_config.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def test_user():
    """Create test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role="student"
    )
    user.set_password("password123")
    return user

@pytest.fixture
def test_locker():
    """Create test locker"""
    locker = Locker(
        name="Test Locker",
        number="L001",
        location="Test Location",
        status="active"
    )
    return locker
```

### Backend Test Execution

#### Running Tests with Different Options

```bash
# Run all tests with coverage
cd backend
python -m pytest --cov=. --cov-report=html --cov-report=term

# Run only unit tests
python -m pytest -m "unit" -v

# Run only integration tests
python -m pytest -m "integration" -v

# Run tests excluding slow tests
python -m pytest -m "not slow" -v

# Run specific test file
python -m pytest tests/test_api.py -v

# Run specific test method
python -m pytest tests/test_api.py::TestAPI::test_health_check -v

# Run tests with detailed output
python -m pytest -v -s

# Run tests in parallel (if pytest-xdist installed)
python -m pytest -n auto
```

#### Test Output Examples

Successful test execution produces:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.6, pytest-7.4.0, pluggy-1.6.0
rootdir: /path/to/smart_locker_project/backend
plugins: cov-4.1.0
collected 45 items

tests/test_api.py::TestAPI::test_health_check PASSED                    [  2%]
tests/test_api.py::TestAPI::test_login_success PASSED                  [  4%]
tests/test_api.py::TestAPI::test_login_invalid_credentials PASSED      [  6%]
...
tests/test_auth_comprehensive.py::TestAuthenticationSystem::test_01_health_check PASSED [ 88%]
tests/test_auth_comprehensive.py::TestAuthenticationSystem::test_02_register_new_user PASSED [ 90%]
...
tests/test_logging.py::TestLogging::test_log_creation PASSED           [ 95%]
tests/test_logging.py::TestLogging::test_log_levels PASSED             [ 97%]
tests/test_logging.py::TestLogging::test_log_rotation PASSED           [100%]

============================== 45 passed in 12.34s ==============================

---------- coverage: platform darwin, python 3.12.6-final-0 -----------
Name                           Stmts   Miss  Cover
--------------------------------------------------
app.py                           156     12    92%
models.py                        245     18    93%
utils/export.py                   45      3    93%
utils/rs485.py                    32      5    84%
--------------------------------------------------
TOTAL                           478     38    92%
```

### Backend Test Best Practices

#### Test Organization

- **Test Files**: One test file per module/component
- **Test Classes**: Group related tests in classes
- **Test Methods**: Use descriptive test method names
- **Fixtures**: Use pytest fixtures for common setup

#### Test Data Management

- **Test Database**: Use separate test database
- **Data Isolation**: Each test should be independent
- **Cleanup**: Always clean up test data
- **Fixtures**: Use fixtures for common test data

#### Test Coverage

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **API Tests**: Test HTTP endpoints
- **Model Tests**: Test database models and relationships

#### Performance Testing

```python
# Performance test example
import time
import pytest

def test_api_response_time():
    """Test API response time"""
    start_time = time.time()
    response = requests.get("http://localhost:5050/api/health")
    end_time = time.time()

    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # Response time under 1 second
```

## Automated Test Suite

### Prerequisites

Before running automated tests, ensure:

1. **System is Running**: Start the system with demo data

   ```bash
   ./start.sh --demo --reset-db --verbose
   ```

2. **Node.js Environment**: Verify Node.js installation

   ```bash
   node --version  # Should be 16+
   npm --version   # Should be 8+
   ```

3. **Test Dependencies**: Install test dependencies
   ```bash
   cd frontend
   npm install puppeteer
   cd ..
   ```

### Running Tests

#### Complete Test Suite

Run all automated tests:

```bash
node tests/run_all_tests.js
```

This will execute:

- Authentication flow tests
- Reservation management tests
- Locker management tests
- Admin dashboard tests
- Items management tests

#### Individual Module Tests

Test specific functionality:

```bash
# Authentication flow
node tests/test_auth_flow.js

# Reservation system
node tests/test_reservations.js

# Locker management
node tests/test_lockers.js

# Admin dashboard
node tests/test_admin_dashboard.js

# Items management
node tests/test_items.js
```

### Test Output

Successful test execution produces:

```
Starting Comprehensive Smart Locker System Tests
==================================================

Running Authentication Flow...
──────────────────────────────────────────────────
Loaded frontend page
Login form found
Tested invalid login
Login successful
Session persistence verified
Logout successful
Protected route redirect after logout
Authentication flow tests completed successfully!

Running Reservations Module...
──────────────────────────────────────────────────
Logged in successfully
Navigated to reservations page
New reservation modal opened
Created new reservation
Edit modal opened
Updated reservation
Canceled reservation
Tested search functionality
Tested date filtering
Reservations module tests completed successfully!

Test Results Summary
=======================
Total Tests: 5
Passed: 5
Failed: 0
Success Rate: 100.0%

All tests passed! The Smart Locker System is working correctly.
```

### Test Coverage

#### Authentication Flow Tests

- **Login Process**: Valid and invalid credentials
- **Session Management**: Token persistence and validation
- **Logout Process**: Proper session termination
- **Protected Routes**: Access control verification
- **Error Handling**: Invalid input responses

#### Reservation Tests

- **Creation**: New reservation with validation
- **Editing**: Modify existing reservations
- **Cancellation**: Proper reservation termination
- **Conflict Detection**: Overlapping reservation handling
- **Search and Filter**: Data retrieval functionality

#### Locker Management Tests

- **Status Display**: Current locker availability
- **Filtering**: Status-based filtering
- **Search**: Text-based search functionality
- **Sorting**: Multiple sort criteria
- **Pagination**: Large dataset handling

#### Admin Dashboard Tests

- **User Management**: Create, edit, delete users
- **Reports Generation**: Data export functionality
- **System Settings**: Configuration management
- **Logs Access**: System activity monitoring
- **Statistics Display**: Dashboard metrics

#### Items Management Tests

- **Borrowing Process**: Item checkout workflow
- **Return Process**: Item check-in workflow
- **Inventory Management**: Add, edit, delete items
- **Status Tracking**: Item availability monitoring
- **Search and Filter**: Item discovery tools

## API Testing

### Manual API Testing with curl

#### Authentication

```bash
# Login and get token
curl -X POST http://localhost:5172/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Expected response:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "user": {"id": 1, "username": "admin", "role": "admin"}
# }
```

#### Health Check

```bash
# System health verification
curl http://localhost:5172/api/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-07-10T21:15:00Z"}
```

#### Locker Management

```bash
# Get all lockers
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5172/api/lockers

# Get specific locker
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5172/api/lockers/1

# Update locker status
curl -X PUT http://localhost:5172/api/lockers/1/status \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "maintenance"}'
```

#### Reservation Management

```bash
# Create reservation
curl -X POST http://localhost:5172/api/reservations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "locker_id": 1,
    "start_time": "2025-07-15T10:00:00Z",
    "end_time": "2025-07-16T10:00:00Z",
    "notes": "Test reservation"
  }'

# Get user reservations
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5172/api/reservations

# Update reservation
curl -X PUT http://localhost:5172/api/reservations/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Updated reservation notes"
  }'

# Cancel reservation
curl -X DELETE http://localhost:5172/api/reservations/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### User Management (Admin Only)

```bash
# List all users
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:5172/api/users

# Create new user
curl -X POST http://localhost:5172/api/users \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User",
    "role": "user",
    "password": "password123"
  }'

# Update user
curl -X PUT http://localhost:5172/api/users/2 \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name"
  }'
```

#### Items Management

```bash
# Get all items
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5172/api/items

# Borrow item
curl -X POST http://localhost:5172/api/items/1/borrow \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "borrower_id": 1,
    "expected_return": "2025-07-20T18:00:00Z",
    "notes": "Test borrow"
  }'

# Return item
curl -X POST http://localhost:5172/api/items/1/return \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "return_notes": "Item returned in good condition"
  }'
```

### Automated API Testing Script

Create a comprehensive API test script:

```bash
#!/bin/bash

# API Test Script
BASE_URL="http://localhost:5172"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="admin123"

echo "Starting API Tests..."

# Get authentication token
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$ADMIN_USERNAME\",\"password\":\"$ADMIN_PASSWORD\"}" \
  | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "Authentication failed"
    exit 1
fi

echo "Authentication successful"

# Test health endpoint
HEALTH=$(curl -s "$BASE_URL/api/health")
echo "Health check: $HEALTH"

# Test lockers endpoint
LOCKERS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/lockers")
echo "Lockers count: $(echo $LOCKERS | jq 'length')"

# Test reservations endpoint
RESERVATIONS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/reservations")
echo "Reservations count: $(echo $RESERVATIONS | jq 'length')"

echo "API tests completed"
```

## Manual Testing Procedures

### User Interface Testing

#### Login Page

1. **Valid Login**: Use correct credentials
2. **Invalid Login**: Test wrong username/password
3. **Empty Fields**: Submit form without data
4. **Session Persistence**: Refresh page after login

#### Main Menu

1. **Navigation**: Click all menu items
2. **Responsive Design**: Test on different screen sizes
3. **Dark Mode**: Toggle theme switch
4. **Language Switch**: Change interface language

#### Reservations Page

1. **Create Reservation**: Fill form and submit
2. **Edit Reservation**: Modify existing reservation
3. **Cancel Reservation**: Remove reservation
4. **Search/Filter**: Test data filtering
5. **Validation**: Test date/time constraints

#### Lockers Page

1. **Locker Display**: Verify all lockers shown
2. **Status Indicators**: Check status colors
3. **Filtering**: Test status filters
4. **Search**: Test text search
5. **Sorting**: Test sort options

#### Admin Dashboard

1. **User Management**: Create/edit/delete users
2. **Reports**: Generate various reports
3. **System Settings**: Modify configurations
4. **Logs**: View system activity
5. **Statistics**: Check dashboard metrics

### Cross-Browser Testing

Test the application in multiple browsers:

- **Chrome**: Latest version
- **Firefox**: Latest version
- **Safari**: Latest version (macOS)
- **Edge**: Latest version (Windows)

### Mobile Testing

Test responsive design on:

- **iOS Safari**: iPhone/iPad
- **Android Chrome**: Various screen sizes
- **Tablet Browsers**: iPad, Android tablets

## Performance Testing

### Load Testing

Test system performance under load:

```bash
# Install Apache Bench
# macOS: brew install httpd
# Ubuntu: sudo apt install apache2-utils

# Test backend API
ab -n 1000 -c 10 http://localhost:5172/api/health

# Test frontend
ab -n 1000 -c 10 http://localhost:5173/
```

### Database Performance

Monitor database performance:

```bash
# Check PostgreSQL performance
psql -d smart_locker_db -c "SELECT * FROM pg_stat_activity;"

# Monitor slow queries
psql -d smart_locker_db -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

## Troubleshooting

### Common Test Failures

#### Authentication Failures

```bash
# Check if backend is running
curl http://localhost:5172/api/health

# Verify database connection
psql $DATABASE_URL -c "SELECT 1;"

# Check user exists
psql $DATABASE_URL -c "SELECT username FROM users WHERE username='admin';"
```

#### Frontend Test Failures

```bash
# Check if frontend is running
curl http://localhost:5173/

# Verify Node.js dependencies
cd frontend && npm install

# Check Puppeteer installation
node -e "require('puppeteer')"
```

#### Database Connection Issues

```bash
# Start PostgreSQL
brew services start postgresql@14  # macOS
sudo systemctl start postgresql    # Linux

# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Verify database exists
psql -U postgres -l | grep smart_locker_db
```

### Debug Mode

Enable verbose logging for debugging:

```bash
# Start with verbose logging
./start.sh --demo --reset-db --verbose

# Check backend logs
tail -f backend/logs/app.log

# Check frontend logs
# Monitor browser console in development tools
```

### Test Environment Reset

Reset test environment completely:

```bash
# Stop all services
pkill -f "python.*app.py"
pkill -f "node.*vite"

# Reset database
psql -U postgres -c "DROP DATABASE IF EXISTS smart_locker_db;"
psql -U postgres -c "CREATE DATABASE smart_locker_db OWNER smart_locker_user;"

# Restart with fresh data
./start.sh --demo --reset-db --verbose
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Smart Locker Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: smart_locker_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          cd frontend && npm install && cd ..

      - name: Setup database
        run: |
          export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/smart_locker_db"
          cd backend
          python app.py --reset-db --minimal

      - name: Start backend
        run: |
          export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/smart_locker_db"
          cd backend
          python app.py --minimal &
          sleep 10

      - name: Start frontend
        run: |
          cd frontend
          npm run dev &
          sleep 10

      - name: Run tests
        run: |
          node tests/run_all_tests.js
```

## Best Practices

### Test Organization

- **Modular Tests**: Separate tests by functionality
- **Clear Naming**: Use descriptive test names
- **Independent Tests**: Each test should be self-contained
- **Proper Cleanup**: Clean up test data after each test

### Test Data Management

- **Consistent Data**: Use predictable test data
- **Isolation**: Tests should not interfere with each other
- **Reset Strategy**: Clear data between test runs
- **Demo Data**: Use comprehensive demo data for testing

### Error Handling

- **Graceful Failures**: Handle errors appropriately
- **Detailed Logging**: Log test execution details
- **Timeout Handling**: Set appropriate timeouts
- **Retry Logic**: Implement retry for flaky tests

### Performance Considerations

- **Test Speed**: Optimize test execution time
- **Resource Usage**: Monitor memory and CPU usage
- **Parallel Execution**: Run independent tests in parallel
- **Caching**: Cache dependencies and test data

## Reporting

### Test Reports

Generate comprehensive test reports:

```bash
# Run tests with detailed output
node tests/run_all_tests.js > test_report.txt 2>&1

# Generate HTML report (if using Jest)
npm test -- --coverage --coverageReporters=html
```

### Metrics Tracking

Track test metrics over time:

- **Test Coverage**: Percentage of code covered
- **Execution Time**: Time to run complete test suite
- **Success Rate**: Percentage of passing tests
- **Flaky Tests**: Tests that fail intermittently

## Conclusion

This testing guide provides a comprehensive approach to ensuring the Smart Locker System's reliability and functionality. Regular testing helps maintain system quality and catch issues early in the development cycle.

For additional support or questions about testing, refer to the main documentation or contact the development team.
