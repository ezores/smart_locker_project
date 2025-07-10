# Smart Locker System - Testing Guide

## Overview

This guide covers comprehensive testing strategies for the Smart Locker System, including unit tests, integration tests, end-to-end tests, and manual testing procedures.

## Testing Strategy

### Testing Pyramid

```
    /\
   /  \     E2E Tests (Few)
  /____\    Integration Tests (Some)
 /______\   Unit Tests (Many)
```

### Test Types

1. **Unit Tests** - Test individual functions and components
2. **Integration Tests** - Test API endpoints and database interactions
3. **End-to-End Tests** - Test complete user workflows
4. **Manual Tests** - User acceptance testing and exploratory testing

## Backend Testing

### Setup

1. **Install testing dependencies**

   ```bash
   pip install pytest pytest-cov pytest-mock
   ```

2. **Create test configuration**

   ```python
   # tests/conftest.py
   import pytest
   import tempfile
   import os
   from app import app, db
   from models import init_models

   @pytest.fixture
   def app():
       """Create application for testing."""
       app.config['TESTING'] = True
       app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

       with app.app_context():
           db.create_all()
           yield app
           db.drop_all()

   @pytest.fixture
   def client(app):
       """Create test client."""
       return app.test_client()

   @pytest.fixture
   def runner(app):
       """Create test runner."""
       return app.test_cli_runner()
   ```

### Unit Tests

#### Authentication Tests

```python
# tests/test_auth.py
import pytest
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

class TestAuthentication:
    def test_user_login_success(self, client):
        """Test successful user login."""
        # Create test user
        user = User(
            username='testuser',
            password_hash=generate_password_hash('password123'),
            role='student'
        )
        db.session.add(user)
        db.session.commit()

        # Test login
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert data['user']['username'] == 'testuser'

    def test_user_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/auth/login', json={
            'username': 'invalid',
            'password': 'wrong'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid username or password' in data['message']

    def test_protected_route_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get('/api/user/profile')
        assert response.status_code == 401

    def test_protected_route_with_valid_token(self, client):
        """Test accessing protected route with valid token."""
        # Create user and get token
        user = User(
            username='testuser',
            password_hash=generate_password_hash('password123'),
            role='student'
        )
        db.session.add(user)
        db.session.commit()

        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        token = login_response.get_json()['token']

        # Test protected route
        response = client.get('/api/user/profile', headers={
            'Authorization': f'Bearer {token}'
        })
        assert response.status_code == 200
```

#### Equipment Management Tests

```python
# tests/test_equipment.py
import pytest
from app import app, db
from models import User, Item, Locker, Log

class TestEquipmentManagement:
    def test_borrow_item_success(self, client):
        """Test successful item borrowing."""
        # Create test data
        user = User(username='testuser', role='student')
        item = Item(name='Test Laptop', locker_id=1)
        locker = Locker(number='A1', status='available')

        db.session.add_all([user, item, locker])
        db.session.commit()

        # Get authentication token
        token = self._get_auth_token(client, 'testuser')

        # Test borrow
        response = client.post('/api/borrow',
            json={'user_id': user.id, 'item_id': item.id, 'locker_id': locker.id},
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        assert 'borrowed successfully' in response.get_json()['message']

        # Verify log was created
        log = Log.query.filter_by(user_id=user.id, item_id=item.id).first()
        assert log is not None
        assert log.action_type == 'borrow'

    def test_return_item_success(self, client):
        """Test successful item return."""
        # Create test data with borrowed item
        user = User(username='testuser', role='student')
        item = Item(name='Test Laptop', locker_id=1)
        locker = Locker(number='A1', status='occupied')

        db.session.add_all([user, item, locker])
        db.session.commit()

        # Create borrow log
        borrow_log = Log(user_id=user.id, item_id=item.id, locker_id=locker.id, action_type='borrow')
        db.session.add(borrow_log)
        db.session.commit()

        # Get authentication token
        token = self._get_auth_token(client, 'testuser')

        # Test return
        response = client.post('/api/return',
            json={'user_id': user.id, 'item_id': item.id, 'locker_id': locker.id},
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        assert 'returned successfully' in response.get_json()['message']

    def _get_auth_token(self, client, username):
        """Helper method to get authentication token."""
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, role='student')
            db.session.add(user)
            db.session.commit()

        response = client.post('/api/auth/login', json={
            'username': username,
            'password': 'password123'
        })
        return response.get_json()['token']
```

#### Admin API Tests

```python
# tests/test_admin.py
import pytest
from app import app, db
from models import User, Item, Locker, Log

class TestAdminAPI:
    def test_admin_stats(self, client):
        """Test admin statistics endpoint."""
        # Create test data
        admin = User(username='admin', role='admin')
        user = User(username='student', role='student')
        item = Item(name='Test Item')
        locker = Locker(number='A1', status='available')

        db.session.add_all([admin, user, item, locker])
        db.session.commit()

        # Get admin token
        token = self._get_admin_token(client)

        # Test stats endpoint
        response = client.get('/api/admin/stats',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'totalUsers' in data
        assert 'totalItems' in data
        assert 'totalLockers' in data
        assert 'activeBorrows' in data

    def test_user_management(self, client):
        """Test user management endpoints."""
        token = self._get_admin_token(client)

        # Test create user
        response = client.post('/api/admin/users',
            json={
                'username': 'newuser',
                'password': 'password123',
                'role': 'student'
            },
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 201
        user_data = response.get_json()
        assert user_data['username'] == 'newuser'
        assert user_data['role'] == 'student'

        # Test get users
        response = client.get('/api/admin/users',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        users = response.get_json()
        assert len(users) > 0

    def _get_admin_token(self, client):
        """Helper method to get admin authentication token."""
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            db.session.add(admin)
            db.session.commit()

        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        return response.get_json()['token']
```

### Integration Tests

```python
# tests/test_integration.py
import pytest
from app import app, db
from models import User, Item, Locker, Log

class TestIntegration:
    def test_complete_borrow_return_workflow(self, client):
        """Test complete borrow and return workflow."""
        # Setup
        user = User(username='testuser', role='student')
        item = Item(name='Test Laptop')
        locker = Locker(number='A1', status='available')

        db.session.add_all([user, item, locker])
        db.session.commit()

        token = self._get_auth_token(client, 'testuser')
        headers = {'Authorization': f'Bearer {token}'}

        # Step 1: Borrow item
        borrow_response = client.post('/api/borrow',
            json={'user_id': user.id, 'item_id': item.id, 'locker_id': locker.id},
            headers=headers
        )
        assert borrow_response.status_code == 200

        # Verify locker status changed
        locker = Locker.query.get(locker.id)
        assert locker.status == 'occupied'

        # Step 2: Return item
        return_response = client.post('/api/return',
            json={'user_id': user.id, 'item_id': item.id, 'locker_id': locker.id},
            headers=headers
        )
        assert return_response.status_code == 200

        # Verify locker status changed back
        locker = Locker.query.get(locker.id)
        assert locker.status == 'available'

        # Step 3: Verify logs
        logs = Log.query.filter_by(user_id=user.id).all()
        assert len(logs) == 2
        assert logs[0].action_type == 'borrow'
        assert logs[1].action_type == 'return'

    def _get_auth_token(self, client, username):
        """Helper method to get authentication token."""
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, role='student')
            db.session.add(user)
            db.session.commit()

        response = client.post('/api/auth/login', json={
            'username': username,
            'password': 'password123'
        })
        return response.get_json()['token']
```

### Running Backend Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_auth.py

# Run tests with verbose output
python -m pytest -v

# Run tests and stop on first failure
python -m pytest -x
```

## Frontend Testing

### Setup

1. **Install testing dependencies**

   ```bash
   npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest
   ```

2. **Configure Jest**

   ```javascript
   // jest.config.js
   module.exports = {
     testEnvironment: "jsdom",
     setupFilesAfterEnv: ["<rootDir>/src/setupTests.js"],
     moduleNameMapping: {
       "\\.(css|less|scss|sass)$": "identity-obj-proxy",
     },
     transform: {
       "^.+\\.(js|jsx)$": "babel-jest",
     },
   };
   ```

3. **Setup test utilities**
   ```javascript
   // src/setupTests.js
   import "@testing-library/jest-dom";
   ```

### Component Tests

#### Authentication Component Tests

```javascript
// src/components/__tests__/Login.test.jsx
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../../contexts/AuthContext";
import { LanguageProvider } from "../../contexts/LanguageContext";
import Login from "../Login";

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <LanguageProvider>
        <AuthProvider>{component}</AuthProvider>
      </LanguageProvider>
    </BrowserRouter>
  );
};

describe("Login Component", () => {
  beforeEach(() => {
    // Mock fetch for API calls
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test("renders login form", () => {
    renderWithProviders(<Login />);

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /login/i })).toBeInTheDocument();
  });

  test("handles successful login", async () => {
    const mockToken = "mock-jwt-token";
    const mockUser = { id: 1, username: "testuser", role: "student" };

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ token: mockToken, user: mockUser }),
    });

    renderWithProviders(<Login />);

    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /login/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: "testuser",
          password: "password123",
        }),
      });
    });
  });

  test("handles login error", async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ message: "Invalid credentials" }),
    });

    renderWithProviders(<Login />);

    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: "wronguser" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByRole("button", { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});
```

#### Borrow Component Tests

```javascript
// src/pages/__tests__/Borrow.test.jsx
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../../contexts/AuthContext";
import { LanguageProvider } from "../../contexts/LanguageContext";
import { DarkModeProvider } from "../../contexts/DarkModeContext";
import Borrow from "../Borrow";

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <LanguageProvider>
        <DarkModeProvider>
          <AuthProvider>{component}</AuthProvider>
        </DarkModeProvider>
      </LanguageProvider>
    </BrowserRouter>
  );
};

describe("Borrow Component", () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test("renders authentication step", () => {
    renderWithProviders(<Borrow />);

    expect(screen.getByText(/authentication/i)).toBeInTheDocument();
    expect(screen.getByText(/rfid card/i)).toBeInTheDocument();
    expect(screen.getByText(/user id/i)).toBeInTheDocument();
  });

  test("allows user ID input", async () => {
    renderWithProviders(<Borrow />);

    const userIdInput = screen.getByPlaceholderText(/enter your user id/i);
    fireEvent.change(userIdInput, { target: { value: "12345" } });

    expect(userIdInput.value).toBe("12345");
  });

  test("simulates RFID scan", async () => {
    renderWithProviders(<Borrow />);

    const rfidButton = screen.getByText(/simulate rfid scan/i);
    fireEvent.click(rfidButton);

    await waitFor(() => {
      expect(screen.getByText(/select item/i)).toBeInTheDocument();
    });
  });

  test("handles item selection", async () => {
    const mockItems = [
      { id: 1, name: "Laptop", description: "Test laptop" },
      { id: 2, name: "Projector", description: "Test projector" },
    ];

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockItems,
    });

    renderWithProviders(<Borrow />);

    // Simulate RFID scan to move to item selection
    const rfidButton = screen.getByText(/simulate rfid scan/i);
    fireEvent.click(rfidButton);

    await waitFor(() => {
      expect(screen.getByText("Laptop")).toBeInTheDocument();
      expect(screen.getByText("Projector")).toBeInTheDocument();
    });
  });
});
```

### Running Frontend Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- Borrow.test.jsx

# Run tests and update snapshots
npm test -- -u
```

## End-to-End Testing

### Cypress Setup

1. **Install Cypress**

   ```bash
   npm install --save-dev cypress
   ```

2. **Configure Cypress**
   ```javascript
   // cypress.config.js
   module.exports = {
     e2e: {
       baseUrl: "http://localhost:5173",
       supportFile: "cypress/support/e2e.js",
       specPattern: "cypress/e2e/**/*.cy.{js,jsx,ts,tsx}",
     },
   };
   ```

### E2E Test Examples

```javascript
// cypress/e2e/authentication.cy.js
describe("Authentication", () => {
  beforeEach(() => {
    cy.visit("/login");
  });

  it("should login successfully with valid credentials", () => {
    cy.intercept("POST", "/api/auth/login", {
      statusCode: 200,
      body: {
        token: "mock-token",
        user: { id: 1, username: "admin", role: "admin" },
      },
    }).as("loginRequest");

    cy.get('[data-testid="username-input"]').type("admin");
    cy.get('[data-testid="password-input"]').type("admin123");
    cy.get('[data-testid="login-button"]').click();

    cy.wait("@loginRequest");
    cy.url().should("include", "/");
  });

  it("should show error with invalid credentials", () => {
    cy.intercept("POST", "/api/auth/login", {
      statusCode: 401,
      body: { message: "Invalid username or password" },
    }).as("loginRequest");

    cy.get('[data-testid="username-input"]').type("wrong");
    cy.get('[data-testid="password-input"]').type("wrong");
    cy.get('[data-testid="login-button"]').click();

    cy.wait("@loginRequest");
    cy.get('[data-testid="error-message"]').should("be.visible");
  });
});
```

```javascript
// cypress/e2e/borrow-workflow.cy.js
describe("Borrow Workflow", () => {
  beforeEach(() => {
    // Login before each test
    cy.login("admin", "admin123");
  });

  it("should complete borrow workflow", () => {
    cy.visit("/borrow");

    // Step 1: Authentication
    cy.get('[data-testid="user-id-input"]').type("12345");
    cy.get('[data-testid="continue-button"]').click();

    // Step 2: Item selection
    cy.get('[data-testid="item-card"]').first().click();

    // Step 3: Locker selection
    cy.get('[data-testid="locker-card"]').first().click();

    // Step 4: Confirmation
    cy.get('[data-testid="confirm-borrow-button"]').click();

    // Verify success
    cy.get('[data-testid="success-message"]').should("be.visible");
  });
});
```

### Running E2E Tests

```bash
# Open Cypress UI
npx cypress open

# Run tests in headless mode
npx cypress run

# Run specific test file
npx cypress run --spec "cypress/e2e/authentication.cy.js"
```

## Manual Testing

### Test Cases Checklist

#### Authentication

- [ ] Login with valid admin credentials
- [ ] Login with valid student credentials
- [ ] Login with invalid credentials
- [ ] Logout functionality
- [ ] Session timeout handling
- [ ] Password validation

#### Equipment Borrowing

- [ ] RFID card authentication
- [ ] User ID authentication
- [ ] Item selection
- [ ] Locker selection
- [ ] Borrow confirmation
- [ ] Success/error messages
- [ ] Progress indicators

#### Equipment Returning

- [ ] Return item selection
- [ ] Return confirmation
- [ ] Success/error messages
- [ ] Locker status update

#### Admin Functions

- [ ] Dashboard statistics
- [ ] User management (CRUD)
- [ ] Item management (CRUD)
- [ ] Locker management (CRUD)
- [ ] Activity logs
- [ ] Report generation
- [ ] Export functionality

#### Internationalization

- [ ] Language switching
- [ ] Text translation accuracy
- [ ] Date/time formatting
- [ ] Number formatting

#### Dark Mode

- [ ] Theme switching
- [ ] Text readability
- [ ] Component styling
- [ ] Persistent theme preference

### Browser Compatibility Testing

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

### Performance Testing

- [ ] Page load times
- [ ] API response times
- [ ] Large dataset handling
- [ ] Memory usage
- [ ] Network efficiency

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          python -m pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v1

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 16

      - name: Install dependencies
        run: npm install

      - name: Run tests
        run: npm test -- --coverage --watchAll=false

      - name: Upload coverage
        uses: codecov/codecov-action@v1

  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 16

      - name: Install dependencies
        run: npm install

      - name: Start backend
        run: |
          pip install -r requirements.txt
          python app.py --port 5050 &

      - name: Start frontend
        run: npm run dev &

      - name: Wait for servers
        run: |
          npx wait-on http://localhost:5050
          npx wait-on http://localhost:5173

      - name: Run E2E tests
        run: npx cypress run
```

## Test Data Management

### Fixtures

```python
# tests/fixtures.py
import pytest
from models import User, Item, Locker

@pytest.fixture
def sample_users():
    """Create sample users for testing."""
    users = [
        User(username='admin', role='admin'),
        User(username='student1', role='student'),
        User(username='student2', role='student'),
    ]
    return users

@pytest.fixture
def sample_items():
    """Create sample items for testing."""
    items = [
        Item(name='Laptop Dell XPS 13'),
        Item(name='Projector Epson'),
        Item(name='Microphone Blue Yeti'),
    ]
    return items

@pytest.fixture
def sample_lockers():
    """Create sample lockers for testing."""
    lockers = [
        Locker(number='A1', status='available'),
        Locker(number='A2', status='occupied'),
        Locker(number='B1', status='maintenance'),
    ]
    return lockers
```

### Database Seeding

```python
# tests/seed_data.py
def seed_test_database(db):
    """Seed database with test data."""
    # Create users
    admin = User(username='admin', role='admin')
    student = User(username='student', role='student')

    # Create items
    laptop = Item(name='Test Laptop')
    projector = Item(name='Test Projector')

    # Create lockers
    locker1 = Locker(number='A1', status='available')
    locker2 = Locker(number='A2', status='occupied')

    db.session.add_all([admin, student, laptop, projector, locker1, locker2])
    db.session.commit()

    return {
        'admin': admin,
        'student': student,
        'laptop': laptop,
        'projector': projector,
        'locker1': locker1,
        'locker2': locker2,
    }
```

## Best Practices

### Test Organization

- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests independent and isolated

### Test Data

- Use factories for creating test data
- Clean up test data after each test
- Use meaningful test data
- Avoid hardcoded values

### Mocking

- Mock external dependencies
- Mock time-dependent operations
- Mock network requests
- Use realistic mock data

### Coverage

- Aim for 80%+ code coverage
- Focus on critical business logic
- Test error conditions
- Test edge cases

### Performance

- Keep tests fast
- Use database transactions for rollback
- Avoid unnecessary setup/teardown
- Use parallel test execution when possible
