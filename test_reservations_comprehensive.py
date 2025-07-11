#!/usr/bin/env python3
"""
Comprehensive test script for Smart Locker Reservations
Tests all functionality including datetime handling, expiration, and admin operations
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "http://localhost:5172"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def print_test(test_name, success=True):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {test_name}")

def login():
    """Login and get auth token"""
    print_section("Authentication Test")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            token = response.json().get("token")
            if token:
                print_test("Login successful", True)
                return token
            else:
                print_test("Login failed - no token in response", False)
                return None
        else:
            print_test(f"Login failed - status {response.status_code}", False)
            return None
    except Exception as e:
        print_test(f"Login failed - {str(e)}", False)
        return None

def test_get_lockers(token):
    """Test getting lockers"""
    print_section("Locker Retrieval Test")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/lockers", headers=headers)
        
        if response.status_code == 200:
            lockers = response.json()
            print_test(f"Retrieved {len(lockers)} lockers", True)
            
            # Check if we have active lockers
            active_lockers = [l for l in lockers if l.get('status') == 'active']
            print_test(f"Found {len(active_lockers)} active lockers", len(active_lockers) > 0)
            
            return lockers
        else:
            print_test(f"Failed to get lockers - status {response.status_code}", False)
            return []
    except Exception as e:
        print_test(f"Failed to get lockers - {str(e)}", False)
        return []

def test_get_reservations(token):
    """Test getting reservations"""
    print_section("Reservation Retrieval Test")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            reservations = data.get('reservations', [])
            print_test(f"Retrieved {len(reservations)} reservations", True)
            
            # Check for different statuses
            statuses = {}
            for res in reservations:
                status = res.get('status', 'unknown')
                statuses[status] = statuses.get(status, 0) + 1
            
            for status, count in statuses.items():
                print_test(f"Found {count} {status} reservations", True)
            
            return reservations
        else:
            print_test(f"Failed to get reservations - status {response.status_code}", False)
            return []
    except Exception as e:
        print_test(f"Failed to get reservations - {str(e)}", False)
        return []

def test_create_reservation(token, lockers):
    """Test creating a new reservation"""
    print_section("Reservation Creation Test")
    
    if not lockers:
        print_test("No lockers available for reservation", False)
        return None
    
    # Find an active locker
    active_locker = None
    for locker in lockers:
        if locker.get('status') == 'active':
            active_locker = locker
            break
    
    if not active_locker:
        print_test("No active lockers available", False)
        return None
    
    try:
        # Create reservation for 1 hour from now
        now = datetime.utcnow()
        start_time = now + timedelta(minutes=5)  # 5 minutes from now
        end_time = start_time + timedelta(hours=1)  # 1 hour duration
        
        headers = {"Authorization": f"Bearer {token}"}
        reservation_data = {
            "locker_id": active_locker['id'],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Test reservation created by comprehensive test"
        }
        
        response = requests.post(f"{BASE_URL}/api/reservations", 
                               json=reservation_data, headers=headers)
        
        if response.status_code == 201:
            reservation = response.json().get('reservation')
            print_test("Reservation created successfully", True)
            print_test(f"Reservation ID: {reservation.get('id')}", True)
            print_test(f"Access Code: {reservation.get('access_code')}", True)
            return reservation
        else:
            error = response.json().get('error', 'Unknown error')
            print_test(f"Failed to create reservation - {error}", False)
            return None
    except Exception as e:
        print_test(f"Failed to create reservation - {str(e)}", False)
        return None

def test_edit_reservation(token, reservation):
    """Test editing a reservation"""
    print_section("Reservation Edit Test")
    
    if not reservation:
        print_test("No reservation to edit", False)
        return None
    
    try:
        # Update the reservation to extend by 30 minutes
        start_time = datetime.fromisoformat(reservation['start_time'].replace('Z', '+00:00'))
        end_time = start_time + timedelta(hours=1, minutes=30)  # 1.5 hours total
        
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {
            "locker_id": reservation['locker_id'],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Updated test reservation"
        }
        
        response = requests.put(f"{BASE_URL}/api/reservations/{reservation['id']}", 
                              json=update_data, headers=headers)
        
        if response.status_code == 200:
            updated_reservation = response.json().get('reservation')
            print_test("Reservation updated successfully", True)
            print_test(f"New end time: {updated_reservation.get('end_time')}", True)
            return updated_reservation
        else:
            error = response.json().get('error', 'Unknown error')
            print_test(f"Failed to update reservation - {error}", False)
            return None
    except Exception as e:
        print_test(f"Failed to update reservation - {str(e)}", False)
        return None

def test_expired_reservation(token, lockers):
    """Test creating and checking expired reservations"""
    print_section("Expired Reservation Test")
    
    if not lockers:
        print_test("No lockers available for expired reservation test", False)
        return None
    
    # Find an active locker
    active_locker = None
    for locker in lockers:
        if locker.get('status') == 'active':
            active_locker = locker
            break
    
    if not active_locker:
        print_test("No active lockers available", False)
        return None
    
    try:
        # Create a reservation that expires in 2 seconds
        now = datetime.utcnow()
        start_time = now + timedelta(seconds=1)
        end_time = start_time + timedelta(seconds=2)  # Expires in 2 seconds
        
        headers = {"Authorization": f"Bearer {token}"}
        reservation_data = {
            "locker_id": active_locker['id'],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Test reservation that will expire"
        }
        
        response = requests.post(f"{BASE_URL}/api/reservations", 
                               json=reservation_data, headers=headers)
        
        if response.status_code == 201:
            reservation = response.json().get('reservation')
            print_test("Expiring reservation created successfully", True)
            print_test(f"Reservation ID: {reservation.get('id')}", True)
            
            # Wait for it to expire
            print("Waiting 3 seconds for reservation to expire...")
            time.sleep(3)
            
            # Check if it's now expired
            response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
            if response.status_code == 200:
                data = response.json()
                reservations = data.get('reservations', [])
                
                # Find our reservation
                expired_reservation = None
                for res in reservations:
                    if res.get('id') == reservation['id']:
                        expired_reservation = res
                        break
                
                if expired_reservation:
                    status = expired_reservation.get('status')
                    print_test(f"Reservation status after expiration: {status}", status == 'expired')
                    return expired_reservation
                else:
                    print_test("Could not find expired reservation in list", False)
                    return None
            else:
                print_test("Failed to check expired reservations", False)
                return None
        else:
            error = response.json().get('error', 'Unknown error')
            print_test(f"Failed to create expiring reservation - {error}", False)
            return None
    except Exception as e:
        print_test(f"Failed to test expired reservation - {str(e)}", False)
        return None

def test_past_time_validation(token, lockers):
    """Test validation for past start times"""
    print_section("Past Time Validation Test")
    
    if not lockers:
        print_test("No lockers available for validation test", False)
        return False
    
    # Find an active locker
    active_locker = None
    for locker in lockers:
        if locker.get('status') == 'active':
            active_locker = locker
            break
    
    if not active_locker:
        print_test("No active lockers available", False)
        return False
    
    try:
        # Try to create a reservation with start time in the past
        now = datetime.utcnow()
        past_time = now - timedelta(hours=1)  # 1 hour ago
        future_time = past_time + timedelta(hours=2)
        
        headers = {"Authorization": f"Bearer {token}"}
        reservation_data = {
            "locker_id": active_locker['id'],
            "start_time": past_time.isoformat(),
            "end_time": future_time.isoformat(),
            "notes": "Test reservation with past start time"
        }
        
        response = requests.post(f"{BASE_URL}/api/reservations", 
                               json=reservation_data, headers=headers)
        
        if response.status_code == 400:
            error = response.json().get('error', '')
            if "past" in error.lower():
                print_test("Correctly rejected reservation with past start time", True)
                return True
            else:
                print_test(f"Rejected but wrong error message: {error}", False)
                return False
        else:
            print_test("Should have rejected past start time but didn't", False)
            return False
    except Exception as e:
        print_test(f"Failed to test past time validation - {str(e)}", False)
        return False

def test_datetime_format_handling(token, lockers):
    """Test various datetime format handling"""
    print_section("Datetime Format Handling Test")
    
    if not lockers:
        print_test("No lockers available for datetime test", False)
        return False
    
    # Find an active locker
    active_locker = None
    for locker in lockers:
        if locker.get('status') == 'active':
            active_locker = locker
            break
    
    if not active_locker:
        print_test("No active lockers available", False)
        return False
    
    try:
        # Test with different datetime formats
        now = datetime.utcnow()
        start_time = now + timedelta(minutes=10)
        end_time = start_time + timedelta(hours=1)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 1: ISO format with Z
        reservation_data = {
            "locker_id": active_locker['id'],
            "start_time": start_time.isoformat() + "Z",
            "end_time": end_time.isoformat() + "Z",
            "notes": "Test with Z suffix"
        }
        
        response = requests.post(f"{BASE_URL}/api/reservations", 
                               json=reservation_data, headers=headers)
        
        if response.status_code == 201:
            print_test("Accepted ISO format with Z suffix", True)
        else:
            error = response.json().get('error', '')
            print_test(f"Rejected ISO format with Z: {error}", False)
        
        # Test 2: ISO format without Z
        reservation_data = {
            "locker_id": active_locker['id'],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Test without Z suffix"
        }
        
        response = requests.post(f"{BASE_URL}/api/reservations", 
                               json=reservation_data, headers=headers)
        
        if response.status_code == 201:
            print_test("Accepted ISO format without Z suffix", True)
            return True
        else:
            error = response.json().get('error', '')
            print_test(f"Rejected ISO format without Z: {error}", False)
            return False
            
    except Exception as e:
        print_test(f"Failed to test datetime format handling - {str(e)}", False)
        return False

def main():
    """Run all tests"""
    print_section("Smart Locker Reservations Comprehensive Test")
    print(f"Testing against: {BASE_URL}")
    
    # Test authentication
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test getting lockers
    lockers = test_get_lockers(token)
    if not lockers:
        print("❌ Cannot proceed without lockers")
        return
    
    # Test getting reservations
    reservations = test_get_reservations(token)
    
    # Test creating a reservation
    new_reservation = test_create_reservation(token, lockers)
    
    # Test editing a reservation
    if new_reservation:
        updated_reservation = test_edit_reservation(token, new_reservation)
    
    # Test expired reservations
    expired_reservation = test_expired_reservation(token, lockers)
    
    # Test past time validation
    test_past_time_validation(token, lockers)
    
    # Test datetime format handling
    test_datetime_format_handling(token, lockers)
    
    print_section("Test Summary")
    print("✅ All tests completed!")
    print("\nTo test the frontend:")
    print("1. Open http://localhost:5173")
    print("2. Login as admin/admin123")
    print("3. Go to Reservations page")
    print("4. Try creating, editing, and viewing expired reservations")

if __name__ == "__main__":
    main() 