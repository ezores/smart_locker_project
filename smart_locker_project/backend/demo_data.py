"""
Smart Locker System - Demo Data Module

@author Alp
@date 2024-12-XX
@description Demo data generator for testing the Smart Locker System
"""

from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

def create_demo_data(db, User, Locker, Item, Log, Borrow, Return, Payment, Notification, SystemSetting):
    """Create comprehensive demo data for testing the system"""
    
    print("Creating comprehensive demo data...")
    
    # Clear ALL existing data
    Log.query.delete()
    Return.query.delete()
    Borrow.query.delete()
    Payment.query.delete()
    Notification.query.delete()
    Item.query.delete()
    Locker.query.delete()
    User.query.delete()  # Clear all users including admin
    
    # Create admin user first
    admin_user = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        role='admin',
        balance=0.00,
        department='IT',
        is_active=True
    )
    db.session.add(admin_user)
    
    # Create 10x more demo users
    for i in range(1, 501):  # 500 students
        user = User(
            username=f'student{i}',
            password_hash=generate_password_hash('password123'),
            email=f'student{i}@example.com',
            first_name=f'Student{i}',
            last_name=f'User{i}',
            role='student',
            department=random.choice(['CS', 'Math', 'Physics', 'Chemistry', 'Biology', 'Engineering']),
            balance=random.uniform(0, 100),
            is_active=True
        )
        db.session.add(user)
    db.session.commit()
    # Create 10x more lockers
    for i in range(1, 101):  # 100 lockers
        locker = Locker(
            name=f'Locker {i}',
            number=f'L{i}',
            location=f'Building {random.choice(["A","B","C","D","E","F"])}',
            capacity=random.randint(5, 15),
            current_occupancy=0,
            status='available'
        )
        db.session.add(locker)
    db.session.commit()
    # Create 10x more items
    for i in range(1, 2001):  # 2000 items
        item = Item(
            name=f'Item {i}',
            description=f'Description for item {i}',
            category=random.choice(['Electronics', 'Audio/Video', 'VR/Gaming', 'Drones', 'Robotics', '3D Printing', 'Manufacturing', 'Testing', 'Tools']),
            brand=random.choice(['BrandA', 'BrandB', 'BrandC', 'BrandD']),
            model=f'Model{i}',
            condition=random.choice(['new', 'good', 'fair', 'poor']),
            value=random.uniform(10, 5000),
            locker_id=random.choice(Locker.query.all()).id, # Use Locker.query.all() to get all lockers
            is_active=True
        )
        db.session.add(item)
    db.session.commit()
    # Create 10x more borrows and returns
    for i in range(1, 5001):  # 5000 borrows
        user = random.choice(User.query.all()[1:]) # Use User.query.all() to get all users
        item = random.choice(Item.query.all()) # Use Item.query.all() to get all items
        locker = random.choice(Locker.query.all()) # Use Locker.query.all() to get all lockers
        borrowed_at = datetime.now() - timedelta(days=random.randint(1, 90)) # Use datetime.now()
        due_date = borrowed_at + timedelta(days=random.randint(3, 14))
        returned = random.choice([True, False, False])
        borrow = Borrow(
            user_id=user.id,
            item_id=item.id,
            locker_id=locker.id,
            borrowed_at=borrowed_at,
            due_date=due_date,
            status='returned' if returned else 'active',
            returned_at=(borrowed_at + timedelta(days=random.randint(1, 20))) if returned else None
        )
        db.session.add(borrow)
    db.session.commit()
    for borrow in Borrow.query.all(): # Use Borrow.query.all() to get all borrows
        if borrow.status == 'returned':
            return_record = Return(
                borrow_id=borrow.id,
                user_id=borrow.user_id,
                item_id=borrow.item_id,
                locker_id=borrow.locker_id,
                returned_at=borrow.returned_at,
                condition_returned=random.choice(['same', 'damaged', 'missing_parts']),
                notes='Auto-generated return'
            )
            db.session.add(return_record)
    db.session.commit()
    # Create 10x more payments
    for user in User.query.all()[1:]: # Use User.query.all() to get all users
        for _ in range(random.randint(10, 20)):
            payment = Payment(
                user_id=user.id,
                amount=random.uniform(5, 200),
                payment_type=random.choice(['deposit', 'withdrawal', 'fee', 'refund', 'late_fee', 'equipment_fee']),
                payment_method=random.choice(['cash', 'card', 'online', 'transfer', 'check']),
                description=random.choice(['Account deposit', 'Late fee payment', 'Equipment rental fee', 'Refund for early return', 'Security deposit', 'Maintenance fee', 'Replacement fee']),
                status='completed',
                processed_at=datetime.now() - timedelta(days=random.randint(1, 90)) # Use datetime.now()
            )
            db.session.add(payment)
    db.session.commit()
    # Create 10x more notifications
    for user in User.query.all()[1:]: # Use User.query.all() to get all users
        for _ in range(random.randint(5, 15)):
            notification = Notification(
                user_id=user.id,
                title=f'Notification for user {user.username}',
                message='This is a demo notification.',
                notification_type=random.choice(['info', 'warning', 'error', 'success']),
                is_read=random.choice([True, False])
            )
            db.session.add(notification)
    db.session.commit()
    # Create 10x more logs
    for i in range(1, 50001):  # 50,000 logs
        user = random.choice(User.query.all()) # Use User.query.all() to get all users
        log = Log(
            user_id=user.id,
            action_type=random.choice(['login', 'logout', 'borrow', 'return', 'payment', 'profile_update', 'password_change', 'search', 'view_item', 'view_locker', 'export_data']),
            timestamp=datetime.now() - timedelta(days=random.randint(1, 90), hours=random.randint(0, 23)), # Use datetime.now()
            action_details='Auto-generated log entry.'
        )
        db.session.add(log)
    db.session.commit()
    print(f"Demo data created: {len(User.query.all())} users, {len(Locker.query.all())} lockers, {len(Item.query.all())} items, {len(Borrow.query.all())} borrows, {len(Return.query.all())} returns, {len(Payment.query.all())} payments, {len(Notification.query.all())} notifications, {len(Log.query.all())} logs.")
    print("\nDemo credentials:")
    print("Username: admin, Password: admin123 (Admin)")
    for user in User.query.all()[1:4]:  # Show first 3 students
        print(f"Username: {user.username}, Password: password123 (Student)")

def load_simple_demo_data(db):
    """Create a small set of demo data for testing with PostgreSQL."""
    from werkzeug.security import generate_password_hash
    import random
    from datetime import datetime, timedelta
    
    # Import models
    from models import User, Locker, Item, Borrow, Return, Log, Payment
    
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    # Create users
    users = []
    for i in range(1, 11):
        user = User(
            username=f'student{i}',
            password_hash=generate_password_hash('password123'),
            email=f'student{i}@example.com',
            first_name=f'Student{i}',
            last_name=f'User{i}',
            role='student',
            department='CS',
            balance=10.0,
            is_active=True
        )
        db.session.add(user)
        users.append(user)
    
    # Create admin user
    admin = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        role='admin',
        department='IT',
        balance=0.0,
        is_active=True
    )
    db.session.add(admin)
    
    # Create lockers with proper number field
    lockers = []
    for i in range(1, 11):
        locker = Locker(
            name=f'Locker {i}', 
            number=f'L{i:03d}', 
            location=f'Room {i}', 
            status='available',
            capacity=5,
            current_occupancy=0,
            is_active=True
        )
        db.session.add(locker)
        lockers.append(locker)
    
    # Create items
    items = []
    for i in range(1, 21):
        item = Item(
            name=f'Item {i}', 
            description=f'Demo item {i}', 
            category='Electronics',
            condition='good',
            status='available',
            locker_id=lockers[i%10].id,
            is_active=True
        )
        db.session.add(item)
        items.append(item)
    
    db.session.commit()
    
    # Create some borrows
    borrows = []
    for i in range(1, 21):
        borrow = Borrow(
            user_id=users[i%10].id, 
            item_id=items[i%20].id, 
            locker_id=lockers[i%10].id, 
            borrowed_at=datetime.now(),
            due_date=datetime.now() + timedelta(days=7),
            status='active'
        )
        db.session.add(borrow)
        borrows.append(borrow)
    
    db.session.commit()
    
    # Create some logs
    for i in range(1, 21):
        log = Log(
            user_id=users[i%10].id, 
            item_id=items[i%20].id, 
            locker_id=lockers[i%10].id, 
            action_type='borrow', 
            timestamp=datetime.now()
        )
        db.session.add(log)
    
    db.session.commit()
    print('✓ Simple demo data loaded successfully!')

def clear_demo_data(db, User, Locker, Item, Log, Borrow, Return, Payment, Notification):
    """Clear all demo data from the database"""
    print("Clearing demo data...")
    
    Log.query.delete()
    Return.query.delete()
    Borrow.query.delete()
    Payment.query.delete()
    Notification.query.delete()
    Item.query.delete()
    Locker.query.delete()
    User.query.filter(User.username != 'admin').delete()
    
    db.session.commit()
    print("Demo data cleared successfully!") 