#!/usr/bin/env python3
"""
Test script to verify RFID conflict warning functionality
Tests both user creation and user update scenarios
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
        
        if response.status_code == 200:
            return response.json().get("token")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_rfid_conflict_creation(token):
    """Test RFID conflict during user creation"""
    print("\n🔍 Testing RFID conflict during user creation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, create a user with a specific RFID
    user1_data = {
        "username": "testuser1_rfid",
        "password": "password123",
        "role": "student",
        "rfid_tag": "RFID_CONFLICT_TEST"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/admin/users", 
                               json=user1_data, headers=headers)
        
        if response.status_code == 201:
            print("✅ Created first user with RFID")
            user1_id = response.json().get("user", {}).get("id")
        else:
            print(f"❌ Failed to create first user: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating first user: {e}")
        return False
    
    # Now try to create another user with the same RFID
    user2_data = {
        "username": "testuser2_rfid",
        "password": "password123",
        "role": "student",
        "rfid_tag": "RFID_CONFLICT_TEST"  # Same RFID
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/admin/users", 
                               json=user2_data, headers=headers)
        
        if response.status_code == 201:
            response_data = response.json()
            if "warning" in response_data:
                print("✅ RFID conflict warning received during creation")
                print(f"   Warning: {response_data['warning']}")
                return True
            else:
                print("❌ No warning received for RFID conflict during creation")
                return False
        else:
            print(f"❌ Failed to create second user: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating second user: {e}")
        return False

def test_rfid_conflict_update(token):
    """Test RFID conflict during user update"""
    print("\n🔍 Testing RFID conflict during user update...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create two users with different RFIDs
    user1_data = {
        "username": "updateuser1_rfid",
        "password": "password123",
        "role": "student",
        "rfid_tag": "RFID_UPDATE_TEST_1"
    }
    
    user2_data = {
        "username": "updateuser2_rfid",
        "password": "password123",
        "role": "student",
        "rfid_tag": "RFID_UPDATE_TEST_2"
    }
    
    try:
        # Create first user
        response = requests.post(f"{BASE_URL}/api/admin/users", 
                               json=user1_data, headers=headers)
        if response.status_code != 201:
            print(f"❌ Failed to create first user: {response.status_code}")
            return False
        user1_id = response.json().get("user", {}).get("id")
        print("✅ Created first user")
        
        # Create second user
        response = requests.post(f"{BASE_URL}/api/admin/users", 
                               json=user2_data, headers=headers)
        if response.status_code != 201:
            print(f"❌ Failed to create second user: {response.status_code}")
            return False
        user2_id = response.json().get("user", {}).get("id")
        print("✅ Created second user")
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        return False
    
    # Now try to update the second user to use the first user's RFID
    update_data = {
        "rfid_tag": "RFID_UPDATE_TEST_1"  # Same as first user
    }
    
    try:
        response = requests.put(f"{BASE_URL}/api/admin/users/{user2_id}", 
                              json=update_data, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            if "warning" in response_data:
                print("✅ RFID conflict warning received during update")
                print(f"   Warning: {response_data['warning']}")
                return True
            else:
                print("❌ No warning received for RFID conflict during update")
                return False
        else:
            print(f"❌ Failed to update user: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        return False

def cleanup_test_users(token):
    """Clean up test users"""
    print("\n🧹 Cleaning up test users...")
    
    headers = {"Authorization": f"Bearer {token}"}
    test_usernames = [
        "testuser1_rfid", "testuser2_rfid",
        "updateuser1_rfid", "updateuser2_rfid"
    ]
    
    # Get all users
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users?limit=1000", headers=headers)
        if response.status_code == 200:
            users = response.json().get("users", [])
            
            for user in users:
                if user.get("username") in test_usernames:
                    user_id = user.get("id")
                    delete_response = requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=headers)
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted test user: {user.get('username')}")
                    else:
                        print(f"❌ Failed to delete user: {user.get('username')}")
        else:
            print("❌ Failed to get users for cleanup")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def main():
    print("🚀 Testing RFID Conflict Warning Functionality")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print("❌ Backend server is not running")
            print("Please start the backend server first")
            return
        print("✅ Backend server is running")
    except Exception as e:
        print("❌ Cannot connect to backend server")
        print("Please start the backend server first")
        return
    
    # Login as admin
    token = login_admin()
    if not token:
        print("❌ Failed to login as admin")
        return
    
    print("✅ Admin login successful")
    
    # Run tests
    creation_success = test_rfid_conflict_creation(token)
    update_success = test_rfid_conflict_update(token)
    
    # Cleanup
    cleanup_test_users(token)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   User Creation RFID Conflict: {'✅ PASS' if creation_success else '❌ FAIL'}")
    print(f"   User Update RFID Conflict: {'✅ PASS' if update_success else '❌ FAIL'}")
    
    if creation_success and update_success:
        print("\n🎉 All tests passed! RFID conflict warnings are working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 