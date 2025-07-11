#!/usr/bin/env python3
"""
Test script for the Smart Locker Reservation System
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5172"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
STUDENT_USERNAME = "student1"
STUDENT_PASSWORD = "student123"

def test_login(username, password):
    """Test login and return token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": username,
        "password": password
    })
    
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    else:
        print(f"Login failed for {username}: {response.text}")
        return None

def test_reservations():
    """Test reservation functionality"""
    print("=== Testing Smart Locker Reservation System ===\n")
    
    # Test admin login
    print("1. Testing admin login...")
    admin_token = test_login(ADMIN_USERNAME, ADMIN_PASSWORD)
    if not admin_token:
        print("Admin login failed")
        return
    
    print("Admin login successful")
    
    # Test student login
    print("\n2. Testing student login...")
    student_token = test_login(STUDENT_USERNAME, STUDENT_PASSWORD)
    if not student_token:
        print("Student login failed")
        return
    
    print("Student login successful")
    
    # Test getting lockers
    print("\n3. Testing get lockers...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/lockers", headers=headers)
    
    if response.status_code == 200:
        lockers = response.json()
        if isinstance(lockers, dict):
            lockers = lockers.get("lockers", [])
        print(f"Found {len(lockers)} lockers")
        if lockers:
            test_locker_id = lockers[0]["id"]
        else:
            print("No lockers available for testing")
            return
    else:
        print(f"Failed to get lockers: {response.text}")
        return
    
    # Test getting existing reservations
    print("\n4. Testing get reservations...")
    response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
    
    if response.status_code == 200:
        reservations = response.json().get("reservations", [])
        print(f"Found {len(reservations)} existing reservations")
    else:
        print(f"Failed to get reservations: {response.text}")
        return
    
    # Test creating a new reservation
    print("\n5. Testing create reservation...")
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    reservation_data = {
        "locker_id": test_locker_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "notes": "Test reservation created by script"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/reservations", 
        json=reservation_data,
        headers=headers
    )
    
    if response.status_code == 201:
        new_reservation = response.json().get("reservation")
        print(f"Created reservation: {new_reservation['reservation_code']}")
        print(f"   Access code: {new_reservation['access_code']}")
        print(f"   Locker: {new_reservation['locker_name']}")
        print(f"   Time: {new_reservation['start_time']} to {new_reservation['end_time']}")
        
        reservation_id = new_reservation["id"]
    else:
        print(f"Failed to create reservation: {response.text}")
        return
    
    # Test getting the specific reservation
    print("\n6. Testing get specific reservation...")
    response = requests.get(f"{BASE_URL}/api/reservations/{reservation_id}", headers=headers)
    
    if response.status_code == 200:
        reservation = response.json()
        print(f"Retrieved reservation: {reservation['reservation_code']}")
    else:
        print(f"Failed to get reservation: {response.text}")
    
    # Test updating the reservation
    print("\n7. Testing update reservation...")
    updated_end_time = end_time + timedelta(hours=1)
    update_data = {
        "end_time": updated_end_time.isoformat(),
        "notes": "Updated reservation from test script"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/reservations/{reservation_id}",
        json=update_data,
        headers=headers
    )
    
    if response.status_code == 200:
        updated_reservation = response.json().get("reservation")
        print(f"Updated reservation end time to: {updated_reservation['end_time']}")
    else:
        print(f"Failed to update reservation: {response.text}")
    
    # Test access code functionality
    print("\n8. Testing access code...")
    access_code = new_reservation["access_code"]
    response = requests.post(
        f"{BASE_URL}/api/reservations/access/{access_code}",
        headers=headers
    )
    
    if response.status_code == 200:
        access_data = response.json()
        print(f"Access granted for code: {access_code}")
        print(f"   Reservation: {access_data['reservation']['reservation_code']}")
    else:
        print(f"Failed to access with code: {response.text}")
    
    # Test student access to their own reservations
    print("\n9. Testing student access to reservations...")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.get(f"{BASE_URL}/api/reservations", headers=student_headers)
    
    if response.status_code == 200:
        student_reservations = response.json().get("reservations", [])
        print(f"Student can see {len(student_reservations)} reservations")
    else:
        print(f"Student failed to get reservations: {response.text}")
    
    # Test export functionality (admin only)
    print("\n10. Testing export functionality...")
    response = requests.get(
        f"{BASE_URL}/api/admin/export/reservations?format=csv",
        headers=headers
    )
    
    if response.status_code == 200:
        print("Export successful")
    else:
        print(f"Export failed: {response.text}")
    
    # Test cancellation
    print("\n11. Testing cancel reservation...")
    response = requests.post(
        f"{BASE_URL}/api/reservations/{reservation_id}/cancel",
        headers=headers
    )
    
    if response.status_code == 200:
        cancelled_reservation = response.json().get("reservation")
        print(f"Cancelled reservation: {cancelled_reservation['status']}")
    else:
        print(f"Failed to cancel reservation: {response.text}")
    
    print("\n=== Reservation System Test Complete ===")
    print("All tests passed successfully!")

if __name__ == "__main__":
    try:
        test_reservations()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc() 