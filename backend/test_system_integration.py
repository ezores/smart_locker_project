#!/usr/bin/env python3
"""
Comprehensive System Integration Test
Tests all the fixes: database password, demo data serial numbers, RS485 protocol
"""

import requests
import json
import time
from utils.rs485 import generate_rs485_frame, RS485Controller

def test_rs485_protocol():
    """Test RS485 protocol implementation"""
    print("Testing RS485 Protocol...")
    print("=" * 50)
    
    # Test frame generation with various parameters
    test_cases = [
        (0, 1, "5A5A0000000400010104"),
        (1, 2, "5A5A0001000400010206"),
        (31, 24, "5A5A001F000400011802"),
        (15, 12, "5A5A000F000400010C06"),
    ]
    
    for address, locker, expected in test_cases:
        result = generate_rs485_frame(address, locker)
        status = "PASS" if result == expected else "FAIL"
        print(f"Address {address}, Locker {locker}: {result} {status}")
        if result != expected:
            print(f"  Expected: {expected}")
    
    # Test RS485 controller
    controller = RS485Controller()
    result = controller.open_locker(1, 0, 1)
    print(f"\nRS485 Controller Test: {result['success']}" if result['success'] else "FAIL")
    print(f"Generated Frame: {result['frame']}")
    
    print()

def test_database_connection():
    """Test database connection without password prompt"""
    print("Testing Database Connection...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5050/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Database Status: {data['database']}")
            print(f"System Status: {data['status']}")
        else:
            print(f"Health check failed: {response.status_code}")
    except Exception as e:
        print(f"Connection failed: {e}")
    
    print()

def test_demo_data():
    """Test that demo data has correct serial numbers"""
    print("Testing Demo Data...")
    print("=" * 50)
    
    try:
        # Test login to get token
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post("http://localhost:5050/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            token = response.json().get("token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get items
            response = requests.get("http://localhost:5050/api/items", headers=headers)
            if response.status_code == 200:
                items = response.json()
                print(f"Found {len(items)} items")
                
                # Check serial numbers
                demo_serial_count = 0
                non_demo_serial_count = 0
                
                for item in items[:10]:  # Check first 10 items
                    serial = item.get("serial_number", "")
                    if serial and serial.startswith("demo_"):
                        demo_serial_count += 1
                    elif serial:
                        non_demo_serial_count += 1
                        print(f"  Non-demo serial: {serial}")
                
                print(f"Demo serials: {demo_serial_count}")
                print(f"Non-demo serials: {non_demo_serial_count}")
                
                if non_demo_serial_count == 0:
                    print("All serial numbers have demo_ prefix")
                else:
                    print("Some serial numbers missing demo_ prefix")
            else:
                print(f"Failed to get items: {response.status_code}")
        else:
            print(f"Login failed: {response.status_code}")
            
    except Exception as e:
        print(f"Demo data test failed: {e}")
    
    print()

def test_startup_script():
    """Test that startup script works without password prompts"""
    print("Testing Startup Script...")
    print("=" * 50)
    
    # Check if services are running
    services = [
        ("Backend", "http://localhost:5050/api/health"),
        ("Frontend", "http://localhost:5173"),
    ]
    
    for service_name, url in services:
        try:
            if service_name == "Frontend":
                response = requests.get(url, timeout=5)
                status = "RUNNING" if response.status_code == 200 else "NOT RUNNING"
            else:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    status = f"RUNNING ({data['status']})"
                else:
                    status = "NOT RUNNING"
        except Exception as e:
            status = f"ERROR: {e}"
        
        print(f"{service_name}: {status}")
    
    print()

def main():
    """Run all tests"""
    print("Smart Locker System - Comprehensive Integration Test")
    print("=" * 60)
    print()
    
    test_rs485_protocol()
    test_database_connection()
    test_demo_data()
    test_startup_script()
    
    print("Integration test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main() 