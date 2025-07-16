#!/usr/bin/env python3

"""
=============================================================================
Smart Locker System - Comprehensive Authentication Tests
=============================================================================
Version: 2.0.0
Author: Alp Alpdogan
License: MIT - This program can only be used while keeping the names
         of Mehmet Ugurlu & Yusuf Alpdogan in their honor

In Memory of:
  Mehmet Ugurlu & Yusuf Alpdogan
  May their legacy inspire innovation and excellence
=============================================================================

Comprehensive test suite for login and register functionality.
"""

import requests
import json
import time
import unittest
from datetime import datetime

class TestAuthenticationSystem(unittest.TestCase):
    """Comprehensive authentication system tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5050"
        self.test_user = {
            "username": "testuser_auth",
            "password": "TestPass123!",
            "email": "testauth@example.com",
            "first_name": "Test",
            "last_name": "User",
            "student_id": "2024AUTH001",
            "role": "student"
        }
        
    def test_01_health_check(self):
        """Test if the server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/health")
            self.assertEqual(response.status_code, 200)
            print("SUCCESS: Server health check passed")
        except Exception as e:
            self.fail(f"Server health check failed: {e}")
    
    def test_02_register_new_user(self):
        """Test user registration with valid data"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=self.test_user
            )
            
            if response.status_code == 201:
                data = response.json()
                self.assertIn("message", data)
                self.assertIn("user", data)
                self.assertEqual(data["user"]["username"], self.test_user["username"])
                print("SUCCESS: User registration with valid data")
            else:
                # User might already exist, which is also acceptable
                data = response.json()
                if "Username already exists" in data.get("error", ""):
                    print("INFO: User already exists (expected for repeated tests)")
                else:
                    self.fail(f"Registration failed: {data}")
                    
        except Exception as e:
            self.fail(f"Registration test error: {e}")
    
    def test_03_register_duplicate_username(self):
        """Test registration with duplicate username"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=self.test_user
            )
            
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("Username already exists", data["error"])
            print("SUCCESS: Duplicate username registration properly rejected")
            
        except Exception as e:
            self.fail(f"Duplicate username test error: {e}")
    
    def test_04_register_duplicate_student_id(self):
        """Test registration with duplicate student ID"""
        duplicate_user = self.test_user.copy()
        duplicate_user["username"] = "different_username"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=duplicate_user
            )
            
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("Student ID already exists", data["error"])
            print("SUCCESS: Duplicate student ID registration properly rejected")
            
        except Exception as e:
            self.fail(f"Duplicate student ID test error: {e}")
    
    def test_05_register_missing_required_fields(self):
        """Test registration with missing required fields"""
        incomplete_user = {"username": "incomplete"}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=incomplete_user
            )
            
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("Username and password required", data["error"])
            print("SUCCESS: Missing required fields properly rejected")
            
        except Exception as e:
            self.fail(f"Missing fields test error: {e}")
    
    def test_06_login_valid_user(self):
        """Test login with valid credentials"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": self.test_user["username"],
                    "password": self.test_user["password"]
                }
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("token", data)
            self.assertIn("user", data)
            self.assertEqual(data["user"]["username"], self.test_user["username"])
            print("SUCCESS: Valid user login")
            return data["token"]
            
        except Exception as e:
            self.fail(f"Valid login test error: {e}")
    
    def test_07_login_invalid_password(self):
        """Test login with wrong password"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": self.test_user["username"],
                    "password": "wrongpassword"
                }
            )
            
            self.assertEqual(response.status_code, 401)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("Invalid password", data["error"])
            print("SUCCESS: Invalid password properly rejected")
            
        except Exception as e:
            self.fail(f"Invalid password test error: {e}")
    
    def test_08_login_nonexistent_user(self):
        """Test login with non-existent user"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": "nonexistentuser",
                    "password": "anypassword"
                }
            )
            
            self.assertEqual(response.status_code, 401)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("User not found", data["error"])
            print("SUCCESS: Non-existent user properly rejected")
            
        except Exception as e:
            self.fail(f"Non-existent user test error: {e}")
    
    def test_09_login_missing_fields(self):
        """Test login with missing fields"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "testuser"}
            )
            
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("Username and password required", data["error"])
            print("SUCCESS: Missing login fields properly rejected")
            
        except Exception as e:
            self.fail(f"Missing login fields test error: {e}")
    
    def test_10_logout_functionality(self):
        """Test logout functionality"""
        # First login to get token
        login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["token"]
            
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.post(
                    f"{self.base_url}/api/auth/logout",
                    headers=headers
                )
                
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn("message", data)
                self.assertIn("Logged out successfully", data["message"])
                print("SUCCESS: Logout functionality works")
                
            except Exception as e:
                self.fail(f"Logout test error: {e}")
        else:
            self.fail("Could not login to test logout")
    
    def test_11_jwt_token_validation(self):
        """Test JWT token validation"""
        # First login to get token
        login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["token"]
            
            try:
                # Test valid token
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    f"{self.base_url}/api/user/profile",
                    headers=headers
                )
                
                self.assertEqual(response.status_code, 200)
                print("SUCCESS: Valid JWT token accepted")
                
                # Test invalid token
                invalid_headers = {"Authorization": "Bearer invalid_token"}
                response = requests.get(
                    f"{self.base_url}/api/user/profile",
                    headers=invalid_headers
                )
                
                self.assertEqual(response.status_code, 401)
                print("SUCCESS: Invalid JWT token properly rejected")
                
            except Exception as e:
                self.fail(f"JWT validation test error: {e}")
        else:
            self.fail("Could not login to test JWT validation")
    
    def test_12_logging_verification(self):
        """Test that authentication events are properly logged"""
        try:
            # Login as admin to check logs
            admin_response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            
            if admin_response.status_code == 200:
                admin_token = admin_response.json()["token"]
                headers = {"Authorization": f"Bearer {admin_token}"}
                
                # Get logs
                logs_response = requests.get(
                    f"{self.base_url}/api/logs",
                    headers=headers
                )
                
                if logs_response.status_code == 200:
                    logs = logs_response.json().get("logs", [])
                    
                    # Check for authentication-related logs
                    auth_actions = ["login", "login_failed", "logout", "register", "register_failed"]
                    auth_logs = [log for log in logs if log.get("action_type") in auth_actions]
                    
                    self.assertGreater(len(auth_logs), 0, "No authentication logs found")
                    print(f"SUCCESS: Found {len(auth_logs)} authentication log entries")
                    
                    # Check for IP address and user agent in logs
                    logs_with_ip = [log for log in auth_logs if log.get("ip_address")]
                    logs_with_ua = [log for log in auth_logs if log.get("user_agent")]
                    
                    self.assertGreater(len(logs_with_ip), 0, "No logs with IP addresses found")
                    self.assertGreater(len(logs_with_ua), 0, "No logs with user agents found")
                    print("SUCCESS: Logs contain IP addresses and user agents")
                    
                else:
                    self.fail("Could not retrieve logs")
            else:
                self.fail("Could not login as admin to check logs")
                
        except Exception as e:
            self.fail(f"Logging verification test error: {e}")

def run_comprehensive_auth_tests():
    """Run all comprehensive authentication tests"""
    print("Smart Locker System - Comprehensive Authentication Tests")
    print("=======================================================")
    print("Author: Alp Alpdogan")
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAuthenticationSystem)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\nSUCCESS: All authentication tests passed!")
    else:
        print("\nERROR: Some authentication tests failed!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_comprehensive_auth_tests() 