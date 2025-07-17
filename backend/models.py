import random
import string
from datetime import datetime, timedelta

from werkzeug.security import (check_password_hash,  # type: ignore[import]
                               generate_password_hash)


def init_models(db):
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        rfid_tag = db.Column(db.String(64), unique=True)
        qr_code = db.Column(db.String(128), unique=True)
        role = db.Column(db.String(16), nullable=False)
        email = db.Column(db.String(120), unique=True)
        first_name = db.Column(db.String(50))
        last_name = db.Column(db.String(50))
        student_id = db.Column(db.String(20), unique=True)
        department = db.Column(db.String(50))
        balance = db.Column(db.Float, default=0.0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        is_active = db.Column(db.Boolean, default=True)

        # Relationships
        borrows = db.relationship("Borrow", backref="user", lazy=True)
        logs = db.relationship("Log", backref="user", lazy=True)
        payments = db.relationship("Payment", backref="user", lazy=True)
        reservations = db.relationship(
            "Reservation", foreign_keys="Reservation.user_id", backref="user", lazy=True
        )
        cancelled_reservations = db.relationship(
            "Reservation",
            foreign_keys="Reservation.cancelled_by",
            backref="cancelled_by_user",
            lazy=True,
        )
        modified_reservations = db.relationship(
            "Reservation",
            foreign_keys="Reservation.modified_by",
            backref="modified_by_user",
            lazy=True,
        )

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

        def to_dict(self):
            return {
                "id": self.id,
                "username": self.username,
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "student_id": self.student_id,
                "role": self.role,
                "department": self.department,
                "balance": self.balance,
                "is_active": self.is_active,
                "rfid_tag": self.rfid_tag,
                "qr_code": self.qr_code,
                "created_at": self.created_at.isoformat() if self.created_at else None,
            }

    class Locker(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(32), unique=True, nullable=False)
        number = db.Column(db.String(10), unique=True, nullable=False)
        location = db.Column(db.String(100))
        description = db.Column(db.Text)
        capacity = db.Column(db.Integer, default=10)
        current_occupancy = db.Column(db.Integer, default=0)
        status = db.Column(
            db.String(20), default="active"
        )  # active, maintenance, inactive, reserved
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        # RS485 Protocol Configuration
        # Protocol: 5A5A 00 [ADDRESS] 00 04 00 01 [LOCKER_NUMBER] [CHECKSUM]
        rs485_address = db.Column(
            db.Integer, default=0
        )  # Address card (0-31 dipswitch)
        rs485_locker_number = db.Column(
            db.Integer, default=1
        )  # Number of locker (1-24)

        # Relationships
        items = db.relationship("Item", backref="locker", lazy=True)
        borrows = db.relationship("Borrow", backref="locker", lazy=True)
        logs = db.relationship("Log", backref="locker", lazy=True)
        reservations = db.relationship("Reservation", backref="locker", lazy=True)

        def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "number": self.number,
                "location": self.location,
                "description": self.description,
                "status": self.status,
                "capacity": self.capacity,
                "current_occupancy": self.current_occupancy,
                "is_active": self.is_active,
                "rs485_address": self.rs485_address,
                "rs485_locker_number": self.rs485_locker_number,
                "created_at": self.created_at.isoformat() if self.created_at else None,
            }

    class Reservation(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        reservation_code = db.Column(db.String(16), unique=True, nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
        locker_id = db.Column(db.Integer, db.ForeignKey("locker.id"), nullable=False)
        start_time = db.Column(db.DateTime, nullable=False)
        end_time = db.Column(db.DateTime, nullable=False)
        status = db.Column(
            db.String(20), default="active"
        )  # active, cancelled, completed, expired
        access_code = db.Column(
            db.String(8), unique=True, nullable=False
        )  # 8-digit access code
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        cancelled_at = db.Column(db.DateTime)
        cancelled_by = db.Column(db.Integer, db.ForeignKey("user.id"))
        modified_at = db.Column(db.DateTime)
        modified_by = db.Column(db.Integer, db.ForeignKey("user.id"))

        # Relationships
        logs = db.relationship("Log", backref="reservation", lazy=True)

        def to_dict(self):
            return {
                "id": self.id,
                "reservation_code": self.reservation_code,
                "user_id": self.user_id,
                "locker_id": self.locker_id,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "status": self.status,
                "access_code": self.access_code,
                "notes": self.notes,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "cancelled_at": (
                    self.cancelled_at.isoformat() if self.cancelled_at else None
                ),
                "modified_at": (
                    self.modified_at.isoformat() if self.modified_at else None
                ),
                "user_name": (
                    f"{self.user.first_name} {self.user.last_name}"
                    if self.user
                    else None
                ),
                "locker_name": self.locker.name if self.locker else None,
                "locker_number": self.locker.number if self.locker else None,
            }

        @staticmethod
        def generate_reservation_code():
            """Generate a unique 8-character reservation code"""
            while True:
                code = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=8)
                )
                if not Reservation.query.filter_by(reservation_code=code).first():
                    return code

        @staticmethod
        def generate_access_code():
            """Generate a unique 8-digit access code"""
            while True:
                code = "".join(random.choices(string.digits, k=8))
                if not Reservation.query.filter_by(access_code=code).first():
                    return code

    class Item(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        category = db.Column(db.String(50))  # electronics, books, tools, etc.
        condition = db.Column(
            db.String(20), default="good"
        )  # excellent, good, fair, poor
        status = db.Column(
            db.String(20), default="available"
        )  # available, borrowed, maintenance
        serial_number = db.Column(db.String(100), unique=True)
        purchase_date = db.Column(db.DateTime)
        warranty_expiry = db.Column(db.DateTime)
        locker_id = db.Column(db.Integer, db.ForeignKey("locker.id"))
        is_available = db.Column(db.Boolean, default=True)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        # Relationships
        borrows = db.relationship("Borrow", backref="item", lazy=True)
        logs = db.relationship("Log", backref="item", lazy=True)

        def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "category": self.category,
                "condition": self.condition,
                "status": self.status,
                "locker_id": self.locker_id,
                "locker_name": self.locker.name if self.locker else None,
                "is_active": self.is_active,
                "created_at": self.created_at.isoformat() if self.created_at else None,
            }

    class Log(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
        item_id = db.Column(db.Integer, db.ForeignKey("item.id"))
        locker_id = db.Column(db.Integer, db.ForeignKey("locker.id"))
        reservation_id = db.Column(db.Integer, db.ForeignKey("reservation.id"))
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        action_type = db.Column(
            db.String(64), nullable=False
        )  # Enhanced action types:
        # Authentication: login, login_failed, logout, register, register_failed, auth_failed
        # Borrowing: borrow, return, overdue
        # Reservations: reservation_create, reservation_cancel, reservation_modify, reservation_access
        # Admin: admin_action, user_management, locker_management, system_maintenance
        # Security: security_alert, access_denied
        notes = db.Column(db.Text)
        due_date = db.Column(db.DateTime)
        returned_at = db.Column(db.DateTime)
        ip_address = db.Column(db.String(45))  # IPv4/IPv6 addresses
        user_agent = db.Column(db.Text)  # Browser/client information

        def to_dict(self):
            return {
                "id": self.id,
                "user_id": self.user_id,
                "item_id": self.item_id,
                "locker_id": self.locker_id,
                "reservation_id": self.reservation_id,
                "action_type": self.action_type,
                "notes": self.notes,
                "ip_address": self.ip_address,
                "user_agent": self.user_agent,
                "timestamp": self.timestamp.isoformat() if self.timestamp else None,
                "user_name": (
                    f"{self.user.first_name} {self.user.last_name}"
                    if self.user
                    else None
                ),
                "item_name": self.item.name if self.item else None,
                "locker_name": self.locker.name if self.locker else None,
                "reservation_code": (
                    self.reservation.reservation_code if self.reservation else None
                ),
            }

    class Borrow(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
        item_id = db.Column(db.Integer, db.ForeignKey("item.id"))
        locker_id = db.Column(db.Integer, db.ForeignKey("locker.id"))
        borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
        due_date = db.Column(db.DateTime)
        returned_at = db.Column(db.DateTime)
        status = db.Column(
            db.String(20), default="borrowed"
        )  # borrowed, returned, overdue
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def to_dict(self):
            return {
                "id": self.id,
                "user_id": self.user_id,
                "item_id": self.item_id,
                "locker_id": self.locker_id,
                "borrowed_at": (
                    self.borrowed_at.isoformat() if self.borrowed_at else None
                ),
                "due_date": self.due_date.isoformat() if self.due_date else None,
                "returned_at": (
                    self.returned_at.isoformat() if self.returned_at else None
                ),
                "status": self.status,
                "notes": self.notes,
                "user_name": (
                    f"{self.user.first_name} {self.user.last_name}"
                    if self.user
                    else None
                ),
                "item_name": self.item.name if self.item else None,
                "locker_name": self.locker.name if self.locker else None,
                "created_at": self.created_at.isoformat() if self.created_at else None,
            }

    class Payment(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
        amount = db.Column(db.Float, nullable=False)
        method = db.Column(db.String(32), nullable=False)
        status = db.Column(db.String(16), default="completed")
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        description = db.Column(db.Text)

        def to_dict(self):
            user = self.user if hasattr(self, "user") else None
            return {
                "id": self.id,
                "user_id": self.user_id,
                "user_name": user.username if user else None,
                "amount": self.amount,
                "method": self.method,
                "status": self.status,
                "timestamp": self.timestamp.isoformat() if self.timestamp else None,
                "description": self.description,
            }

    def generate_dummy_data(force_regenerate=False):
        """Generate comprehensive dummy data for testing"""
        
        # Check if demo data already exists to avoid duplicates
        existing_demo_users = User.query.filter(User.username.like('demo_%')).count()
        if existing_demo_users > 0 and not force_regenerate:
            print("Demo data already exists, skipping generation...")
            return
        
        # If force_regenerate is True, clear existing demo data first
        if force_regenerate:
            print("Force regenerating demo data...")
            # Clear existing demo data in correct order to avoid foreign key violations
            # First clear dependent tables
            Log.query.filter(Log.user_id.in_(
                db.session.query(User.id).filter(User.username.like('demo_%'))
            )).delete(synchronize_session=False)
            Borrow.query.filter(Borrow.user_id.in_(
                db.session.query(User.id).filter(User.username.like('demo_%'))
            )).delete(synchronize_session=False)
            Reservation.query.filter(Reservation.user_id.in_(
                db.session.query(User.id).filter(User.username.like('demo_%'))
            )).delete(synchronize_session=False)
            
            # Clear items and their dependencies
            Log.query.filter(Log.item_id.in_(
                db.session.query(Item.id).filter(Item.serial_number.like('demo_%'))
            )).delete(synchronize_session=False)
            Borrow.query.filter(Borrow.item_id.in_(
                db.session.query(Item.id).filter(Item.serial_number.like('demo_%'))
            )).delete(synchronize_session=False)
            
            # Clear lockers and their dependencies
            Log.query.filter(Log.locker_id.in_(
                db.session.query(Locker.id).filter(Locker.name.like('demo_%'))
            )).delete(synchronize_session=False)
            Borrow.query.filter(Borrow.locker_id.in_(
                db.session.query(Locker.id).filter(Locker.name.like('demo_%'))
            )).delete(synchronize_session=False)
            Reservation.query.filter(Reservation.locker_id.in_(
                db.session.query(Locker.id).filter(Locker.name.like('demo_%'))
            )).delete(synchronize_session=False)
            
            # Now clear the main tables
            User.query.filter(User.username.like('demo_%')).delete()
            Item.query.filter(Item.serial_number.like('demo_%')).delete()
            Locker.query.filter(Locker.name.like('demo_%')).delete()
            
            # Also clear items without demo_ prefix to ensure clean slate
            Log.query.filter(Log.item_id.in_(
                db.session.query(Item.id)
            )).delete(synchronize_session=False)
            Borrow.query.filter(Borrow.item_id.in_(
                db.session.query(Item.id)
            )).delete(synchronize_session=False)
            Item.query.delete()
            
            db.session.commit()

        # Create users - much more comprehensive
        # Use environment variables for passwords, fallback to simple demo defaults
        import os

        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
        manager_password = os.environ.get("MANAGER_PASSWORD", "manager123")
        supervisor_password = os.environ.get(
            "SUPERVISOR_PASSWORD", "supervisor123"
        )
        student_password = os.environ.get("STUDENT_PASSWORD", "student123")

        users_data = [
            # Demo Admins
            {
                "username": "demo_admin",
                "password": admin_password,
                "role": "admin",
                "email": "demo_admin@ets.com",
                "first_name": "Demo Admin",
                "last_name": "User",
            },
            {
                "username": "demo_manager",
                "password": manager_password,
                "role": "admin",
                "email": "demo_manager@ets.com",
                "first_name": "Demo Manager",
                "last_name": "User",
            },
            {
                "username": "demo_supervisor",
                "password": supervisor_password,
                "role": "admin",
                "email": "demo_supervisor@ets.com",
                "first_name": "Demo Supervisor",
                "last_name": "User",
            },
            # Demo Students - Create 50 students
            {
                "username": "demo_student1",
                "password": student_password,
                "role": "student",
                "email": "demo_student1@ets.com",
                "first_name": "Demo John",
                "last_name": "Doe",
                "student_id": "demo_2024001",
            },
            {
                "username": "demo_student2",
                "password": student_password,
                "role": "student",
                "email": "demo_student2@ets.com",
                "first_name": "Demo Jane",
                "last_name": "Smith",
                "student_id": "demo_2024002",
            },
            {
                "username": "demo_student3",
                "password": student_password,
                "role": "student",
                "email": "demo_student3@ets.com",
                "first_name": "Demo Mike",
                "last_name": "Johnson",
                "student_id": "demo_2024003",
            },
            {
                "username": "demo_student4",
                "password": student_password,
                "role": "student",
                "email": "demo_student4@ets.com",
                "first_name": "Demo Sarah",
                "last_name": "Wilson",
                "student_id": "demo_2024004",
            },
            {
                "username": "demo_student5",
                "password": student_password,
                "role": "student",
                "email": "demo_student5@ets.com",
                "first_name": "Demo David",
                "last_name": "Brown",
                "student_id": "demo_2024005",
            },
            {
                "username": "demo_student6",
                "password": student_password,
                "role": "student",
                "email": "demo_student6@ets.com",
                "first_name": "Demo Emily",
                "last_name": "Davis",
                "student_id": "demo_2024006",
            },
            {
                "username": "demo_student7",
                "password": student_password,
                "role": "student",
                "email": "demo_student7@ets.com",
                "first_name": "Demo Alex",
                "last_name": "Miller",
                "student_id": "demo_2024007",
            },
            {
                "username": "demo_student8",
                "password": student_password,
                "role": "student",
                "email": "demo_student8@ets.com",
                "first_name": "Demo Lisa",
                "last_name": "Garcia",
                "student_id": "demo_2024008",
            },
            {
                "username": "demo_student9",
                "password": student_password,
                "role": "student",
                "email": "demo_student9@ets.com",
                "first_name": "Demo Tom",
                "last_name": "Martinez",
                "student_id": "demo_2024009",
            },
            {
                "username": "demo_student10",
                "password": student_password,
                "role": "student",
                "email": "demo_student10@ets.com",
                "first_name": "Demo Anna",
                "last_name": "Rodriguez",
                "student_id": "demo_2024010",
            },
            {
                "username": "demo_student11",
                "password": student_password,
                "role": "student",
                "email": "demo_student11@ets.com",
                "first_name": "James",
                "last_name": "Taylor",
                "student_id": "demo_2024011",
            },
            {
                "username": "demo_student12",
                "password": student_password,
                "role": "student",
                "email": "demo_student12@ets.com",
                "first_name": "Maria",
                "last_name": "Anderson",
                "student_id": "demo_2024012",
            },
            {
                "username": "demo_student13",
                "password": student_password,
                "role": "student",
                "email": "demo_student13@ets.com",
                "first_name": "Robert",
                "last_name": "Thomas",
                "student_id": "demo_2024013",
            },
            {
                "username": "demo_student14",
                "password": student_password,
                "role": "student",
                "email": "demo_student14@ets.com",
                "first_name": "Jennifer",
                "last_name": "Jackson",
                "student_id": "demo_2024014",
            },
            {
                "username": "demo_student15",
                "password": student_password,
                "role": "student",
                "email": "demo_student15@ets.com",
                "first_name": "William",
                "last_name": "White",
                "student_id": "demo_2024015",
            },
            {
                "username": "demo_student16",
                "password": student_password,
                "role": "student",
                "email": "demo_student16@ets.com",
                "first_name": "Linda",
                "last_name": "Harris",
                "student_id": "demo_2024016",
            },
            {
                "username": "demo_student17",
                "password": student_password,
                "role": "student",
                "email": "demo_student17@ets.com",
                "first_name": "Michael",
                "last_name": "Clark",
                "student_id": "demo_2024017",
            },
            {
                "username": "demo_student18",
                "password": student_password,
                "role": "student",
                "email": "demo_student18@ets.com",
                "first_name": "Barbara",
                "last_name": "Lewis",
                "student_id": "demo_2024018",
            },
            {
                "username": "demo_student19",
                "password": student_password,
                "role": "student",
                "email": "demo_student19@ets.com",
                "first_name": "Richard",
                "last_name": "Lee",
                "student_id": "demo_2024019",
            },
            {
                "username": "demo_student20",
                "password": student_password,
                "role": "student",
                "email": "demo_student20@ets.com",
                "first_name": "Susan",
                "last_name": "Walker",
                "student_id": "demo_2024020",
            },
            {
                "username": "demo_student21",
                "password": student_password,
                "role": "student",
                "email": "demo_student21@ets.com",
                "first_name": "Joseph",
                "last_name": "Hall",
                "student_id": "demo_2024021",
            },
            {
                "username": "demo_student22",
                "password": student_password,
                "role": "student",
                "email": "demo_student22@ets.com",
                "first_name": "Jessica",
                "last_name": "Allen",
                "student_id": "demo_2024022",
            },
            {
                "username": "demo_student23",
                "password": student_password,
                "role": "student",
                "email": "demo_student23@ets.com",
                "first_name": "Christopher",
                "last_name": "Young",
                "student_id": "demo_2024023",
            },
            {
                "username": "demo_student24",
                "password": student_password,
                "role": "student",
                "email": "demo_student24@ets.com",
                "first_name": "Amanda",
                "last_name": "King",
                "student_id": "demo_2024024",
            },
            {
                "username": "demo_student25",
                "password": student_password,
                "role": "student",
                "email": "demo_student25@ets.com",
                "first_name": "Daniel",
                "last_name": "Wright",
                "student_id": "demo_2024025",
            },
            {
                "username": "demo_student26",
                "password": student_password,
                "role": "student",
                "email": "demo_student26@ets.com",
                "first_name": "Melissa",
                "last_name": "Lopez",
                "student_id": "demo_2024026",
            },
            {
                "username": "demo_student27",
                "password": student_password,
                "role": "student",
                "email": "demo_student27@ets.com",
                "first_name": "Matthew",
                "last_name": "Hill",
                "student_id": "demo_2024027",
            },
            {
                "username": "demo_student28",
                "password": student_password,
                "role": "student",
                "email": "demo_student28@ets.com",
                "first_name": "Nicole",
                "last_name": "Scott",
                "student_id": "demo_2024028",
            },
            {
                "username": "demo_student29",
                "password": student_password,
                "role": "student",
                "email": "demo_student29@ets.com",
                "first_name": "Anthony",
                "last_name": "Green",
                "student_id": "demo_2024029",
            },
            {
                "username": "demo_student30",
                "password": student_password,
                "role": "student",
                "email": "demo_student30@ets.com",
                "first_name": "Stephanie",
                "last_name": "Adams",
                "student_id": "demo_2024030",
            },
            {
                "username": "demo_student31",
                "password": student_password,
                "role": "student",
                "email": "demo_student31@ets.com",
                "first_name": "Mark",
                "last_name": "Baker",
                "student_id": "demo_2024031",
            },
            {
                "username": "demo_student32",
                "password": student_password,
                "role": "student",
                "email": "demo_student32@ets.com",
                "first_name": "Laura",
                "last_name": "Gonzalez",
                "student_id": "demo_2024032",
            },
            {
                "username": "demo_student33",
                "password": student_password,
                "role": "student",
                "email": "demo_student33@ets.com",
                "first_name": "Donald",
                "last_name": "Nelson",
                "student_id": "demo_2024033",
            },
            {
                "username": "demo_student34",
                "password": student_password,
                "role": "student",
                "email": "demo_student34@ets.com",
                "first_name": "Michelle",
                "last_name": "Carter",
                "student_id": "demo_2024034",
            },
            {
                "username": "demo_student35",
                "password": student_password,
                "role": "student",
                "email": "demo_student35@ets.com",
                "first_name": "Steven",
                "last_name": "Mitchell",
                "student_id": "demo_2024035",
            },
            {
                "username": "demo_student36",
                "password": student_password,
                "role": "student",
                "email": "demo_student36@ets.com",
                "first_name": "Kimberly",
                "last_name": "Perez",
                "student_id": "demo_2024036",
            },
            {
                "username": "demo_student37",
                "password": student_password,
                "role": "student",
                "email": "demo_student37@ets.com",
                "first_name": "Paul",
                "last_name": "Roberts",
                "student_id": "demo_2024037",
            },
            {
                "username": "demo_student38",
                "password": student_password,
                "role": "student",
                "email": "demo_student38@ets.com",
                "first_name": "Deborah",
                "last_name": "Turner",
                "student_id": "demo_2024038",
            },
            {
                "username": "demo_student39",
                "password": student_password,
                "role": "student",
                "email": "demo_student39@ets.com",
                "first_name": "Andrew",
                "last_name": "Phillips",
                "student_id": "demo_2024039",
            },
            {
                "username": "demo_student40",
                "password": student_password,
                "role": "student",
                "email": "demo_student40@ets.com",
                "first_name": "Dorothy",
                "last_name": "Campbell",
                "student_id": "demo_2024040",
            },
            {
                "username": "demo_student41",
                "password": student_password,
                "role": "student",
                "email": "demo_student41@ets.com",
                "first_name": "Joshua",
                "last_name": "Parker",
                "student_id": "demo_2024041",
            },
            {
                "username": "demo_student42",
                "password": student_password,
                "role": "student",
                "email": "demo_student42@ets.com",
                "first_name": "Helen",
                "last_name": "Evans",
                "student_id": "demo_2024042",
            },
            {
                "username": "demo_student43",
                "password": student_password,
                "role": "student",
                "email": "demo_student43@ets.com",
                "first_name": "Kenneth",
                "last_name": "Edwards",
                "student_id": "demo_2024043",
            },
            {
                "username": "demo_student44",
                "password": student_password,
                "role": "student",
                "email": "demo_student44@ets.com",
                "first_name": "Sandra",
                "last_name": "Collins",
                "student_id": "demo_2024044",
            },
            {
                "username": "demo_student45",
                "password": student_password,
                "role": "student",
                "email": "demo_student45@ets.com",
                "first_name": "Kevin",
                "last_name": "Stewart",
                "student_id": "demo_2024045",
            },
            {
                "username": "demo_student46",
                "password": student_password,
                "role": "student",
                "email": "demo_student46@ets.com",
                "first_name": "Donna",
                "last_name": "Sanchez",
                "student_id": "demo_2024046",
            },
            {
                "username": "demo_student47",
                "password": student_password,
                "role": "student",
                "email": "demo_student47@ets.com",
                "first_name": "Brian",
                "last_name": "Morris",
                "student_id": "demo_2024047",
            },
            {
                "username": "demo_student48",
                "password": student_password,
                "role": "student",
                "email": "demo_student48@ets.com",
                "first_name": "Carol",
                "last_name": "Rogers",
                "student_id": "demo_2024048",
            },
            {
                "username": "demo_student49",
                "password": student_password,
                "role": "student",
                "email": "demo_student49@ets.com",
                "first_name": "George",
                "last_name": "Reed",
                "student_id": "demo_2024049",
            },
            {
                "username": "demo_student50",
                "password": student_password,
                "role": "student",
                "email": "demo_student50@ets.com",
                "first_name": "Ruth",
                "last_name": "Cook",
                "student_id": "demo_2024050",
            },
        ]

        users = []
        for user_data in users_data:
            user = User(
                username=user_data["username"],
                role=user_data["role"],
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                rfid_tag=f"RFID_{user_data['username'].upper()}",
                qr_code=f"QR_{user_data['username'].upper()}",
                student_id=user_data.get("student_id"),
            )
            user.set_password(user_data["password"])
            users.append(user)
            db.session.add(user)

        # Create lockers - ensure each has a unique 'number' field
        lockers = []
        for i in range(1, 41):
            locker = Locker(
                name=f"Demo Locker {i}",
                number=f"DL{i}",
                location=f"Demo Building {((i-1)//10)+1} - Floor {((i-1)%10)+1}",
                description=f"Demo Locker {i} description",
                capacity=10,
                current_occupancy=0,
                status="active",
                is_active=True,
                created_at=datetime.utcnow(),
            )
            db.session.add(locker)
            lockers.append(locker)
        db.session.commit()

        # Create items - much more comprehensive (100+ items)
        items_data = [
            # Electronics (30 items)
            {
                "name": 'MacBook Pro 16"',
                "description": "Apple MacBook Pro with M2 chip",
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_MBP001",
            },
            {
                "name": 'MacBook Air 13"',
                "description": "Apple MacBook Air M1",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_MBA001",
            },
            {
                "name": "Dell XPS 15",
                "description": "Dell XPS 15 Laptop",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_DXP001",
            },
            {
                "name": 'iPad Pro 12.9"',
                "description": "Apple iPad Pro with Apple Pencil",
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_IPP001",
            },
            {
                "name": "iPad Air",
                "description": "Apple iPad Air",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_IPA001",
            },
            {
                "name": "Samsung Galaxy Tab",
                "description": "Samsung Galaxy Tab S8",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_SGT001",
            },
            {
                "name": "iPhone 15 Pro",
                "description": "Apple iPhone 15 Pro",
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_IPH001",
            },
            {
                "name": "Samsung Galaxy S24",
                "description": "Samsung Galaxy S24 Ultra",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_SGS001",
            },
            {
                "name": "Canon EOS R5",
                "description": "Canon EOS R5 Camera",
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_CER001",
            },
            {
                "name": "Sony A7 IV",
                "description": "Sony A7 IV Mirrorless Camera",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_SAV001",
            },
            {
                "name": 'MacBook Pro 14"',
                "description": 'Apple MacBook Pro 14" M3',
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_MBP002",
            },
            {
                "name": "Dell Latitude",
                "description": "Dell Latitude Business Laptop",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_DLT001",
            },
            {
                "name": "HP EliteBook",
                "description": "HP EliteBook 840",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_HEB001",
            },
            {
                "name": "Lenovo ThinkPad",
                "description": "Lenovo ThinkPad X1 Carbon",
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_LTC001",
            },
            {
                "name": "iPad Mini",
                "description": "Apple iPad Mini 6",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_IPM001",
            },
            {
                "name": "Surface Pro",
                "description": "Microsoft Surface Pro 9",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_MSP001",
            },
            {
                "name": "iPhone 14",
                "description": "Apple iPhone 14",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_IPH002",
            },
            {
                "name": "Google Pixel 8",
                "description": "Google Pixel 8 Pro",
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_GPP001",
            },
            {
                "name": "Nikon Z6",
                "description": "Nikon Z6 Mirrorless Camera",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_NZ6001",
            },
            {
                "name": "Fujifilm X-T5",
                "description": "Fujifilm X-T5 Camera",
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_FXT001",
            },
            {
                "name": "GoPro Hero 11",
                "description": "GoPro Hero 11 Black",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_GPH001",
            },
            {
                "name": "DJI Mini 3",
                "description": "DJI Mini 3 Pro Drone",
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_DJM001",
            },
            {
                "name": "AirPods Pro",
                "description": "Apple AirPods Pro 2",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_APP001",
            },
            {
                "name": "Sony WH-1000XM5",
                "description": "Sony WH-1000XM5 Headphones",
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_SWH001",
            },
            {
                "name": "Bose QuietComfort",
                "description": "Bose QuietComfort 45",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_BQC001",
            },
            {
                "name": "Apple Watch",
                "description": "Apple Watch Series 9",
                "category": "electronics",
                "condition": "excellent",
                "serial_number": "demo_AW9001",
            },
            {
                "name": "Samsung Galaxy Watch",
                "description": "Samsung Galaxy Watch 6",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_SGW001",
            },
            {
                "name": "Kindle Paperwhite",
                "description": "Amazon Kindle Paperwhite",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_KPP001",
            },
            {
                "name": "Roku Ultra",
                "description": "Roku Ultra Streaming Device",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_RKU001",
            },
            {
                "name": "Chromecast",
                "description": "Google Chromecast 4K",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_GCC001",
            },
            {
                "name": "Fire TV Stick",
                "description": "Amazon Fire TV Stick 4K",
                "category": "electronics",
                "condition": "good",
                "serial_number": "demo_AFS001",
            },
            # Books (25 items)
            {
                "name": "Python Programming",
                "description": "Python Programming for Beginners",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BPY001",
            },
            {
                "name": "Data Science Handbook",
                "description": "Complete Data Science Guide",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BDS001",
            },
            {
                "name": "Machine Learning",
                "description": "Introduction to Machine Learning",
                "category": "books",
                "condition": "fair",
                "serial_number": "demo_BML001",
            },
            {
                "name": "Web Development",
                "description": "Modern Web Development",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BWD001",
            },
            {
                "name": "Database Design",
                "description": "Database Design Principles",
                "category": "books",
                "condition": "excellent",
                "serial_number": "demo_BDD001",
            },
            {
                "name": "JavaScript Guide",
                "description": "JavaScript: The Definitive Guide",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BJS001",
            },
            {
                "name": "React Development",
                "description": "Learning React",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BRD001",
            },
            {
                "name": "Node.js Guide",
                "description": "Node.js Design Patterns",
                "category": "books",
                "condition": "fair",
                "serial_number": "demo_BND001",
            },
            {
                "name": "Docker Handbook",
                "description": "Docker in Practice",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BDH001",
            },
            {
                "name": "Kubernetes Guide",
                "description": "Kubernetes: Up and Running",
                "category": "books",
                "condition": "excellent",
                "serial_number": "demo_BKG001",
            },
            {
                "name": "AWS Solutions",
                "description": "AWS Solutions Architect",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BAS001",
            },
            {
                "name": "Azure Fundamentals",
                "description": "Microsoft Azure Fundamentals",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BAF001",
            },
            {
                "name": "Google Cloud",
                "description": "Google Cloud Platform",
                "category": "books",
                "condition": "fair",
                "serial_number": "demo_BGC001",
            },
            {
                "name": "DevOps Handbook",
                "description": "The DevOps Handbook",
                "category": "books",
                "condition": "excellent",
                "serial_number": "demo_BDH002",
            },
            {
                "name": "Clean Code",
                "description": "Clean Code: A Handbook",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BCC001",
            },
            {
                "name": "Design Patterns",
                "description": "Design Patterns: Elements",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BDP001",
            },
            {
                "name": "Refactoring",
                "description": "Refactoring: Improving Design",
                "category": "books",
                "condition": "fair",
                "serial_number": "demo_BRF001",
            },
            {
                "name": "Test Driven Development",
                "description": "Test-Driven Development",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BTD001",
            },
            {
                "name": "Agile Development",
                "description": "Agile Software Development",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BAD001",
            },
            {
                "name": "Scrum Guide",
                "description": "The Scrum Guide",
                "category": "books",
                "condition": "excellent",
                "serial_number": "demo_BSG001",
            },
            {
                "name": "Git Version Control",
                "description": "Pro Git",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BGV001",
            },
            {
                "name": "Linux Administration",
                "description": "Linux System Administration",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BLA001",
            },
            {
                "name": "Network Security",
                "description": "Network Security Essentials",
                "category": "books",
                "condition": "fair",
                "serial_number": "demo_BNS001",
            },
            {
                "name": "Cryptography",
                "description": "Applied Cryptography",
                "category": "books",
                "condition": "excellent",
                "serial_number": "demo_BCR001",
            },
            {
                "name": "Computer Networks",
                "description": "Computer Networks",
                "category": "books",
                "condition": "good",
                "serial_number": "demo_BCN001",
            },
            # Tools (25 items)
            {
                "name": "Arduino Kit",
                "description": "Arduino Starter Kit with Components",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TAR001",
            },
            {
                "name": "Raspberry Pi 4",
                "description": "Raspberry Pi 4 Model B",
                "category": "tools",
                "condition": "excellent",
                "serial_number": "demo_TRP001",
            },
            {
                "name": "Soldering Iron",
                "description": "Professional Soldering Iron",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TSI001",
            },
            {
                "name": "Multimeter",
                "description": "Digital Multimeter",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TMM001",
            },
            {
                "name": "Oscilloscope",
                "description": "Digital Oscilloscope",
                "category": "tools",
                "condition": "excellent",
                "serial_number": "demo_TOS001",
            },
            {
                "name": "3D Printer",
                "description": "Creality Ender 3 Pro",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_T3P001",
            },
            {
                "name": "Laser Cutter",
                "description": "CO2 Laser Cutter",
                "category": "tools",
                "condition": "excellent",
                "serial_number": "demo_TLC001",
            },
            {
                "name": "CNC Machine",
                "description": "Desktop CNC Router",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TCM001",
            },
            {
                "name": "Drill Press",
                "description": "Bench Drill Press",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TDP001",
            },
            {
                "name": "Band Saw",
                "description": "Table Band Saw",
                "category": "tools",
                "condition": "fair",
                "serial_number": "demo_TBS001",
            },
            {
                "name": "Circular Saw",
                "description": "Portable Circular Saw",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TCS001",
            },
            {
                "name": "Jigsaw",
                "description": "Electric Jigsaw",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TJS001",
            },
            {
                "name": "Router",
                "description": "Wood Router",
                "category": "tools",
                "condition": "excellent",
                "serial_number": "demo_TWR001",
            },
            {
                "name": "Sander",
                "description": "Orbital Sander",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TOS002",
            },
            {
                "name": "Air Compressor",
                "description": "Portable Air Compressor",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TAC001",
            },
            {
                "name": "Welding Machine",
                "description": "MIG Welding Machine",
                "category": "tools",
                "condition": "excellent",
                "serial_number": "demo_TWM001",
            },
            {
                "name": "Plasma Cutter",
                "description": "Plasma Cutting Machine",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TPC001",
            },
            {
                "name": "Heat Gun",
                "description": "Industrial Heat Gun",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_THG001",
            },
            {
                "name": "Hot Air Station",
                "description": "SMD Hot Air Station",
                "category": "tools",
                "condition": "excellent",
                "serial_number": "demo_THS001",
            },
            {
                "name": "Logic Analyzer",
                "description": "USB Logic Analyzer",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TLA001",
            },
            {
                "name": "Function Generator",
                "description": "Signal Function Generator",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TFG001",
            },
            {
                "name": "Power Supply",
                "description": "Variable Power Supply",
                "category": "tools",
                "condition": "excellent",
                "serial_number": "demo_TPS001",
            },
            {
                "name": "Microscope",
                "description": "Digital Microscope",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TDM001",
            },
            {
                "name": "Calipers",
                "description": "Digital Calipers",
                "category": "tools",
                "condition": "good",
                "serial_number": "demo_TDC001",
            },
            {
                "name": "Micrometer",
                "description": "Digital Micrometer",
                "category": "tools",
                "condition": "excellent",
                "serial_number": "demo_TDM002",
            },
            # Audio/Video (20 items)
            {
                "name": "Microphone Set",
                "description": "Professional USB Microphone",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_AMS001",
            },
            {
                "name": "Video Camera",
                "description": "4K Video Camera",
                "category": "audio",
                "condition": "excellent",
                "serial_number": "demo_AVC001",
            },
            {
                "name": "Audio Interface",
                "description": "USB Audio Interface",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_AAI001",
            },
            {
                "name": "Studio Lights",
                "description": "LED Studio Lighting Kit",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_ASL001",
            },
            {
                "name": "Green Screen",
                "description": "Professional Green Screen",
                "category": "audio",
                "condition": "fair",
                "serial_number": "demo_AGS001",
            },
            {
                "name": "Tripod",
                "description": "Professional Camera Tripod",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_ATP001",
            },
            {
                "name": "Gimbal",
                "description": "3-Axis Camera Gimbal",
                "category": "audio",
                "condition": "excellent",
                "serial_number": "demo_AGM001",
            },
            {
                "name": "Wireless Mic",
                "description": "Wireless Lavalier Microphone",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_AWM001",
            },
            {
                "name": "Mixer",
                "description": "Audio Mixer Console",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_AMX001",
            },
            {
                "name": "Speakers",
                "description": "Studio Monitor Speakers",
                "category": "audio",
                "condition": "excellent",
                "serial_number": "demo_ASP001",
            },
            {
                "name": "Headphones",
                "description": "Studio Headphones",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_AHD001",
            },
            {
                "name": "MIDI Controller",
                "description": "USB MIDI Controller",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_AMC001",
            },
            {
                "name": "Synthesizer",
                "description": "Digital Synthesizer",
                "category": "audio",
                "condition": "excellent",
                "serial_number": "demo_ASY001",
            },
            {
                "name": "Drum Machine",
                "description": "Electronic Drum Machine",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_ADM001",
            },
            {
                "name": "Guitar Amp",
                "description": "Electric Guitar Amplifier",
                "category": "audio",
                "condition": "fair",
                "serial_number": "demo_AGA001",
            },
            {
                "name": "Bass Amp",
                "description": "Bass Guitar Amplifier",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_ABA001",
            },
            {
                "name": "Effects Pedal",
                "description": "Guitar Effects Pedal",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_AEP001",
            },
            {
                "name": "Cables",
                "description": "Professional Audio Cables",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_ACB001",
            },
            {
                "name": "Stand",
                "description": "Microphone Stand",
                "category": "audio",
                "condition": "good",
                "serial_number": "demo_AMS002",
            },
            {
                "name": "Pop Filter",
                "description": "Microphone Pop Filter",
                "category": "audio",
                "condition": "fair",
                "serial_number": "demo_APF001",
            },
        ]

        items = []
        for i, item_data in enumerate(items_data):
            item = Item(
                **item_data,
                locker_id=lockers[i % len(lockers)].id,
                purchase_date=datetime.now() - timedelta(days=random.randint(30, 365)),
                warranty_expiry=datetime.now()
                + timedelta(days=random.randint(100, 1000)),
            )
            items.append(item)
            db.session.add(item)

        # Create reservations - much more comprehensive
        # Remove static reservations_data and generate reservations only for valid users and lockers
        max_reservations = min(len(users), len(lockers))
        for i in range(max_reservations):
            user = users[i]
            locker = lockers[i]
            reservation = Reservation(
                reservation_code=Reservation.generate_reservation_code(),
                user_id=user.id,
                locker_id=locker.id,
                start_time=datetime.now() - timedelta(days=i + 1),
                end_time=datetime.now() + timedelta(days=i + 1),
                status="active",
                access_code=Reservation.generate_access_code(),
                notes=f"Reservation for {user.username}",
                created_at=datetime.utcnow(),
            )
            db.session.add(reservation)
        db.session.commit()

        # Create logs and borrows - much more comprehensive
        action_types = ["borrow", "return", "maintenance", "check_in", "check_out"]
        for i in range(500):  # Create 500 log entries
            user = random.choice(users)
            item = random.choice(items)
            locker = random.choice(lockers)
            action = random.choice(action_types)

            # Create log entry
            log = Log(
                user_id=user.id,
                item_id=item.id,
                locker_id=locker.id,
                action_type=action,
                timestamp=datetime.now() - timedelta(days=random.randint(1, 90)),
                notes=f"Log entry {i+1} for {action} action",
            )
            db.session.add(log)

            # Create borrow entries (for active borrows) - more active borrows
            if (
                action == "borrow" and random.random() < 0.4
            ):  # 40% chance of active borrow
                borrow = Borrow(
                    user_id=user.id,
                    item_id=item.id,
                    borrowed_at=datetime.now() - timedelta(days=random.randint(1, 14)),
                    due_date=datetime.now() + timedelta(days=random.randint(1, 21)),
                    status="borrowed",
                    notes=f"Active borrow for {item.name}",
                )
                db.session.add(borrow)

                # Mark item as unavailable
                item.is_available = False

        # Create payments
        for user in users:
            for i in range(random.randint(1, 5)):
                payment = Payment(
                    user_id=user.id,
                    amount=round(random.uniform(10, 100), 2),
                    method=random.choice(["credit_card", "bank_transfer", "cash"]),
                    status="completed",
                    description=f"Payment {i+1} for user {user.username}",
                )
                db.session.add(payment)

        db.session.commit()
        print(
            f"Created {len(users)} users, {len(lockers)} lockers, {len(items)} items, and 500 log entries with active borrows"
        )

    def init_db(minimal=False):
        # This function should be called within an application context
        # The actual database operations are handled in app.py with proper context
        pass

    return (
        User,
        Locker,
        Item,
        Log,
        Borrow,
        Payment,
        Reservation,
        init_db,
        generate_dummy_data,
    )
