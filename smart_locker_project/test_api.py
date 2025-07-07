#!/usr/bin/env python3
"""
Test script for Smart Locker API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8080"

def test_login():
    """Test the login endpoint"""
    print("Testing login endpoint...")
    
    # Test admin login
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful! Token: {data.get('token', 'No token')[:20]}...")
        return data.get('token')
    else:
        print("❌ Login failed!")
        return None

def test_items(token=None):
    """Test the items endpoint"""
    print("\nTesting items endpoint...")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(f"{BASE_URL}/api/items", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

def test_lockers(token=None):
    """Test the lockers endpoint"""
    print("\nTesting lockers endpoint...")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(f"{BASE_URL}/api/lockers", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    print("🧪 Testing Smart Locker API...")
    print("=" * 50)
    
    # Test login first
    token = test_login()
    
    # Test other endpoints
    test_items(token)
    test_lockers(token)
    
    print("\n" + "=" * 50)
    print("✅ API testing complete!") 