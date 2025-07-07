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
    
    # Clear existing data (except admin user)
    Log.query.delete()
    Item.query.delete()
    Locker.query.delete()
    User.query.filter(User.username != 'admin').delete()
    
    # Create demo users
    demo_users = [
        {'username': 'john.doe', 'password': 'password123', 'role': 'employee'},
        {'username': 'jane.smith', 'password': 'password123', 'role': 'employee'},
        {'username': 'mike.wilson', 'password': 'password123', 'role': 'employee'},
        {'username': 'sarah.jones', 'password': 'password123', 'role': 'employee'},
        {'username': 'david.brown', 'password': 'password123', 'role': 'employee'},
        {'username': 'emma.davis', 'password': 'password123', 'role': 'employee'},
        {'username': 'alex.taylor', 'password': 'password123', 'role': 'employee'},
        {'username': 'lisa.anderson', 'password': 'password123', 'role': 'employee'},
        {'username': 'tom.martinez', 'password': 'password123', 'role': 'employee'},
        {'username': 'anna.garcia', 'password': 'password123', 'role': 'employee'},
    ]
    
    users = []
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
    
    # Create demo logs (transactions)
    actions = ['borrow', 'return']
    now = datetime.now()
    
    # Generate logs for the past 30 days
    for day in range(30):
        base_date = now - timedelta(days=day)
        
        # Generate 5-15 transactions per day
        num_transactions = random.randint(5, 15)
        
        for _ in range(num_transactions):
            # Random time during the day
            hour = random.randint(8, 18)  # 8 AM to 6 PM
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            timestamp = base_date.replace(hour=hour, minute=minute, second=second)
            action = random.choice(actions)
            user = random.choice(users)
            item = random.choice(items)
            locker = random.choice(lockers)
            
            log = Log(
                user_id=user.id,
                item_id=item.id,
                locker_id=locker.id,
                action_type=action,
                timestamp=timestamp
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
        print(f"Username: {user.username}, Password: password123 (Employee)")

def clear_demo_data(db, User, Locker, Item, Log):
    """Clear all demo data from the database"""
    print("Clearing demo data...")
    
    Log.query.delete()
    Item.query.delete()
    Locker.query.delete()
    User.query.filter(User.username != 'admin').delete()
    
    db.session.commit()
    print("Demo data cleared successfully!") 