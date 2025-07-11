#!/usr/bin/env python3

import requests
import json
import sys

def test_backend():
    """Test if the backend is running and has lockers and reservations"""
    
    base_url = "http://localhost:5172"
    
    # Test 1: Health check
    print("Testing backend health...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running on localhost:5172")
        return False
    
    # Test 2: Login to get token
    print("Testing authentication...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        print(f"Login response: {response.text}")
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data keys: {list(response_data.keys())}")
            token = response_data.get("token")
            print("✅ Authentication successful")
            print(f"Token: {token[:20]}..." if token else "No token received")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    if not token:
        print("❌ No token received from login response!")
        return False
    
    # Test 3: Get lockers with token
    print("Testing lockers endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Using headers: {headers}")
        response = requests.get(f"{base_url}/api/lockers", headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        if response.status_code == 200:
            lockers = response.json()
            print(f"✅ Found {len(lockers)} lockers")
            for locker in lockers[:5]:  # Show first 5 lockers
                print(f"  - {locker['name']} ({locker['number']}) - Status: {locker['status']}")
            if len(lockers) > 5:
                print(f"  ... and {len(lockers) - 5} more")
        else:
            print(f"❌ Lockers endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Lockers endpoint error: {e}")
        return False

    # Test 4: Get reservations with token
    print("Testing reservations endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/api/reservations", headers=headers)
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            reservations = response.json().get("reservations")
            if reservations is None:
                # fallback for list response
                reservations = response.json()
            print(f"✅ Found {len(reservations)} reservations")
            for reservation in reservations[:5]:
                print(f"  - Reservation {reservation.get('reservation_code')} for locker {reservation.get('locker_name')} from {reservation.get('start_time')} to {reservation.get('end_time')}")
            if len(reservations) > 5:
                print(f"  ... and {len(reservations) - 5} more")
            return True
        else:
            print(f"❌ Reservations endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Reservations endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Smart Locker Backend...")
    print("=" * 50)
    
    success = test_backend()
    
    print("=" * 50)
    if success:
        print("✅ All tests passed! Backend is working correctly.")
        sys.exit(0)
    else:
        print("❌ Tests failed. Please check the backend.")
        print("\nTroubleshooting tips:")
        print("1. Make sure the backend is running: ./start.sh")
        print("2. Check if PostgreSQL is running")
        print("3. Check if demo data is loaded")
        print("4. Check backend logs for errors")
        sys.exit(1) 