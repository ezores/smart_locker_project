#!/usr/bin/env python3

"""
Smart Locker System - pytest Configuration
Author: Alp Alpdogan
In memory of Mehmet Ugurlu and Yusuf Alpdogan

LICENSING CONDITION: These memorial dedications and author credits
must never be removed from this file or any derivative works.
This condition is binding and must be preserved in all versions.
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta

# Import models for fixtures
try:
    from models import User, Locker, Item, Log, Borrow, Payment, Reservation
except ImportError:
    # Models might not be available in all test environments
    pass


@pytest.fixture(scope='session')
def app_config():
    """Configure test application"""
    # This would be used if we had a Flask app instance
    # For now, we'll use environment variables for configuration
    os.environ['TESTING'] = 'True'
    os.environ['DATABASE_URL'] = 'postgresql://test_user:test_pass@localhost/test_db'
    return True


@pytest.fixture
def test_user():
    """Create test user fixture"""
    try:
        user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="student",
            student_id="2024TEST001"
        )
        user.set_password("password123")
        return user
    except NameError:
        # Return a mock user if models are not available
        return {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "student",
            "student_id": "2024TEST001"
        }


@pytest.fixture
def test_locker():
    """Create test locker fixture"""
    try:
        locker = Locker(
            name="Test Locker",
            number="L001",
            location="Test Location",
            description="Test locker description",
            capacity=10,
            status="active",
            is_active=True,
            rs485_address=1,
            rs485_locker_number=1
        )
        return locker
    except NameError:
        # Return a mock locker if models are not available
        return {
            "name": "Test Locker",
            "number": "L001",
            "location": "Test Location",
            "description": "Test locker description",
            "capacity": 10,
            "status": "active",
            "is_active": True,
            "rs485_address": 1,
            "rs485_locker_number": 1
        }


@pytest.fixture
def test_item():
    """Create test item fixture"""
    try:
        item = Item(
            name="Test Item",
            description="Test item description",
            category="Electronics",
            status="available",
            locker_id=1,
            rfid_tag="RFID123456"
        )
        return item
    except NameError:
        # Return a mock item if models are not available
        return {
            "name": "Test Item",
            "description": "Test item description",
            "category": "Electronics",
            "status": "available",
            "locker_id": 1,
            "rfid_tag": "RFID123456"
        }


@pytest.fixture
def test_reservation():
    """Create test reservation fixture"""
    try:
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=1)
        
        reservation = Reservation(
            reservation_code="RES001",
            user_id=1,
            locker_id=1,
            start_time=start_time,
            end_time=end_time,
            access_code="123456",
            notes="Test reservation",
            status="active"
        )
        return reservation
    except NameError:
        # Return a mock reservation if models are not available
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=1)
        
        return {
            "reservation_code": "RES001",
            "user_id": 1,
            "locker_id": 1,
            "start_time": start_time,
            "end_time": end_time,
            "access_code": "123456",
            "notes": "Test reservation",
            "status": "active"
        }


@pytest.fixture
def test_borrow():
    """Create test borrow fixture"""
    try:
        borrow = Borrow(
            user_id=1,
            item_id=1,
            locker_id=1,
            due_date=datetime.utcnow() + timedelta(days=7),
            status="borrowed",
            notes="Test borrow"
        )
        return borrow
    except NameError:
        # Return a mock borrow if models are not available
        return {
            "user_id": 1,
            "item_id": 1,
            "locker_id": 1,
            "due_date": datetime.utcnow() + timedelta(days=7),
            "status": "borrowed",
            "notes": "Test borrow"
        }


@pytest.fixture
def test_payment():
    """Create test payment fixture"""
    try:
        payment = Payment(
            user_id=1,
            amount=25.50,
            payment_type="credit_card",
            status="completed",
            transaction_id="TXN123456",
            description="Locker rental payment"
        )
        return payment
    except NameError:
        # Return a mock payment if models are not available
        return {
            "user_id": 1,
            "amount": 25.50,
            "payment_type": "credit_card",
            "status": "completed",
            "transaction_id": "TXN123456",
            "description": "Locker rental payment"
        }


@pytest.fixture
def test_log():
    """Create test log fixture"""
    try:
        log = Log(
            user_id=1,
            item_id=1,
            locker_id=1,
            action_type="login",
            notes="Test log entry",
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )
        return log
    except NameError:
        # Return a mock log if models are not available
        return {
            "user_id": 1,
            "item_id": 1,
            "locker_id": 1,
            "action_type": "login",
            "notes": "Test log entry",
            "ip_address": "127.0.0.1",
            "user_agent": "Test Browser"
        }


@pytest.fixture
def admin_user():
    """Create admin user fixture"""
    try:
        admin = User(
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role="admin"
        )
        admin.set_password("admin123")
        return admin
    except NameError:
        # Return a mock admin if models are not available
        return {
            "username": "admin",
            "email": "admin@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin"
        }


@pytest.fixture
def sample_test_data():
    """Create sample test data for comprehensive testing"""
    return {
        "users": [
            {
                "username": "student1",
                "email": "student1@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "student",
                "student_id": "2024STU001"
            },
            {
                "username": "manager1",
                "email": "manager1@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "role": "manager"
            }
        ],
        "lockers": [
            {
                "name": "Locker A1",
                "number": "A1",
                "location": "Building A",
                "status": "active"
            },
            {
                "name": "Locker B1",
                "number": "B1",
                "location": "Building B",
                "status": "active"
            }
        ],
        "items": [
            {
                "name": "Laptop",
                "description": "Dell XPS 13",
                "category": "Electronics",
                "status": "available"
            },
            {
                "name": "Calculator",
                "description": "Scientific calculator",
                "category": "Tools",
                "status": "available"
            }
        ]
    }


@pytest.fixture
def temp_file():
    """Create a temporary file for testing"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test data")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def mock_rs485_response():
    """Mock RS485 response for testing"""
    return {
        "status": "success",
        "message": "Command executed successfully",
        "locker_id": 1,
        "timestamp": datetime.utcnow().isoformat()
    }


@pytest.fixture
def mock_api_response():
    """Mock API response for testing"""
    return {
        "status": "success",
        "data": {
            "id": 1,
            "name": "Test Item",
            "status": "available"
        },
        "message": "Operation completed successfully"
    } 