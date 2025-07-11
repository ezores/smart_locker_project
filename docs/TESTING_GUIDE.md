# Smart Locker System - Testing Guide

This guide provides comprehensive information about testing the Smart Locker System, including automated test suites, manual testing procedures, and troubleshooting techniques.

## Overview

The Smart Locker System includes multiple testing layers to ensure reliability and functionality:

- **Automated UI Tests**: Puppeteer-based end-to-end testing
- **API Testing**: Direct endpoint testing with curl
- **Unit Testing**: Backend component testing
- **Integration Testing**: Full workflow validation

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
