import json
import os
from datetime import datetime, timedelta

import pytest
import requests

# Test configuration
BASE_URL = "http://localhost:5172"
API_BASE = f"{BASE_URL}/api"


class TestAPI:
    """Comprehensive API test suite for Smart Locker System"""

    def setup_method(self):
        """Setup for each test method"""
        self.session = requests.Session()
        self.auth_token = None

    def teardown_method(self):
        """Cleanup after each test method"""
        if self.auth_token:
            # Logout if we were logged in
            try:
                self.session.post(
                    f"{API_BASE}/auth/logout",
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                )
            except:
                pass

    def login(self, username="admin", password="admin123"):
        """Login and store token"""
        response = self.session.post(
            f"{API_BASE}/auth/login", json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("token")
            return True
        return False

    def get_auth_headers(self):
        """Get headers with authentication token"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.session.get(f"{API_BASE}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data

    def test_login_success(self):
        """Test successful login"""
        response = self.session.post(
            f"{API_BASE}/auth/login", json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["username"] == "admin"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.session.post(
            f"{API_BASE}/auth/login", json={"username": "admin", "password": "wrong"}
        )
        assert response.status_code == 401

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = self.session.post(
            f"{API_BASE}/auth/login", json={"username": "admin"}
        )
        assert response.status_code == 400

    def test_logout_success(self):
        """Test successful logout"""
        # First login
        assert self.login()
        response = self.session.post(
            f"{API_BASE}/auth/logout", headers=self.get_auth_headers()
        )
        assert response.status_code == 200

    def test_logout_without_auth(self):
        """Test logout without authentication"""
        response = self.session.post(f"{API_BASE}/auth/logout")
        assert response.status_code == 401

    def test_admin_stats(self):
        """Test admin stats endpoint"""
        assert self.login()
        response = self.session.get(
            f"{API_BASE}/admin/stats", headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_lockers" in data
        assert "total_items" in data

    def test_admin_users(self):
        """Test admin users endpoint"""
        assert self.login()
        response = self.session.get(
            f"{API_BASE}/admin/users", headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        # Updated to expect dict with metadata
        assert isinstance(data, dict)
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)
        assert len(data["users"]) > 0

    def test_admin_active_borrows(self):
        """Test admin active borrows endpoint"""
        assert self.login()
        response = self.session.get(
            f"{API_BASE}/admin/active-borrows", headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        # Updated to expect dict with metadata
        assert isinstance(data, dict)
        assert "borrows" in data
        assert "total" in data
        assert isinstance(data["borrows"], list)

    def test_admin_endpoints_unauthorized(self):
        """Test admin endpoints without authentication"""
        # Test without auth token
        response = self.session.get(f"{API_BASE}/admin/stats")
        assert response.status_code == 401

        response = self.session.get(f"{API_BASE}/admin/users")
        assert response.status_code == 401

        response = self.session.get(f"{API_BASE}/admin/active-borrows")
        assert response.status_code == 401

    def test_get_lockers(self):
        """Test getting all lockers"""
        response = self.session.get(f"{API_BASE}/lockers")
        assert response.status_code == 401  # Requires authentication

    def test_get_lockers_with_auth(self):
        """Test getting lockers with authentication"""
        assert self.login()
        response = self.session.get(
            f"{API_BASE}/lockers", headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "name" in data[0]

    def test_get_items(self):
        """Test getting all items"""
        response = self.session.get(f"{API_BASE}/items")
        assert response.status_code == 401  # Requires authentication

    def test_get_items_with_auth(self):
        """Test getting items with authentication"""
        assert self.login()
        response = self.session.get(
            f"{API_BASE}/items", headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "name" in data[0]

    def test_borrow_item_success(self):
        """Test successful item borrowing"""
        assert self.login("student1", "student123")

        # Get available items first
        items_response = self.session.get(
            f"{API_BASE}/items", headers=self.get_auth_headers()
        )
        assert items_response.status_code == 200
        items = items_response.json()

        if len(items) > 0:
            # Find an available item
            available_item = None
            for item in items:
                if item.get("status") == "available":
                    available_item = item
                    break

            if available_item:
                borrow_data = {
                    "item_id": available_item["id"],
                    "user_id": 4,  # student1 user ID
                    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                }

                response = self.session.post(
                    f"{API_BASE}/borrows",
                    json=borrow_data,
                    headers=self.get_auth_headers(),
                )
                assert response.status_code == 201
                data = response.json()
                assert "borrow" in data
                assert data["borrow"]["item_id"] == available_item["id"]

    def test_borrow_item_unauthorized(self):
        """Test borrowing without authentication"""
        borrow_data = {
            "item_id": 1,
            "locker_id": 1,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
        }

        response = self.session.post(f"{API_BASE}/lockers/borrow", json=borrow_data)
        assert response.status_code == 401

    def test_return_item_success(self):
        """Test successful item return"""
        assert self.login("student1", "student123")

        # First borrow an item
        items_response = self.session.get(
            f"{API_BASE}/items", headers=self.get_auth_headers()
        )
        assert items_response.status_code == 200
        items = items_response.json()

        if len(items) > 0:
            available_item = None
            for item in items:
                if item.get("status") == "available":
                    available_item = item
                    break

            if available_item:
                # Borrow the item
                borrow_data = {
                    "item_id": available_item["id"],
                    "user_id": 4,  # student1 user ID
                    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                }

                borrow_response = self.session.post(
                    f"{API_BASE}/borrows",
                    json=borrow_data,
                    headers=self.get_auth_headers(),
                )
                assert borrow_response.status_code == 201
                borrow_data = borrow_response.json()
                borrow_id = borrow_data["borrow"]["id"]

                # Return the item
                return_data = {"condition": "good", "notes": "Test return"}

                response = self.session.post(
                    f"{API_BASE}/borrows/{borrow_id}/return",
                    json=return_data,
                    headers=self.get_auth_headers(),
                )
                assert response.status_code == 200

    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        response = self.session.get(f"{API_BASE}/invalid-endpoint")
        assert response.status_code == 404

    def test_invalid_method(self):
        """Test invalid HTTP method returns 405"""
        response = self.session.post(f"{API_BASE}/lockers")
        assert response.status_code == 405

    def test_malformed_json(self):
        """Test malformed JSON returns 400"""
        response = self.session.post(
            f"{API_BASE}/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400

    def test_health_check_performance(self):
        """Test health check performance"""
        import time

        start_time = time.time()
        response = self.session.get(f"{API_BASE}/health")
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second

    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        # Test with SQL injection attempt
        response = self.session.post(
            f"{API_BASE}/auth/login",
            json={"username": "admin' OR '1'='1", "password": "admin123"},
        )
        assert response.status_code == 401

    def test_xss_protection(self):
        """Test XSS protection in responses"""
        assert self.login()
        response = self.session.get(
            f"{API_BASE}/admin/users", headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()

        # Check that no script tags are returned
        response_text = response.text
        assert "<script>" not in response_text.lower()
        assert "javascript:" not in response_text.lower()

    # New comprehensive tests

    def test_locker_operations(self):
        """Test locker open/close operations"""
        assert self.login()

        # Get lockers
        lockers_response = self.session.get(
            f"{API_BASE}/lockers", headers=self.get_auth_headers()
        )
        assert lockers_response.status_code == 200
        lockers = lockers_response.json()

        if len(lockers) > 0:
            locker_id = lockers[0]["id"]

            # Test open locker
            open_response = self.session.post(
                f"{API_BASE}/lockers/{locker_id}/open", headers=self.get_auth_headers()
            )
            assert open_response.status_code == 200

            # Test close locker
            close_response = self.session.post(
                f"{API_BASE}/lockers/{locker_id}/close", headers=self.get_auth_headers()
            )
            assert close_response.status_code == 200

            # Test get locker status
            status_response = self.session.get(
                f"{API_BASE}/lockers/{locker_id}/status",
                headers=self.get_auth_headers(),
            )
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert "status" in status_data

    def test_item_management(self):
        """Test item management operations"""
        assert self.login()

        # Get items
        items_response = self.session.get(
            f"{API_BASE}/items", headers=self.get_auth_headers()
        )
        assert items_response.status_code == 200
        items = items_response.json()

        if len(items) > 0:
            item = items[0]
            assert "id" in item
            assert "name" in item
            assert "status" in item
            assert "category" in item

    def test_user_profile(self):
        """Test user profile endpoint"""
        assert self.login("student1", "student123")

        response = self.session.get(
            f"{API_BASE}/user/profile", headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "student1"
        assert "email" in data
        assert "role" in data

    def test_borrow_history(self):
        """Test borrow history and management"""
        assert self.login("student1", "student123")

        # Get borrows
        response = self.session.get(
            f"{API_BASE}/borrows", headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert "borrows" in data
        assert "total" in data

    def test_admin_export_endpoints(self):
        """Test admin export endpoints"""
        assert self.login()

        # Test export logs
        response = self.session.get(
            f"{API_BASE}/admin/export/logs", headers=self.get_auth_headers()
        )
        assert response.status_code == 200

        # Test export users
        response = self.session.get(
            f"{API_BASE}/admin/export/users", headers=self.get_auth_headers()
        )
        assert response.status_code == 200

        # Test export borrows
        response = self.session.get(
            f"{API_BASE}/admin/export/borrows", headers=self.get_auth_headers()
        )
        assert response.status_code == 200

    def test_rs485_test_endpoint(self):
        """Test RS485 test endpoint"""
        assert self.login()

        response = self.session.get(
            f"{API_BASE}/admin/rs485/test", headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_multiple_user_login(self):
        """Test login with different user types"""
        # Test admin login
        assert self.login("admin", "admin123")

        # Test student login
        assert self.login("student1", "student123")

        # Test manager login
        assert self.login("manager", "manager123")

    def test_invalid_token_access(self):
        """Test access with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}

        response = self.session.get(f"{API_BASE}/lockers", headers=headers)
        assert response.status_code == 401

        response = self.session.get(f"{API_BASE}/items", headers=headers)
        assert response.status_code == 401

    def test_borrow_unavailable_item(self):
        """Test borrowing an unavailable item"""
        assert self.login("student1", "student123")

        # First borrow an item to make it unavailable
        items_response = self.session.get(
            f"{API_BASE}/items", headers=self.get_auth_headers()
        )
        assert items_response.status_code == 200
        items = items_response.json()

        if len(items) > 0:
            available_item = None
            for item in items:
                if item.get("status") == "available":
                    available_item = item
                    break

            if available_item:
                # Borrow the item
                borrow_data = {
                    "item_id": available_item["id"],
                    "user_id": 4,
                    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                }

                borrow_response = self.session.post(
                    f"{API_BASE}/borrows",
                    json=borrow_data,
                    headers=self.get_auth_headers(),
                )
                assert borrow_response.status_code == 201

                # Try to borrow the same item again
                second_borrow_response = self.session.post(
                    f"{API_BASE}/borrows",
                    json=borrow_data,
                    headers=self.get_auth_headers(),
                )
                assert second_borrow_response.status_code == 400  # Should fail

    def test_return_nonexistent_borrow(self):
        """Test returning a nonexistent borrow"""
        assert self.login("student1", "student123")

        return_data = {"condition": "good", "notes": "Test return"}

        response = self.session.post(
            f"{API_BASE}/borrows/99999/return",
            json=return_data,
            headers=self.get_auth_headers(),
        )
        assert response.status_code == 404

    def test_locker_status_unauthorized(self):
        """Test locker status without authentication"""
        response = self.session.get(f"{API_BASE}/lockers/1/status")
        assert response.status_code == 401

    def test_export_without_auth(self):
        """Test export endpoints without authentication"""
        response = self.session.get(f"{API_BASE}/admin/export/logs")
        assert response.status_code == 401

        response = self.session.get(f"{API_BASE}/admin/export/users")
        assert response.status_code == 401

    def test_user_registration(self):
        """Test user registration endpoint"""
        registration_data = {
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "student",
        }

        response = self.session.post(
            f"{API_BASE}/auth/register", json=registration_data
        )
        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert "user" in data
        assert data["user"]["username"] == "testuser"

    def test_duplicate_user_registration(self):
        """Test registering duplicate username"""
        # First registration
        registration_data = {
            "username": "duplicateuser",
            "password": "testpass123",
            "email": "duplicate@example.com",
            "first_name": "Duplicate",
            "last_name": "User",
            "role": "student",
        }

        response = self.session.post(
            f"{API_BASE}/auth/register", json=registration_data
        )
        assert response.status_code == 201

        # Second registration with same username
        response = self.session.post(
            f"{API_BASE}/auth/register", json=registration_data
        )
        assert response.status_code == 400
