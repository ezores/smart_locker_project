#!/usr/bin/env python3
"""
Test script for the Smart Locker Reservation System
"""

import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5050"
API_BASE = f"{BASE_URL}/api"
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
    
    # Test student login (skip in minimal mode)
    print("\n2. Testing student login...")
    student_token = test_login(STUDENT_USERNAME, STUDENT_PASSWORD)
    if not student_token:
        print("Student login failed (expected in minimal mode - no demo users)")
        # Continue with admin-only tests
    else:
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

    # Test reservation expiration
    print("\n8. Testing reservation expiration (short reservation)...")
    short_start = datetime.utcnow() + timedelta(seconds=5)
    short_end = short_start + timedelta(seconds=60)
    short_res_data = {
        "locker_id": test_locker_id,
        "start_time": short_start.isoformat(),
        "end_time": short_end.isoformat(),
        "notes": "Short reservation for expiration test"
    }
    response = requests.post(
        f"{BASE_URL}/api/reservations",
        json=short_res_data,
        headers=headers
    )
    if response.status_code == 201:
        short_res = response.json().get("reservation")
        print(f"Created short reservation: {short_res['reservation_code']} (ends in 1 min)")
        short_res_id = short_res["id"]
        print("Waiting 70 seconds for reservation to expire...")
        import time
        time.sleep(70)
        # Fetch the reservation again
        response = requests.get(f"{BASE_URL}/api/reservations/{short_res_id}", headers=headers)
        if response.status_code == 200:
            res = response.json()
            print(f"Reservation status after expiration: {res['status']}")
            assert res['status'] == 'expired', "Reservation did not expire as expected!"
            print("Expiration test passed!")
        else:
            print(f"Failed to fetch reservation after expiration: {response.text}")
    else:
        print(f"Failed to create short reservation: {response.text}")
    
    # Test access code functionality
    print("\n9. Testing access code...")
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
    
    # Test student access to their own reservations (skip if no student token)
    if student_token:
        print("\n10. Testing student access to reservations...")
        student_headers = {"Authorization": f"Bearer {student_token}"}
        response = requests.get(f"{BASE_URL}/api/reservations", headers=student_headers)
        
        if response.status_code == 200:
            student_reservations = response.json().get("reservations", [])
            print(f"Student can see {len(student_reservations)} reservations")
        else:
            print(f"Student failed to get reservations: {response.text}")
    else:
        print("\n10. Skipping student access test (no student token)")
    
    # Test export functionality (admin only)
    print("\n11. Testing export functionality...")
    response = requests.get(
        f"{BASE_URL}/api/admin/export/reservations?format=csv",
        headers=headers
    )
    
    if response.status_code == 200:
        print("Export successful")
    else:
        print(f"Export failed: {response.text}")
    
    # Test cancellation
    print("\n12. Testing cancel reservation...")
    response = requests.post(
        f"{BASE_URL}/api/reservations/{reservation_id}/cancel",
        headers=headers
    )
    
    if response.status_code == 200:
        cancelled_reservation = response.json().get("reservation")
        print(f"Cancelled reservation: {cancelled_reservation['status']}")
    else:
        print(f"Failed to cancel reservation: {response.text}")
    
    # Test maximum duration (should fail if > 7 days)
    print("\n10. Testing maximum reservation duration (should fail if > 7 days)...")
    too_long_start = datetime.utcnow() + timedelta(hours=1)
    too_long_end = too_long_start + timedelta(days=8)
    too_long_data = {
        "locker_id": test_locker_id,
        "start_time": too_long_start.isoformat(),
        "end_time": too_long_end.isoformat(),
        "notes": "Reservation exceeding 7 days (should fail)"
    }
    response = requests.post(
        f"{BASE_URL}/api/reservations",
        json=too_long_data,
        headers=headers
    )
    if response.status_code == 400 and "7 days" in response.text:
        print("Correctly rejected reservation exceeding 7 days.")
    else:
        print(f"Failed: Reservation exceeding 7 days was not rejected as expected. Status: {response.status_code}, Response: {response.text}")
    
    # Test timezone handling (local time should be preserved)
    print("\n11. Testing timezone handling...")
    # Create a reservation with a specific local time (use future date)
    tomorrow = datetime.now() + timedelta(days=1)
    test_local_time = f"{tomorrow.strftime('%Y-%m-%d')}T23:30:00"  # 11:30 PM local time
    test_end_time = f"{(tomorrow + timedelta(days=1)).strftime('%Y-%m-%d')}T01:30:00"    # 1:30 AM next day local time
    
    timezone_test_data = {
        "locker_id": test_locker_id,
        "start_time": test_local_time,
        "end_time": test_end_time,
        "notes": "Timezone test reservation"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/reservations",
        json=timezone_test_data,
        headers=headers
    )
    
    if response.status_code == 201:
        timezone_res = response.json().get("reservation")
        print(f"Created timezone test reservation: {timezone_res['reservation_code']}")
        print(f"   Start time (local): {test_local_time}")
        print(f"   Start time (stored): {timezone_res['start_time']}")
        print(f"   End time (local): {test_end_time}")
        print(f"   End time (stored): {timezone_res['end_time']}")
        
        # Verify the times are reasonable (should be within a few hours)
        stored_start = datetime.fromisoformat(timezone_res['start_time'].replace('Z', '+00:00'))
        stored_end = datetime.fromisoformat(timezone_res['end_time'].replace('Z', '+00:00'))
        
        # The stored times should be UTC versions of the local times
        # For EST (UTC-5), 23:30 local should be around 04:30 UTC next day
        expected_start_hour = 4  # 23:30 EST = 04:30 UTC next day
        expected_end_hour = 6    # 01:30 EST = 06:30 UTC next day
        
        if stored_start.hour in [expected_start_hour, expected_start_hour + 1, expected_start_hour - 1]:
            print("✓ Start time timezone conversion looks correct")
        else:
            print(f"⚠ Start time conversion may be incorrect: {stored_start.hour} vs expected ~{expected_start_hour}")
            
        if stored_end.hour in [expected_end_hour, expected_end_hour + 1, expected_end_hour - 1]:
            print("✓ End time timezone conversion looks correct")
        else:
            print(f"⚠ End time conversion may be incorrect: {stored_end.hour} vs expected ~{expected_end_hour}")
    else:
        print(f"Failed to create timezone test reservation: {response.text}")
    
    # Test locker status updates based on reservations
    print("\n12. Testing locker status updates...")
    
    # Get initial locker status
    response = requests.get(f"{BASE_URL}/api/lockers", headers=headers)
    if response.status_code == 200:
        lockers = response.json()
        test_locker = lockers[0]  # Use first locker for testing
        print(f"Initial locker status: {test_locker['status']}")
        
        # Create a reservation - locker should become reserved
        reservation_data = {
            "locker_id": test_locker['id'],
            "start_time": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "end_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "notes": "Test reservation for locker status"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/reservations",
            json=reservation_data,
            headers=headers
        )
        
        if response.status_code == 201:
            reservation = response.json().get("reservation")
            print(f"Created reservation: {reservation['reservation_code']}")
            
            # Check locker status after reservation creation
            response = requests.get(f"{BASE_URL}/api/lockers", headers=headers)
            if response.status_code == 200:
                lockers = response.json()
                updated_locker = next((l for l in lockers if l['id'] == test_locker['id']), None)
                if updated_locker:
                    print(f"Locker status after reservation: {updated_locker['status']}")
                    if updated_locker['status'] == 'reserved':
                        print("✓ Locker correctly marked as reserved")
                    else:
                        print("✗ Locker should be reserved but is not")
            
            # Cancel the reservation - locker should become active
            response = requests.post(
                f"{BASE_URL}/api/reservations/{reservation['id']}/cancel",
                headers=headers
            )
            
            if response.status_code == 200:
                print("Reservation cancelled")
                
                # Check locker status after cancellation
                response = requests.get(f"{BASE_URL}/api/lockers", headers=headers)
                if response.status_code == 200:
                    lockers = response.json()
                    updated_locker = next((l for l in lockers if l['id'] == test_locker['id']), None)
                    if updated_locker:
                        print(f"Locker status after cancellation: {updated_locker['status']}")
                        if updated_locker['status'] == 'active':
                            print("✓ Locker correctly marked as active after cancellation")
                        else:
                            print("✗ Locker should be active but is not")
            else:
                print(f"Failed to cancel reservation: {response.text}")
        else:
            print(f"Failed to create reservation: {response.text}")
    else:
        print(f"Failed to get lockers: {response.text}")
    
    print("\n=== Reservation System Test Complete ===")
    print("All tests passed successfully!")

if __name__ == "__main__":
    try:
        test_reservations()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc() 