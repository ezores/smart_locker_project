#!/usr/bin/env python3
"""
Smart Locker System - Comprehensive Integration Test
Tests RS485 protocol, database connection, demo data, and system functionality
"""

import requests
import json
import sys
import time
from datetime import datetime

def test_rs485_protocol():
    """Test RS485 checksum calculation and dipswitch numbering logic"""
    print("Testing RS485 Protocol...")
    print("=" * 50)
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from utils.rs485 import generate_rs485_frame
        
        # Test cases: (address, locker, expected_frame)
        test_cases = [
            (0, 1, '5A5A0000000400010104'),
            (1, 2, '5A5A0001000400010206'),
            (31, 24, '5A5A001F000400011802'),
            (15, 12, '5A5A000F000400010C06'),
            (1, 14, '5A5A0001000400010E0A'),  # Example from user query
            (5, 8, '5A5A0005000400010808'),
            (10, 20, '5A5A000A00040001141B'),
            (20, 15, '5A5A0014000400010F1E'),
        ]
        
        all_passed = True
        
        for address, locker, expected in test_cases:
            frame = generate_rs485_frame(address, locker)
            passed = frame == expected
            status = 'PASS' if passed else 'FAIL'
            print(f'Address {address}, Locker {locker}: {frame} {status}')
            if not passed:
                print(f'  Expected: {expected}')
                print(f'  Got:      {frame}')
                all_passed = False
        
        print()
        print(f'RS485 Controller Test: {all_passed}')
        
        # Test the specific example from user query
        example_frame = generate_rs485_frame(1, 14)
        print(f'Generated Frame: {example_frame}')
        
        return all_passed
        
    except Exception as e:
        print(f"RS485 test failed: {e}")
        return False

def test_database_connection():
    """Test database connection and health"""
    print("\nTesting Database Connection...")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5050/api/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"Database Status: {health_data['database']}")
            print(f"System Status: {health_data['status']}")
            return True
        else:
            print(f"Database health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def test_demo_data():
    """Test demo data correctness"""
    print("\nTesting Demo Data...")
    print("=" * 50)
    
    try:
        # Login to get token
        login_data = {'username': 'admin', 'password': 'admin123'}
        response = requests.post('http://localhost:5050/api/auth/login', json=login_data, timeout=5)
        if response.status_code != 200:
            print("Failed to login for demo data test")
            return False
        
        token = response.json().get('token')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get items
        response = requests.get('http://localhost:5050/api/items', headers=headers, timeout=5)
        if response.status_code != 200:
            print("Failed to get items")
            return False
        
        items = response.json()
        print(f"Found {len(items)} items")
        
        # Check serial numbers
        demo_serials = 0
        non_demo_serials = 0
        
        for item in items:
            serial = item.get('serial_number')
            if serial:
                if serial.startswith('demo_'):
                    demo_serials += 1
                else:
                    non_demo_serials += 1
        
        print(f"Demo serials: {demo_serials}")
        print(f"Non-demo serials: {non_demo_serials}")
        
        # All serial numbers should have demo_ prefix or be null
        if non_demo_serials == 0:
            print("All serial numbers have demo_ prefix")
            return True
        else:
            print(f"Warning: {non_demo_serials} items have non-demo serial numbers")
            return False
            
    except Exception as e:
        print(f"Demo data test failed: {e}")
        return False

def test_startup_script():
    """Test that startup script works correctly"""
    print("\nTesting Startup Script...")
    print("=" * 50)
    
    try:
        # Test backend
        response = requests.get('http://localhost:5050/api/health', timeout=5)
        backend_running = response.status_code == 200
        
        # Test frontend
        response = requests.get('http://localhost:5173', timeout=5)
        frontend_running = response.status_code == 200
        
        print(f"Backend: {'RUNNING' if backend_running else 'NOT RUNNING'}")
        print(f"Frontend: {'RUNNING' if frontend_running else 'NOT RUNNING'}")
        
        return backend_running and frontend_running
        
    except Exception as e:
        print(f"Startup script test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("Smart Locker System - Integration Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    tests = [
        ("RS485 Protocol", test_rs485_protocol),
        ("Database Connection", test_database_connection),
        ("Demo Data", test_demo_data),
        ("Startup Script", test_startup_script),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\nIntegration test completed!")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\nOverall Result: {'PASS' if all_passed else 'FAIL'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 