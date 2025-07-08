"""
Smart Locker System - Demo Data Module

@author Alp
@date 2024-12-XX
@description Demo data generator for testing the Smart Locker System
"""

from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

def create_demo_data(db, User, Locker, Item, Log):
    """Create demo data for testing the system"""
    
    print("Creating demo data...")
    
    # Clear ALL existing data
    Log.query.delete()
    Item.query.delete()
    Locker.query.delete()
    User.query.delete()  # Clear all users including admin
    
    # Create admin user first
    admin_user = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),
        role='admin'
    )
    db.session.add(admin_user)
    
    # Create demo users
    demo_users = [
        {'username': 'student', 'password': 'password123', 'role': 'student'},
        {'username': 'john.doe', 'password': 'password123', 'role': 'student'},
        {'username': 'jane.smith', 'password': 'password123', 'role': 'student'},
        {'username': 'mike.wilson', 'password': 'password123', 'role': 'student'},
        {'username': 'sarah.jones', 'password': 'password123', 'role': 'student'},
        {'username': 'david.brown', 'password': 'password123', 'role': 'student'},
        {'username': 'emma.davis', 'password': 'password123', 'role': 'student'},
        {'username': 'alex.taylor', 'password': 'password123', 'role': 'student'},
        {'username': 'lisa.anderson', 'password': 'password123', 'role': 'student'},
        {'username': 'tom.martinez', 'password': 'password123', 'role': 'student'},
        {'username': 'anna.garcia', 'password': 'password123', 'role': 'student'},
    ]
    
    users = [admin_user]  # Start with admin user
    for user_data in demo_users:
        user = User(
            username=user_data['username'],
            password_hash=generate_password_hash(user_data['password']),
            role=user_data['role']
        )
        db.session.add(user)
        users.append(user)
    
    # Create demo lockers
    demo_lockers = [
        'A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3', 'D1', 'D2', 'D3'
    ]
    
    lockers = []
    for locker_name in demo_lockers:
        locker = Locker(name=locker_name)
        db.session.add(locker)
        lockers.append(locker)
    
    # Create demo items
    demo_items = [
        'Laptop Dell XPS 13',
        'Laptop MacBook Pro',
        'Projector Epson',
        'Camera Canon EOS',
        'Microphone Shure',
        'Tablet iPad Pro',
        'VR Headset Oculus',
        'Drone DJI Mavic',
        '3D Printer Prusa',
        'Arduino Kit',
        'Raspberry Pi 4',
        'Soldering Iron',
        'Oscilloscope',
        'Multimeter',
        'Tool Kit',
    ]
    
    items = []
    for item_name in demo_items:
        item = Item(
            name=item_name,
            locker_id=random.choice(lockers).id
        )
        db.session.add(item)
        items.append(item)
    
    # Commit to get IDs
    db.session.commit()
    
    # Create demo logs (transactions) - More realistic scenario
    now = datetime.now()
    
    # Track active borrows to ensure realistic return patterns
    active_borrows = {}  # {item_id: {user_id, borrow_time, locker_id}}
    
    # Generate logs for the past 30 days
    for day in range(30):
        base_date = now - timedelta(days=day)
        
        # Generate 3-8 transactions per day
        num_transactions = random.randint(3, 8)
        
        for _ in range(num_transactions):
            # Random time during the day
            hour = random.randint(8, 18)  # 8 AM to 6 PM
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            timestamp = base_date.replace(hour=hour, minute=minute, second=second)
            user = random.choice(users)
            
            # Decide action based on current state
            available_items = [item for item in items if item.id not in active_borrows]
            
            if available_items and random.random() < 0.7:  # 70% chance to borrow if items available
                # Create a borrow
                item = random.choice(available_items)
                locker = random.choice(lockers)
                
                log = Log(
                    user_id=user.id,
                    item_id=item.id,
                    locker_id=locker.id,
                    action_type='borrow',
                    timestamp=timestamp
                )
                db.session.add(log)
                
                # Track this borrow
                active_borrows[item.id] = {
                    'user_id': user.id,
                    'borrow_time': timestamp,
                    'locker_id': locker.id
                }
                
            elif active_borrows and random.random() < 0.8:  # 80% chance to return if items borrowed
                # Create a return
                item_id = random.choice(list(active_borrows.keys()))
                borrow_info = active_borrows[item_id]
                
                log = Log(
                    user_id=borrow_info['user_id'],
                    item_id=item_id,
                    locker_id=borrow_info['locker_id'],
                    action_type='return',
                    timestamp=timestamp
                )
                db.session.add(log)
                
                # Remove from active borrows
                del active_borrows[item_id]
    
    # Add some login/logout logs
    for day in range(30):
        base_date = now - timedelta(days=day)
        for user in users:
            if random.random() < 0.3:  # 30% chance of login per day per user
                hour = random.randint(8, 18)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                login_time = base_date.replace(hour=hour, minute=minute, second=second)
                
                # Login log
                log = Log(
                    user_id=user.id,
                    action_type='login',
                    timestamp=login_time
                )
                db.session.add(log)
                
                # Logout log (same day, later)
                logout_hour = min(22, hour + random.randint(1, 4))
                logout_time = base_date.replace(hour=logout_hour, minute=random.randint(0, 59), second=random.randint(0, 59))
                
                log = Log(
                    user_id=user.id,
                    action_type='logout',
                    timestamp=logout_time
                )
                db.session.add(log)
    
    # Commit all logs
    db.session.commit()
    
    print(f"Demo data created successfully!")
    print(f"- {len(users)} users")
    print(f"- {len(lockers)} lockers")
    print(f"- {len(items)} items")
    print(f"- {Log.query.count()} transaction logs")
    print("\nDemo credentials:")
    print("Username: admin, Password: admin123 (Admin)")
    for user in users[:3]:  # Show first 3 users
        print(f"Username: {user.username}, Password: password123 (Student)")

def clear_demo_data(db, User, Locker, Item, Log):
    """Clear all demo data from the database"""
    print("Clearing demo data...")
    
    Log.query.delete()
    Item.query.delete()
    Locker.query.delete()
    User.query.filter(User.username != 'admin').delete()
    
    db.session.commit()
    print("Demo data cleared successfully!") 