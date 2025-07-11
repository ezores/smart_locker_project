#!/usr/bin/env python3
"""
Frontend-focused test script for Smart Locker Reservations
Tests the datetime handling and form submission that the frontend uses
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

def test_frontend_datetime_format(token):
    """Test the exact datetime format that the frontend sends"""
    print_section("Frontend Datetime Format Test")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get available lockers
        response = requests.get(f"{BASE_URL}/api/lockers", headers=headers)
        if response.status_code != 200:
            print_test("Failed to get lockers", False)
            return False
        
        lockers = response.json()
        if not lockers:
            print_test("No lockers available", False)
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
        
        # Test the exact format the frontend sends (YYYY-MM-DDTHH:mm)
        now = datetime.now()  # Local time
        start_time = now + timedelta(minutes=10)
        end_time = start_time + timedelta(hours=1)
        
        # Format as the frontend does (local time)
        start_str = start_time.strftime("%Y-%m-%dT%H:%M")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M")
        
        print(f"Testing with frontend format:")
        print(f"  Start time: {start_str}")
        print(f"  End time: {end_str}")
        
        reservation_data = {
            "locker_id": active_locker['id'],
            "start_time": start_str,
            "end_time": end_str,
            "notes": "Test from frontend format"
        }
        
        response = requests.post(f"{BASE_URL}/api/reservations", 
                               json=reservation_data, headers=headers)
        
        if response.status_code == 201:
            reservation = response.json().get('reservation')
            print_test("Frontend datetime format accepted", True)
            print_test(f"Created reservation ID: {reservation.get('id')}", True)
            return True
        else:
            error = response.json().get('error', 'Unknown error')
            print_test(f"Frontend datetime format rejected: {error}", False)
            return False
            
    except Exception as e:
        print_test(f"Frontend datetime test failed - {str(e)}", False)
        return False

def test_reservation_edit(token):
    """Test editing a reservation with frontend datetime format"""
    print_section("Reservation Edit Test")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get existing reservations
        response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
        if response.status_code != 200:
            print_test("Failed to get reservations", False)
            return False
        
        data = response.json()
        reservations = data.get('reservations', [])
        
        if not reservations:
            print_test("No reservations to edit", False)
            return False
        
        # Find an active reservation
        active_reservation = None
        for res in reservations:
            if res.get('status') == 'active':
                active_reservation = res
                break
        
        if not active_reservation:
            print_test("No active reservations to edit", False)
            return False
        
        # Parse the current times and extend by 30 minutes
        start_time = datetime.fromisoformat(active_reservation['start_time'].replace('Z', '+00:00'))
        end_time = start_time + timedelta(hours=1, minutes=30)
        
        # Format as frontend does
        start_str = start_time.strftime("%Y-%m-%dT%H:%M")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M")
        
        print(f"Editing reservation {active_reservation['id']}:")
        print(f"  New start time: {start_str}")
        print(f"  New end time: {end_str}")
        
        update_data = {
            "locker_id": active_reservation['locker_id'],
            "start_time": start_str,
            "end_time": end_str,
            "notes": "Updated via frontend format"
        }
        
        response = requests.put(f"{BASE_URL}/api/reservations/{active_reservation['id']}", 
                              json=update_data, headers=headers)
        
        if response.status_code == 200:
            updated_reservation = response.json().get('reservation')
            print_test("Reservation updated successfully", True)
            print_test(f"New end time: {updated_reservation.get('end_time')}", True)
            return True
        else:
            error = response.json().get('error', 'Unknown error')
            print_test(f"Failed to update reservation: {error}", False)
            return False
            
    except Exception as e:
        print_test(f"Reservation edit test failed - {str(e)}", False)
        return False

def test_expired_reservations_visibility(token):
    """Test that expired reservations are visible"""
    print_section("Expired Reservations Visibility Test")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all reservations
        response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
        if response.status_code != 200:
            print_test("Failed to get reservations", False)
            return False
        
        data = response.json()
        reservations = data.get('reservations', [])
        
        # Count by status
        status_counts = {}
        for res in reservations:
            status = res.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("Reservation status counts:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
            print_test(f"Found {count} {status} reservations", True)
        
        # Check if we have expired reservations
        expired_count = status_counts.get('expired', 0)
        print_test(f"Expired reservations visible: {expired_count} found", expired_count > 0)
        
        return True
        
    except Exception as e:
        print_test(f"Expired reservations test failed - {str(e)}", False)
        return False

def main():
    """Run frontend-focused tests"""
    print_section("Frontend Reservations Test")
    print(f"Testing against: {BASE_URL}")
    
    # Test authentication
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test frontend datetime format
    test_frontend_datetime_format(token)
    
    # Test reservation editing
    test_reservation_edit(token)
    
    # Test expired reservations visibility
    test_expired_reservations_visibility(token)
    
    print_section("Frontend Test Summary")
    print("✅ Frontend tests completed!")
    print("\nManual testing steps:")
    print("1. Open http://localhost:5173")
    print("2. Login as admin/admin123")
    print("3. Go to Reservations page")
    print("4. Try creating a new reservation")
    print("5. Try editing an existing reservation")
    print("6. Check that expired reservations are visible")
    print("7. Verify datetime pickers work correctly")

if __name__ == "__main__":
    main() 