#!/usr/bin/env python3

"""
Smart Locker System - Model Tests
Author: Alp Alpdogan
In memory of Mehmet Ugurlu and Yusuf Alpdogan

LICENSING CONDITION: These memorial dedications and author credits
must never be removed from this file or any derivative works.
This condition is binding and must be preserved in all versions.
"""

import pytest
from datetime import datetime, timedelta
from models import User, Locker, Item, Log, Borrow, Payment, Reservation


class TestUserModel:
    """Test User model functionality"""

    def test_user_creation(self):
        """Test user model creation and validation"""
        user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="student",
            student_id="2024TEST001"
        )
        user.set_password("password123")
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.role == "student"
        assert user.student_id == "2024TEST001"
        assert user.check_password("password123")
        assert not user.check_password("wrongpassword")

    def test_user_to_dict(self):
        """Test user serialization to dictionary"""
        user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="student"
        )
        user.id = 1
        
        user_dict = user.to_dict()
        
        assert user_dict["id"] == 1
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["first_name"] == "Test"
        assert user_dict["last_name"] == "User"
        assert user_dict["role"] == "student"
        assert "password_hash" not in user_dict

    def test_user_password_hashing(self):
        """Test password hashing and verification"""
        user = User(username="testuser")
        
        # Test password setting
        user.set_password("testpassword")
        assert user.password_hash is not None
        assert user.password_hash != "testpassword"
        
        # Test password verification
        assert user.check_password("testpassword")
        assert not user.check_password("wrongpassword")
        assert not user.check_password("")

    def test_user_role_validation(self):
        """Test user role validation"""
        valid_roles = ["admin", "manager", "supervisor", "student"]
        
        for role in valid_roles:
            user = User(username="testuser", role=role)
            assert user.role == role

    def test_user_email_validation(self):
        """Test user email format validation"""
        user = User(
            username="testuser",
            email="valid.email@example.com"
        )
        assert user.email == "valid.email@example.com"


class TestLockerModel:
    """Test Locker model functionality"""

    def test_locker_creation(self):
        """Test locker model creation"""
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
        
        assert locker.name == "Test Locker"
        assert locker.number == "L001"
        assert locker.location == "Test Location"
        assert locker.description == "Test locker description"
        assert locker.capacity == 10
        assert locker.status == "active"
        assert locker.is_active is True
        assert locker.rs485_address == 1
        assert locker.rs485_locker_number == 1

    def test_locker_to_dict(self):
        """Test locker serialization to dictionary"""
        locker = Locker(
            name="Test Locker",
            number="L001",
            location="Test Location",
            status="active"
        )
        locker.id = 1
        
        locker_dict = locker.to_dict()
        
        assert locker_dict["id"] == 1
        assert locker_dict["name"] == "Test Locker"
        assert locker_dict["number"] == "L001"
        assert locker_dict["location"] == "Test Location"
        assert locker_dict["status"] == "active"

    def test_locker_status_validation(self):
        """Test locker status validation"""
        valid_statuses = ["active", "inactive", "maintenance", "reserved"]
        
        for status in valid_statuses:
            locker = Locker(name="Test Locker", number="L001", status=status)
            assert locker.status == status

    def test_locker_rs485_configuration(self):
        """Test locker RS485 configuration"""
        locker = Locker(
            name="Test Locker",
            number="L001",
            rs485_address=5,
            rs485_locker_number=3
        )
        
        assert locker.rs485_address == 5
        assert locker.rs485_locker_number == 3


class TestItemModel:
    """Test Item model functionality"""

    def test_item_creation(self):
        """Test item model creation"""
        item = Item(
            name="Test Item",
            description="Test item description",
            category="Electronics",
            status="available",
            locker_id=1,
            rfid_tag="RFID123456"
        )
        
        assert item.name == "Test Item"
        assert item.description == "Test item description"
        assert item.category == "Electronics"
        assert item.status == "available"
        assert item.locker_id == 1
        assert item.rfid_tag == "RFID123456"

    def test_item_to_dict(self):
        """Test item serialization to dictionary"""
        item = Item(
            name="Test Item",
            description="Test item description",
            status="available",
            locker_id=1
        )
        item.id = 1
        
        item_dict = item.to_dict()
        
        assert item_dict["id"] == 1
        assert item_dict["name"] == "Test Item"
        assert item_dict["description"] == "Test item description"
        assert item_dict["status"] == "available"
        assert item_dict["locker_id"] == 1

    def test_item_status_validation(self):
        """Test item status validation"""
        valid_statuses = ["available", "borrowed", "maintenance", "lost"]
        
        for status in valid_statuses:
            item = Item(name="Test Item", status=status, locker_id=1)
            assert item.status == status


class TestReservationModel:
    """Test Reservation model functionality"""

    def test_reservation_creation(self):
        """Test reservation model creation"""
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
        
        assert reservation.reservation_code == "RES001"
        assert reservation.user_id == 1
        assert reservation.locker_id == 1
        assert reservation.start_time == start_time
        assert reservation.end_time == end_time
        assert reservation.access_code == "123456"
        assert reservation.notes == "Test reservation"
        assert reservation.status == "active"

    def test_reservation_to_dict(self):
        """Test reservation serialization to dictionary"""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=1)
        
        reservation = Reservation(
            reservation_code="RES001",
            user_id=1,
            locker_id=1,
            start_time=start_time,
            end_time=end_time,
            status="active"
        )
        reservation.id = 1
        
        reservation_dict = reservation.to_dict()
        
        assert reservation_dict["id"] == 1
        assert reservation_dict["reservation_code"] == "RES001"
        assert reservation_dict["user_id"] == 1
        assert reservation_dict["locker_id"] == 1
        assert reservation_dict["status"] == "active"

    def test_reservation_code_generation(self):
        """Test reservation code generation"""
        code1 = Reservation.generate_reservation_code()
        code2 = Reservation.generate_reservation_code()
        
        assert len(code1) == 8
        assert len(code2) == 8
        assert code1 != code2
        assert code1.isalnum()
        assert code2.isalnum()

    def test_access_code_generation(self):
        """Test access code generation"""
        code1 = Reservation.generate_access_code()
        code2 = Reservation.generate_access_code()
        
        assert len(code1) == 6
        assert len(code2) == 6
        assert code1 != code2
        assert code1.isdigit()
        assert code2.isdigit()

    def test_reservation_status_validation(self):
        """Test reservation status validation"""
        valid_statuses = ["active", "cancelled", "expired", "completed"]
        
        for status in valid_statuses:
            reservation = Reservation(
                reservation_code="RES001",
                user_id=1,
                locker_id=1,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(hours=1),
                status=status
            )
            assert reservation.status == status


class TestBorrowModel:
    """Test Borrow model functionality"""

    def test_borrow_creation(self):
        """Test borrow model creation"""
        borrow = Borrow(
            user_id=1,
            item_id=1,
            locker_id=1,
            due_date=datetime.utcnow() + timedelta(days=7),
            status="borrowed",
            notes="Test borrow"
        )
        
        assert borrow.user_id == 1
        assert borrow.item_id == 1
        assert borrow.locker_id == 1
        assert borrow.status == "borrowed"
        assert borrow.notes == "Test borrow"

    def test_borrow_to_dict(self):
        """Test borrow serialization to dictionary"""
        borrow = Borrow(
            user_id=1,
            item_id=1,
            locker_id=1,
            status="borrowed"
        )
        borrow.id = 1
        
        borrow_dict = borrow.to_dict()
        
        assert borrow_dict["id"] == 1
        assert borrow_dict["user_id"] == 1
        assert borrow_dict["item_id"] == 1
        assert borrow_dict["locker_id"] == 1
        assert borrow_dict["status"] == "borrowed"

    def test_borrow_status_validation(self):
        """Test borrow status validation"""
        valid_statuses = ["borrowed", "returned", "overdue", "lost"]
        
        for status in valid_statuses:
            borrow = Borrow(
                user_id=1,
                item_id=1,
                locker_id=1,
                status=status
            )
            assert borrow.status == status


class TestLogModel:
    """Test Log model functionality"""

    def test_log_creation(self):
        """Test log model creation"""
        log = Log(
            user_id=1,
            item_id=1,
            locker_id=1,
            action_type="login",
            notes="Test log entry",
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )
        
        assert log.user_id == 1
        assert log.item_id == 1
        assert log.locker_id == 1
        assert log.action_type == "login"
        assert log.notes == "Test log entry"
        assert log.ip_address == "127.0.0.1"
        assert log.user_agent == "Test Browser"

    def test_log_to_dict(self):
        """Test log serialization to dictionary"""
        log = Log(
            user_id=1,
            action_type="login",
            notes="Test log entry"
        )
        log.id = 1
        
        log_dict = log.to_dict()
        
        assert log_dict["id"] == 1
        assert log_dict["user_id"] == 1
        assert log_dict["action_type"] == "login"
        assert log_dict["notes"] == "Test log entry"


class TestPaymentModel:
    """Test Payment model functionality"""

    def test_payment_creation(self):
        """Test payment model creation"""
        payment = Payment(
            user_id=1,
            amount=25.50,
            payment_type="credit_card",
            status="completed",
            transaction_id="TXN123456",
            description="Locker rental payment"
        )
        
        assert payment.user_id == 1
        assert payment.amount == 25.50
        assert payment.payment_type == "credit_card"
        assert payment.status == "completed"
        assert payment.transaction_id == "TXN123456"
        assert payment.description == "Locker rental payment"

    def test_payment_to_dict(self):
        """Test payment serialization to dictionary"""
        payment = Payment(
            user_id=1,
            amount=25.50,
            payment_type="credit_card",
            status="completed"
        )
        payment.id = 1
        
        payment_dict = payment.to_dict()
        
        assert payment_dict["id"] == 1
        assert payment_dict["user_id"] == 1
        assert payment_dict["amount"] == 25.50
        assert payment_dict["payment_type"] == "credit_card"
        assert payment_dict["status"] == "completed"

    def test_payment_status_validation(self):
        """Test payment status validation"""
        valid_statuses = ["pending", "completed", "failed", "refunded"]
        
        for status in valid_statuses:
            payment = Payment(
                user_id=1,
                amount=25.50,
                payment_type="credit_card",
                status=status
            )
            assert payment.status == status

    def test_payment_type_validation(self):
        """Test payment type validation"""
        valid_types = ["credit_card", "debit_card", "cash", "online"]
        
        for payment_type in valid_types:
            payment = Payment(
                user_id=1,
                amount=25.50,
                payment_type=payment_type,
                status="completed"
            )
            assert payment.payment_type == payment_type 