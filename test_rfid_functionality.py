#!/usr/bin/env python3
"""
Test script for RFID functionality in Smart Locker System
Tests user creation, update, and retrieval with RFID tags
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5050"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login_admin():
    """Login as admin and return JWT token"""
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        response.raise_for_status()
        data = response.json()
        return data["token"]
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_create_user_with_rfid(token):
    """Test creating a user with RFID tag"""
    print("Testing user creation with RFID...")
    
    user_data = {
        "username": "rfid_test_user",
        "password": "testpass123",
        "role": "student",
        "rfid_tag": "RFID_TEST_001"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=user_data
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"User created successfully: {data['user']['username']}")
        print(f"   RFID Tag: {data['user']['rfid_tag']}")
        print(f"   User ID: {data['user']['id']}")
        
        return data['user']['id']
    except Exception as e:
        print(f"User creation failed: {e}")
        return None

def test_update_user_rfid(token, user_id):
    """Test updating a user's RFID tag"""
    print(f"\nTesting RFID update for user {user_id}...")
    
    update_data = {
        "rfid_tag": "RFID_TEST_002"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=update_data
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"User updated successfully")
        print(f"   New RFID Tag: {data['user']['rfid_tag']}")
        
        return True
    except Exception as e:
        print(f"User update failed: {e}")
        return False

def test_get_users_with_rfid(token):
    """Test retrieving users list with RFID tags"""
    print("\nTesting users list retrieval with RFID...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        data = response.json()
        
        users_with_rfid = [user for user in data['users'] if user.get('rfid_tag')]
        print(f"Retrieved {len(data['users'])} users")
        print(f"   Users with RFID tags: {len(users_with_rfid)}")
        
        # Show first few users with RFID
        for user in users_with_rfid[:3]:
            print(f"   - {user['username']}: {user['rfid_tag']}")
        
        return True
    except Exception as e:
        print(f"Users retrieval failed: {e}")
        return False

def test_duplicate_rfid_validation(token):
    """Test that duplicate RFID tags are rejected"""
    print("\nTesting duplicate RFID validation...")
    
    user_data = {
        "username": "duplicate_test_user",
        "password": "testpass123",
        "role": "student",
        "rfid_tag": "RFID_TEST_002"  # Same as updated test user
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=user_data
        )
        
        if response.status_code == 400:
            print("Duplicate RFID correctly rejected")
            return True
        else:
            print(f"Duplicate RFID should have been rejected, got status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Duplicate RFID test failed: {e}")
        return False

def main():
    """Run all RFID functionality tests"""
    print("Testing RFID Functionality in Smart Locker System")
    print("=" * 60)
    
    # Login as admin
    token = login_admin()
    if not token:
        print("Cannot proceed without admin token")
        sys.exit(1)
    
    print("Admin login successful")
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Create user with RFID
    user_id = test_create_user_with_rfid(token)
    if user_id:
        tests_passed += 1
    
    # Test 2: Update user RFID
    if test_update_user_rfid(token, user_id):
        tests_passed += 1
    
    # Test 3: Get users with RFID
    if test_get_users_with_rfid(token):
        tests_passed += 1
    
    # Test 4: Duplicate RFID validation
    if test_duplicate_rfid_validation(token):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("All RFID functionality tests passed!")
        print("\nRFID functionality is working correctly:")
        print("   - Users can be created with RFID tags")
        print("   - RFID tags can be updated")
        print("   - RFID tags are included in user lists")
        print("   - Duplicate RFID tags are properly validated")
    else:
        print("Some tests failed. Please check the implementation.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 