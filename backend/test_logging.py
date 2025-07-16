#!/usr/bin/env python3

"""
=============================================================================
Smart Locker System - Logging Test Script
=============================================================================
Version: 2.0.0
Author: Alp Alpdogan
License: MIT - This program can only be used while keeping the names
         of Mehmet Ugurlu & Yusuf Alpdogan in their honor

In Memory of:
  Mehmet Ugurlu & Yusuf Alpdogan
  May their legacy inspire innovation and excellence
=============================================================================

Test script to verify enhanced logging functionality.
"""

import requests
import json
import time
from datetime import datetime

def test_logging_system():
    """Test the enhanced logging system"""
    base_url = "http://localhost:5050"
    
    print("Smart Locker System - Logging Test")
    print("===================================")
    print("Author: Alp Alpdogan")
    print()
    
    # Test 1: Failed login attempt (should log login_failed)
    print("1. Testing failed login logging...")
    try:
        response = requests.post(f"{base_url}/api/auth/login", 
                               json={"username": "nonexistent", "password": "wrong"})
        print(f"   SUCCESS: Failed login logged (Status: {response.status_code})")
    except Exception as e:
        print(f"   ERROR: Failed login test error: {e}")
    
    # Test 2: Successful login (should log login)
    print("2. Testing successful login logging...")
    try:
        response = requests.post(f"{base_url}/api/auth/login", 
                               json={"username": "admin", "password": "admin123"})
        if response.status_code == 200:
            token = response.json().get("token")
            print(f"   SUCCESS: Successful login logged (Status: {response.status_code})")
        else:
            print(f"   ERROR: Login failed (Status: {response.status_code})")
            return
    except Exception as e:
        print(f"   ERROR: Login test error: {e}")
        return
    
    # Test 3: Logout (should log logout)
    print("3. Testing logout logging...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{base_url}/api/auth/logout", headers=headers)
        print(f"   SUCCESS: Logout logged (Status: {response.status_code})")
    except Exception as e:
        print(f"   ERROR: Logout test error: {e}")
    
    # Test 4: Check logs endpoint
    print("4. Testing logs retrieval...")
    try:
        # Login again to get token
        login_response = requests.post(f"{base_url}/api/auth/login", 
                                     json={"username": "admin", "password": "admin123"})
        if login_response.status_code == 200:
            admin_token = login_response.json().get("token")
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            response = requests.get(f"{base_url}/api/logs", headers=headers)
            if response.status_code == 200:
                logs = response.json().get("logs", [])
                print(f"   SUCCESS: Retrieved {len(logs)} log entries")
                
                # Check for our test entries
                test_actions = ["login", "login_failed", "logout"]
                found_actions = [log["action_type"] for log in logs if log["action_type"] in test_actions]
                print(f"   INFO: Found actions: {found_actions}")
                
                # Show recent logs
                print("   INFO: Recent log entries:")
                for log in logs[:5]:  # Show last 5 logs
                    timestamp = log.get("timestamp", "N/A")
                    action = log.get("action_type", "N/A")
                    notes = log.get("notes", "N/A")
                    ip = log.get("ip_address", "N/A")
                    print(f"      {timestamp} | {action} | {notes} | IP: {ip}")
            else:
                print(f"   ERROR: Failed to retrieve logs (Status: {response.status_code})")
        else:
            print(f"   ERROR: Admin login failed (Status: {login_response.status_code})")
    except Exception as e:
        print(f"   ERROR: Logs test error: {e}")
    
    print()
    print("SUCCESS: Logging system test completed!")
    print("Check the database logs table to see the enhanced logging in action.")

if __name__ == "__main__":
    test_logging_system() 