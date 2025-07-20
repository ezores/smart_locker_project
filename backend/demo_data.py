"""
Smart Locker System - Demo Data Module

@author Alp
@date 2024-12-XX
@description Demo data generator for testing the Smart Locker System
"""

import random
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash


def create_demo_data(
    db, User, Locker, Item, Log, Borrow, Payment
):
    """Create comprehensive demo data for testing the system"""

    print("Creating comprehensive demo data...")

    # Clear ALL existing data
    Log.query.delete()
    Borrow.query.delete()
    Payment.query.delete()
    Item.query.delete()
    Locker.query.delete()
    User.query.delete()  # Clear all users including admin

    # Create admin user first
    admin_user = User(
        username="admin",
        password_hash=generate_password_hash("admin123"),
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        role="admin",
        balance=0.00,
        department="IT",
        is_active=True,
    )
    db.session.add(admin_user)

    # Create 10x more demo users
    for i in range(1, 501):  # 500 students
        user = User(
            username=f"student{i}",
            password_hash=generate_password_hash("password123"),
            email=f"student{i}@example.com",
            first_name=f"Student{i}",
            last_name=f"User{i}",
            role="student",
            department=random.choice(
                ["CS", "Math", "Physics", "Chemistry", "Biology", "Engineering"]
            ),
            balance=random.uniform(0, 100),
            is_active=True,
        )
        db.session.add(user)
    db.session.commit()
    # Create exactly 62 lockers with precise RS485 mapping
    # RS485 mapping based on the provided data - exactly 62 lockers
    rs485_mapping = [
        # Global, armoire, carte, casier, rs485_address, rs485_locker_number
        (1, 1, 1, 1, 1, 1), (2, 1, 1, 2, 1, 2), (3, 1, 1, 3, 1, 3), (4, 1, 1, 4, 1, 4),
        (5, 1, 1, 5, 1, 5), (6, 1, 1, 6, 1, 6), (7, 1, 1, 7, 1, 7), (8, 1, 1, 8, 1, 8),
        (9, 1, 1, 9, 1, 9), (10, 1, 1, 10, 1, 10), (11, 1, 1, 11, 1, 11), (12, 1, 1, 12, 1, 12),
        (13, 1, 1, 13, 1, 13), (14, 1, 1, 14, 1, 14),
        
        (15, 2, 2, 1, 2, 1), (16, 2, 2, 2, 2, 2), (17, 2, 2, 3, 2, 3), (18, 2, 2, 4, 2, 4),
        (19, 2, 2, 5, 2, 5), (20, 2, 2, 6, 2, 6), (21, 2, 2, 7, 2, 7), (22, 2, 2, 8, 2, 8),
        (23, 2, 2, 9, 2, 9), (24, 2, 2, 10, 2, 10), (25, 2, 2, 11, 2, 11), (26, 2, 2, 12, 2, 12),
        (27, 2, 2, 13, 2, 13), (28, 2, 2, 14, 2, 14), (29, 2, 2, 15, 2, 15), (30, 2, 2, 16, 2, 16),
        (31, 2, 2, 17, 2, 17), (32, 2, 2, 18, 2, 18), (33, 2, 2, 19, 2, 19), (34, 2, 2, 20, 2, 20),
        (35, 2, 2, 21, 2, 21), (36, 2, 2, 22, 2, 22), (37, 2, 2, 23, 2, 23), (38, 2, 2, 24, 2, 24),
        
        (39, 2, 3, 1, 3, 1), (40, 2, 3, 2, 3, 2), (41, 2, 3, 3, 3, 3), (42, 2, 3, 4, 3, 4),
        (43, 2, 3, 5, 3, 5), (44, 2, 3, 6, 3, 6), (45, 2, 3, 7, 3, 7), (46, 2, 3, 8, 3, 8),
        (47, 2, 3, 9, 3, 9), (48, 2, 3, 10, 3, 10), (49, 2, 3, 11, 3, 11), (50, 2, 3, 12, 3, 12),
        (51, 2, 3, 13, 3, 13), (52, 2, 3, 14, 3, 14), (53, 2, 3, 15, 3, 15), (54, 2, 3, 16, 3, 16),
        (55, 2, 3, 17, 3, 17), (56, 2, 3, 18, 3, 18), (57, 2, 3, 19, 3, 19), (58, 2, 3, 20, 3, 20),
        (59, 2, 3, 21, 3, 21), (60, 2, 3, 22, 3, 22), (61, 2, 3, 23, 3, 23), (62, 2, 3, 24, 3, 24)
    ]
    
    # Create exactly 62 lockers with correct RS485 mapping
    for global_id, armoire, carte, casier, rs485_address, rs485_locker_number in rs485_mapping:
        locker = Locker(
            name=f"Locker {global_id}",
            number=f"L{global_id}",
            location=f"Armoire {armoire}, Carte {carte}, Casier {casier}",
            capacity=random.randint(5, 15),
            current_occupancy=0,
            status="available",
            rs485_address=rs485_address,
            rs485_locker_number=rs485_locker_number,
        )
        db.session.add(locker)
    db.session.commit()
    # Create 10x more items
    for i in range(1, 2001):  # 2000 items
        item = Item(
            name=f"Item {i}",
            description=f"Description for item {i}",
            category=random.choice(
                [
                    "Electronics",
                    "Audio/Video",
                    "VR/Gaming",
                    "Drones",
                    "Robotics",
                    "3D Printing",
                    "Manufacturing",
                    "Testing",
                    "Tools",
                ]
            ),
            brand=random.choice(["BrandA", "BrandB", "BrandC", "BrandD"]),
            model=f"Model{i}",
            condition=random.choice(["new", "good", "fair", "poor"]),
            value=random.uniform(10, 5000),
            locker_id=random.choice(
                Locker.query.all()
            ).id,  # Use Locker.query.all() to get all lockers
            is_active=True,
        )
        db.session.add(item)
    db.session.commit()
    # Create 10x more borrows and returns
    for i in range(1, 5001):  # 5000 borrows
        user = random.choice(
            User.query.all()[1:]
        )  # Use User.query.all() to get all users
        item = random.choice(Item.query.all())  # Use Item.query.all() to get all items
        locker = random.choice(
            Locker.query.all()
        )  # Use Locker.query.all() to get all lockers
        borrowed_at = datetime.now() - timedelta(
            days=random.randint(1, 90)
        )  # Use datetime.now()
        due_date = borrowed_at + timedelta(days=random.randint(3, 14))
        returned = random.choice([True, False, False])
        borrow = Borrow(
            user_id=user.id,
            item_id=item.id,
            locker_id=locker.id,
            borrowed_at=borrowed_at,
            due_date=due_date,
            status="returned" if returned else "active",
            returned_at=(
                (borrowed_at + timedelta(days=random.randint(1, 20)))
                if returned
                else None
            ),
        )
        db.session.add(borrow)
    db.session.commit()
    # Create more payments (increased from 10-20 to 30-50 per user)
    for user in User.query.all()[1:]:  # Use User.query.all() to get all users
        for _ in range(random.randint(30, 50)):
            payment = Payment(
                user_id=user.id,
                amount=random.uniform(5, 500),
                payment_type=random.choice(
                    [
                        "deposit",
                        "withdrawal",
                        "fee",
                        "refund",
                        "late_fee",
                        "equipment_fee",
                        "security_deposit",
                        "maintenance_fee",
                        "replacement_fee",
                        "insurance_fee",
                    ]
                ),
                payment_method=random.choice(
                    ["cash", "card", "online", "transfer", "check", "paypal", "stripe"]
                ),
                description=random.choice(
                    [
                        "Account deposit",
                        "Late fee payment",
                        "Equipment rental fee",
                        "Refund for early return",
                        "Security deposit",
                        "Maintenance fee",
                        "Replacement fee",
                        "Insurance coverage",
                        "Extended rental fee",
                        "Damage deposit",
                        "Processing fee",
                        "Administrative fee",
                        "Equipment upgrade fee",
                        "Training session fee",
                        "Workshop participation fee",
                        "Special equipment access fee",
                        "Weekend rental surcharge",
                        "Holiday rental fee",
                    ]
                ),
                status="completed",
                processed_at=datetime.now()
                - timedelta(days=random.randint(1, 365)),  # Extended to 1 year
            )
            db.session.add(payment)
    db.session.commit()
    # Create 10x more logs
    for i in range(1, 50001):  # 50,000 logs
        user = random.choice(User.query.all())  # Use User.query.all() to get all users
        log = Log(
            user_id=user.id,
            action_type=random.choice(
                [
                    "login",
                    "logout",
                    "borrow",
                    "return",
                    "payment",
                    "profile_update",
                    "password_change",
                    "search",
                    "view_item",
                    "view_locker",
                    "export_data",
                ]
            ),
            timestamp=datetime.now()
            - timedelta(
                days=random.randint(1, 90), hours=random.randint(0, 23)
            ),  # Use datetime.now()
            notes="Auto-generated log entry.",
        )
        db.session.add(log)
    db.session.commit()
    print(
        f"Demo data created: {len(User.query.all())} users, {len(Locker.query.all())} lockers, {len(Item.query.all())} items, {len(Borrow.query.all())} borrows, {len(Payment.query.all())} payments, {len(Log.query.all())} logs."
    )
    print("\nDemo credentials:")
    print("Username: admin, Password: admin123 (Admin)")
    for user in User.query.all()[1:4]:  # Show first 3 students
        print(f"Username: {user.username}, Password: password123 (Student)")


def load_simple_demo_data(db, User, Locker, Item, Log, Borrow, Payment):
    """Create a small set of demo data for testing with PostgreSQL."""
    import random
    from datetime import datetime, timedelta

    from werkzeug.security import generate_password_hash

    # Clear existing data
    db.drop_all()
    db.create_all()

    # Create users
    users = []
    for i in range(1, 11):
        user = User(
            username=f"student{i}",
            password_hash=generate_password_hash("password123"),
            email=f"student{i}@example.com",
            first_name=f"Student{i}",
            last_name=f"User{i}",
            role="student",
            department="CS",
            balance=10.0,
            is_active=True,
        )
        db.session.add(user)
        users.append(user)

    # Create admin user
    admin = User(
        username="admin",
        password_hash=generate_password_hash("admin123"),
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        role="admin",
        department="IT",
        balance=0.0,
        is_active=True,
    )
    db.session.add(admin)

    # Create exactly 62 lockers with precise RS485 mapping
    lockers = []
    # RS485 mapping for all 62 lockers (based on the provided data)
    rs485_mapping_simple = [
        # Global, armoire, carte, casier, rs485_address, rs485_locker_number
        (1, 1, 1, 1, 1, 1), (2, 1, 1, 2, 1, 2), (3, 1, 1, 3, 1, 3), (4, 1, 1, 4, 1, 4),
        (5, 1, 1, 5, 1, 5), (6, 1, 1, 6, 1, 6), (7, 1, 1, 7, 1, 7), (8, 1, 1, 8, 1, 8),
        (9, 1, 1, 9, 1, 9), (10, 1, 1, 10, 1, 10), (11, 1, 1, 11, 1, 11), (12, 1, 1, 12, 1, 12),
        (13, 1, 1, 13, 1, 13), (14, 1, 1, 14, 1, 14),
        
        (15, 2, 2, 1, 2, 1), (16, 2, 2, 2, 2, 2), (17, 2, 2, 3, 2, 3), (18, 2, 2, 4, 2, 4),
        (19, 2, 2, 5, 2, 5), (20, 2, 2, 6, 2, 6), (21, 2, 2, 7, 2, 7), (22, 2, 2, 8, 2, 8),
        (23, 2, 2, 9, 2, 9), (24, 2, 2, 10, 2, 10), (25, 2, 2, 11, 2, 11), (26, 2, 2, 12, 2, 12),
        (27, 2, 2, 13, 2, 13), (28, 2, 2, 14, 2, 14), (29, 2, 2, 15, 2, 15), (30, 2, 2, 16, 2, 16),
        (31, 2, 2, 17, 2, 17), (32, 2, 2, 18, 2, 18), (33, 2, 2, 19, 2, 19), (34, 2, 2, 20, 2, 20),
        (35, 2, 2, 21, 2, 21), (36, 2, 2, 22, 2, 22), (37, 2, 2, 23, 2, 23), (38, 2, 2, 24, 2, 24),
        
        (39, 2, 3, 1, 3, 1), (40, 2, 3, 2, 3, 2), (41, 2, 3, 3, 3, 3), (42, 2, 3, 4, 3, 4),
        (43, 2, 3, 5, 3, 5), (44, 2, 3, 6, 3, 6), (45, 2, 3, 7, 3, 7), (46, 2, 3, 8, 3, 8),
        (47, 2, 3, 9, 3, 9), (48, 2, 3, 10, 3, 10), (49, 2, 3, 11, 3, 11), (50, 2, 3, 12, 3, 12),
        (51, 2, 3, 13, 3, 13), (52, 2, 3, 14, 3, 14), (53, 2, 3, 15, 3, 15), (54, 2, 3, 16, 3, 16),
        (55, 2, 3, 17, 3, 17), (56, 2, 3, 18, 3, 18), (57, 2, 3, 19, 3, 19), (58, 2, 3, 20, 3, 20),
        (59, 2, 3, 21, 3, 21), (60, 2, 3, 22, 3, 22), (61, 2, 3, 23, 3, 23), (62, 2, 3, 24, 3, 24)
    ]
    
    for global_id, armoire, carte, casier, rs485_address, rs485_locker_number in rs485_mapping_simple:
        locker = Locker(
            name=f"Locker {global_id}",
            number=f"L{global_id:03d}",
            location=f"Armoire {armoire}, Carte {carte}, Casier {casier}",
            status="available",
            capacity=5,
            current_occupancy=0,
            rs485_address=rs485_address,
            rs485_locker_number=rs485_locker_number,
            is_active=True,
        )
        db.session.add(locker)
        lockers.append(locker)

    # Create items
    items = []
    for i in range(1, 21):
        item = Item(
            name=f"Item {i}",
            description=f"Demo item {i}",
            category="Electronics",
            condition="good",
            status="available",
            locker_id=lockers[i % 62].id,  # Use modulo 62 for 62 lockers
            is_active=True,
        )
        db.session.add(item)
        items.append(item)

    db.session.commit()

    # Create some borrows
    borrows = []
    for i in range(1, 21):
        borrow = Borrow(
            user_id=users[i % 10].id,
            item_id=items[i % 20].id,
            locker_id=lockers[i % 62].id,  # Use modulo 62 for 62 lockers
            borrowed_at=datetime.now(),
            due_date=datetime.now() + timedelta(days=7),
            status="active",
        )
        db.session.add(borrow)
        borrows.append(borrow)

    db.session.commit()

    # Create some logs
    for i in range(1, 21):
        log = Log(
            user_id=users[i % 10].id,
            item_id=items[i % 20].id,
            locker_id=lockers[i % 62].id,  # Use modulo 62 for 62 lockers
            action_type="borrow",
            timestamp=datetime.now(),
        )
        db.session.add(log)

    db.session.commit()
    print("✓ Simple demo data loaded successfully!")



