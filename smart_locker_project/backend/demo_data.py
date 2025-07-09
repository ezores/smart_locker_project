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
    
    # Create comprehensive demo users
    demo_users = [
        {'username': 'student', 'password': 'password123', 'role': 'student', 'first_name': 'John', 'last_name': 'Student', 'email': 'student@example.com', 'department': 'Computer Science'},
        {'username': 'john.doe', 'password': 'password123', 'role': 'student', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com', 'department': 'Engineering'},
        {'username': 'jane.smith', 'password': 'password123', 'role': 'student', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane.smith@example.com', 'department': 'Physics'},
        {'username': 'mike.wilson', 'password': 'password123', 'role': 'student', 'first_name': 'Mike', 'last_name': 'Wilson', 'email': 'mike.wilson@example.com', 'department': 'Mathematics'},
        {'username': 'sarah.jones', 'password': 'password123', 'role': 'student', 'first_name': 'Sarah', 'last_name': 'Jones', 'email': 'sarah.jones@example.com', 'department': 'Chemistry'},
        {'username': 'david.brown', 'password': 'password123', 'role': 'student', 'first_name': 'David', 'last_name': 'Brown', 'email': 'david.brown@example.com', 'department': 'Biology'},
        {'username': 'emma.davis', 'password': 'password123', 'role': 'student', 'first_name': 'Emma', 'last_name': 'Davis', 'email': 'emma.davis@example.com', 'department': 'Psychology'},
        {'username': 'alex.taylor', 'password': 'password123', 'role': 'student', 'first_name': 'Alex', 'last_name': 'Taylor', 'email': 'alex.taylor@example.com', 'department': 'Economics'},
        {'username': 'lisa.anderson', 'password': 'password123', 'role': 'student', 'first_name': 'Lisa', 'last_name': 'Anderson', 'email': 'lisa.anderson@example.com', 'department': 'History'},
        {'username': 'tom.martinez', 'password': 'password123', 'role': 'student', 'first_name': 'Tom', 'last_name': 'Martinez', 'email': 'tom.martinez@example.com', 'department': 'Sociology'},
        {'username': 'anna.garcia', 'password': 'password123', 'role': 'student', 'first_name': 'Anna', 'last_name': 'Garcia', 'email': 'anna.garcia@example.com', 'department': 'Art'},
        {'username': 'chris.lee', 'password': 'password123', 'role': 'student', 'first_name': 'Chris', 'last_name': 'Lee', 'email': 'chris.lee@example.com', 'department': 'Music'},
        {'username': 'maria.rodriguez', 'password': 'password123', 'role': 'student', 'first_name': 'Maria', 'last_name': 'Rodriguez', 'email': 'maria.rodriguez@example.com', 'department': 'Philosophy'},
        {'username': 'james.miller', 'password': 'password123', 'role': 'student', 'first_name': 'James', 'last_name': 'Miller', 'email': 'james.miller@example.com', 'department': 'Political Science'},
        {'username': 'sophia.white', 'password': 'password123', 'role': 'student', 'first_name': 'Sophia', 'last_name': 'White', 'email': 'sophia.white@example.com', 'department': 'Linguistics'},
    ]
    
    users = [admin_user]  # Start with admin user
    for user_data in demo_users:
        user = User(
            username=user_data['username'],
            password_hash=generate_password_hash(user_data['password']),
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            department=user_data['department'],
            balance=random.uniform(0, 100),  # Random balance
            is_active=True
        )
        db.session.add(user)
        users.append(user)
    
    # Create comprehensive demo lockers
    demo_lockers = [
        {'name': 'Locker A1', 'number': 'A1', 'location': 'Building A, Floor 1', 'capacity': 5},
        {'name': 'Locker A2', 'number': 'A2', 'location': 'Building A, Floor 1', 'capacity': 3},
        {'name': 'Locker A3', 'number': 'A3', 'location': 'Building A, Floor 1', 'capacity': 4},
        {'name': 'Locker B1', 'number': 'B1', 'location': 'Building B, Floor 1', 'capacity': 6},
        {'name': 'Locker B2', 'number': 'B2', 'location': 'Building B, Floor 1', 'capacity': 4},
        {'name': 'Locker B3', 'number': 'B3', 'location': 'Building B, Floor 1', 'capacity': 5},
        {'name': 'Locker C1', 'number': 'C1', 'location': 'Building C, Floor 1', 'capacity': 3},
        {'name': 'Locker C2', 'number': 'C2', 'location': 'Building C, Floor 1', 'capacity': 4},
        {'name': 'Locker C3', 'number': 'C3', 'location': 'Building C, Floor 1', 'capacity': 5},
        {'name': 'Locker D1', 'number': 'D1', 'location': 'Building D, Floor 1', 'capacity': 6},
        {'name': 'Locker D2', 'number': 'D2', 'location': 'Building D, Floor 1', 'capacity': 4},
        {'name': 'Locker D3', 'number': 'D3', 'location': 'Building D, Floor 1', 'capacity': 3},
        {'name': 'Locker E1', 'number': 'E1', 'location': 'Building E, Floor 2', 'capacity': 5},
        {'name': 'Locker E2', 'number': 'E2', 'location': 'Building E, Floor 2', 'capacity': 4},
        {'name': 'Locker E3', 'number': 'E3', 'location': 'Building E, Floor 2', 'capacity': 6},
    ]
    
    lockers = []
    for locker_data in demo_lockers:
        locker = Locker(
            name=locker_data['name'],
            number=locker_data['number'],
            location=locker_data['location'],
            capacity=locker_data['capacity'],
            current_occupancy=0,
            status='available'
        )
        db.session.add(locker)
        lockers.append(locker)
    
    # Commit lockers first to get their IDs
    db.session.commit()

    # Create comprehensive demo items
    demo_items = [
        # Electronics
        {'name': 'Laptop Dell XPS 13', 'category': 'Electronics', 'brand': 'Dell', 'model': 'XPS 13', 'condition': 'good', 'value': 1200.00},
        {'name': 'Laptop MacBook Pro', 'category': 'Electronics', 'brand': 'Apple', 'model': 'MacBook Pro', 'condition': 'new', 'value': 1800.00},
        {'name': 'Laptop HP Pavilion', 'category': 'Electronics', 'brand': 'HP', 'model': 'Pavilion', 'condition': 'good', 'value': 800.00},
        {'name': 'Laptop Lenovo ThinkPad', 'category': 'Electronics', 'brand': 'Lenovo', 'model': 'ThinkPad', 'condition': 'good', 'value': 1000.00},
        {'name': 'Tablet iPad Pro', 'category': 'Electronics', 'brand': 'Apple', 'model': 'iPad Pro', 'condition': 'new', 'value': 900.00},
        {'name': 'Tablet Samsung Galaxy', 'category': 'Electronics', 'brand': 'Samsung', 'model': 'Galaxy Tab', 'condition': 'good', 'value': 500.00},
        {'name': 'Smartphone iPhone 14', 'category': 'Electronics', 'brand': 'Apple', 'model': 'iPhone 14', 'condition': 'new', 'value': 1000.00},
        {'name': 'Smartphone Samsung Galaxy', 'category': 'Electronics', 'brand': 'Samsung', 'model': 'Galaxy S23', 'condition': 'good', 'value': 800.00},
        
        # Audio/Video Equipment
        {'name': 'Projector Epson', 'category': 'Audio/Video', 'brand': 'Epson', 'model': 'PowerLite', 'condition': 'good', 'value': 800.00},
        {'name': 'Projector BenQ', 'category': 'Audio/Video', 'brand': 'BenQ', 'model': 'TH685P', 'condition': 'good', 'value': 600.00},
        {'name': 'Camera Canon EOS', 'category': 'Audio/Video', 'brand': 'Canon', 'model': 'EOS R6', 'condition': 'good', 'value': 2500.00},
        {'name': 'Camera Sony Alpha', 'category': 'Audio/Video', 'brand': 'Sony', 'model': 'Alpha A7', 'condition': 'good', 'value': 2000.00},
        {'name': 'Microphone Shure', 'category': 'Audio/Video', 'brand': 'Shure', 'model': 'SM58', 'condition': 'good', 'value': 100.00},
        {'name': 'Microphone Blue Yeti', 'category': 'Audio/Video', 'brand': 'Blue', 'model': 'Yeti', 'condition': 'good', 'value': 130.00},
        {'name': 'Speaker JBL', 'category': 'Audio/Video', 'brand': 'JBL', 'model': 'Flip 5', 'condition': 'good', 'value': 120.00},
        {'name': 'Speaker Bose', 'category': 'Audio/Video', 'brand': 'Bose', 'model': 'SoundLink', 'condition': 'good', 'value': 200.00},
        
        # VR and Gaming
        {'name': 'VR Headset Oculus', 'category': 'VR/Gaming', 'brand': 'Meta', 'model': 'Quest 2', 'condition': 'good', 'value': 400.00},
        {'name': 'VR Headset HTC Vive', 'category': 'VR/Gaming', 'brand': 'HTC', 'model': 'Vive Pro', 'condition': 'good', 'value': 800.00},
        {'name': 'Gaming Console PS5', 'category': 'VR/Gaming', 'brand': 'Sony', 'model': 'PlayStation 5', 'condition': 'good', 'value': 500.00},
        {'name': 'Gaming Console Xbox', 'category': 'VR/Gaming', 'brand': 'Microsoft', 'model': 'Xbox Series X', 'condition': 'good', 'value': 500.00},
        
        # Drones and Robotics
        {'name': 'Drone DJI Mavic', 'category': 'Drones', 'brand': 'DJI', 'model': 'Mavic Air 2', 'condition': 'good', 'value': 800.00},
        {'name': 'Drone Parrot Anafi', 'category': 'Drones', 'brand': 'Parrot', 'model': 'Anafi', 'condition': 'good', 'value': 600.00},
        {'name': 'Robot Kit LEGO', 'category': 'Robotics', 'brand': 'LEGO', 'model': 'Mindstorms', 'condition': 'good', 'value': 350.00},
        {'name': 'Robot Kit Arduino', 'category': 'Robotics', 'brand': 'Arduino', 'model': 'Robot Kit', 'condition': 'good', 'value': 200.00},
        
        # 3D Printing and Manufacturing
        {'name': '3D Printer Prusa', 'category': '3D Printing', 'brand': 'Prusa', 'model': 'i3 MK3S', 'condition': 'good', 'value': 800.00},
        {'name': '3D Printer Creality', 'category': '3D Printing', 'brand': 'Creality', 'model': 'Ender 3', 'condition': 'good', 'value': 200.00},
        {'name': 'Laser Cutter Epilog', 'category': 'Manufacturing', 'brand': 'Epilog', 'model': 'Laser Mini', 'condition': 'good', 'value': 8000.00},
        {'name': 'CNC Machine Haas', 'category': 'Manufacturing', 'brand': 'Haas', 'model': 'Mini Mill', 'condition': 'good', 'value': 25000.00},
        
        # Electronics and Testing
        {'name': 'Arduino Kit', 'category': 'Electronics', 'brand': 'Arduino', 'model': 'Starter Kit', 'condition': 'good', 'value': 80.00},
        {'name': 'Raspberry Pi 4', 'category': 'Electronics', 'brand': 'Raspberry Pi', 'model': '4B 8GB', 'condition': 'good', 'value': 75.00},
        {'name': 'Soldering Iron', 'category': 'Electronics', 'brand': 'Weller', 'model': 'WE1010', 'condition': 'good', 'value': 150.00},
        {'name': 'Oscilloscope', 'category': 'Electronics', 'brand': 'Tektronix', 'model': 'TBS1052B', 'condition': 'good', 'value': 400.00},
        {'name': 'Multimeter', 'category': 'Electronics', 'brand': 'Fluke', 'model': '117', 'condition': 'good', 'value': 200.00},
        {'name': 'Function Generator', 'category': 'Electronics', 'brand': 'Rigol', 'model': 'DG1022Z', 'condition': 'good', 'value': 300.00},
        
        # Tools and Equipment
        {'name': 'Tool Kit', 'category': 'Tools', 'brand': 'DeWalt', 'model': 'Mechanics Set', 'condition': 'good', 'value': 150.00},
        {'name': 'Drill Set', 'category': 'Tools', 'brand': 'Milwaukee', 'model': 'M18', 'condition': 'good', 'value': 200.00},
        {'name': 'Screwdriver Set', 'category': 'Tools', 'brand': 'Wera', 'model': 'Kraftform', 'condition': 'good', 'value': 80.00},
        {'name': 'Wrench Set', 'category': 'Tools', 'brand': 'Snap-on', 'model': 'Professional', 'condition': 'good', 'value': 300.00},
        
        # Lab Equipment
        {'name': 'Microscope', 'category': 'Lab Equipment', 'brand': 'Olympus', 'model': 'CX23', 'condition': 'good', 'value': 1200.00},
        {'name': 'Centrifuge', 'category': 'Lab Equipment', 'brand': 'Eppendorf', 'model': '5810R', 'condition': 'good', 'value': 5000.00},
        {'name': 'pH Meter', 'category': 'Lab Equipment', 'brand': 'Hanna', 'model': 'HI98107', 'condition': 'good', 'value': 100.00},
        {'name': 'Scale Digital', 'category': 'Lab Equipment', 'brand': 'Ohaus', 'model': 'Pioneer', 'condition': 'good', 'value': 200.00},
        
        # Sports and Recreation
        {'name': 'Bicycle', 'category': 'Sports', 'brand': 'Trek', 'model': 'FX 2', 'condition': 'good', 'value': 500.00},
        {'name': 'Tennis Racket', 'category': 'Sports', 'brand': 'Wilson', 'model': 'Pro Staff', 'condition': 'good', 'value': 200.00},
        {'name': 'Basketball', 'category': 'Sports', 'brand': 'Spalding', 'model': 'NBA Official', 'condition': 'good', 'value': 50.00},
        {'name': 'Soccer Ball', 'category': 'Sports', 'brand': 'Adidas', 'model': 'Champions League', 'condition': 'good', 'value': 40.00},
    ]
    
    items = []
    for item_data in demo_items:
        # Create multiple instances of each item
        for i in range(random.randint(1, 3)):  # 1-3 instances per item
            item = Item(
                name=f"{item_data['name']} #{i+1}" if i > 0 else item_data['name'],
                description=f"{item_data['brand']} {item_data['model']} - {item_data['condition']} condition",
                category=item_data['category'],
                brand=item_data['brand'],
                model=item_data['model'],
                condition=item_data['condition'],
                value=item_data['value'],
                status='available',
                locker_id=random.choice(lockers).id,
                is_active=True
            )
            db.session.add(item)
            items.append(item)
    
    # Commit to get IDs
    db.session.commit()
    
    # Create borrow/return records
    borrows = []
    returns = []
    now = datetime.now()
    
    # Generate realistic borrow/return history
    for _ in range(50):  # Create 50 borrow records
        user = random.choice(users[1:])  # Exclude admin
        item = random.choice(items)
        locker = random.choice(lockers)
        
        # Random date in the past 30 days
        days_ago = random.randint(1, 30)
        borrow_date = now - timedelta(days=days_ago)
        due_date = borrow_date + timedelta(days=random.randint(1, 14))  # 1-14 days loan
        
        borrow = Borrow(
            user_id=user.id,
            item_id=item.id,
            locker_id=locker.id,
            borrowed_at=borrow_date,
            due_date=due_date,
            status='returned' if random.random() < 0.8 else 'active',  # 80% returned
            notes=random.choice(['', 'For class project', 'Research purposes', 'Personal use'])
        )
        db.session.add(borrow)
        borrows.append(borrow)
        
        # Create return record for most borrows
        if borrow.status == 'returned':
            return_date = min(due_date, borrow_date + timedelta(days=random.randint(1, 10)))
            return_record = Return(
                borrow_id=borrow.id,
                user_id=user.id,
                item_id=item.id,
                locker_id=locker.id,
                returned_at=return_date,
                condition_returned=random.choice(['same', 'good', 'minor_damage']),
                notes=random.choice(['', 'Returned on time', 'Slight wear', 'Perfect condition'])
            )
            db.session.add(return_record)
            returns.append(return_record)
    
    # Create payment records
    payments = []
    payment_types = ['deposit', 'withdrawal', 'fee', 'refund']
    payment_methods = ['cash', 'card', 'online', 'transfer']
    
    for user in users[1:]:  # Exclude admin
        for _ in range(random.randint(1, 5)):  # 1-5 payments per user
            payment = Payment(
                user_id=user.id,
                amount=random.uniform(10, 100),
                payment_type=random.choice(payment_types),
                payment_method=random.choice(payment_methods),
                description=random.choice(['Account deposit', 'Late fee', 'Equipment fee', 'Refund']),
                status='completed',
                processed_at=now - timedelta(days=random.randint(1, 60))
            )
            db.session.add(payment)
            payments.append(payment)
    
    # Create notifications
    notifications = []
    notification_types = ['info', 'warning', 'error', 'success']
    
    for user in users[1:]:  # Exclude admin
        for _ in range(random.randint(0, 3)):  # 0-3 notifications per user
            notification = Notification(
                user_id=user.id,
                title=random.choice([
                    'Item due soon',
                    'Payment received',
                    'New item available',
                    'System maintenance',
                    'Welcome to Smart Locker'
                ]),
                message=random.choice([
                    'Your borrowed item is due in 2 days.',
                    'Your payment of $25 has been processed.',
                    'New equipment is available for borrowing.',
                    'System will be down for maintenance tonight.',
                    'Welcome to the Smart Locker System!'
                ]),
                notification_type=random.choice(notification_types),
                is_read=random.choice([True, False])
            )
            db.session.add(notification)
            notifications.append(notification)
    
    # Create comprehensive logs
    logs = []
    
    # Login/logout logs
    for day in range(30):
        base_date = now - timedelta(days=day)
        for user in users:
            if random.random() < 0.4:  # 40% chance of login per day per user
                hour = random.randint(8, 18)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                login_time = base_date.replace(hour=hour, minute=minute, second=second)
                
                # Login log
                log = Log(
                    user_id=user.id,
                    action_type='login',
                    timestamp=login_time,
                    ip_address=f"192.168.1.{random.randint(1, 254)}",
                    user_agent=random.choice([
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                    ])
                )
                db.session.add(log)
                logs.append(log)
                
                # Logout log (same day, later)
                logout_hour = min(22, hour + random.randint(1, 4))
                logout_time = base_date.replace(hour=logout_hour, minute=random.randint(0, 59), second=random.randint(0, 59))
                
                log = Log(
                    user_id=user.id,
                    action_type='logout',
                    timestamp=logout_time,
                    ip_address=f"192.168.1.{random.randint(1, 254)}"
                )
                db.session.add(log)
                logs.append(log)
    
    # Borrow/return logs
    for borrow in borrows:
        # Borrow log
        log = Log(
            user_id=borrow.user_id,
            item_id=borrow.item_id,
            locker_id=borrow.locker_id,
            borrow_id=borrow.id,
            action_type='borrow',
            timestamp=borrow.borrowed_at,
            action_details=f"Borrowed {Item.query.get(borrow.item_id).name}"
        )
        db.session.add(log)
        logs.append(log)
        
        # Return log if returned
        if borrow.status == 'returned':
            return_record = Return.query.filter_by(borrow_id=borrow.id).first()
            if return_record:
                log = Log(
                    user_id=return_record.user_id,
                    item_id=return_record.item_id,
                    locker_id=return_record.locker_id,
                    return_id=return_record.id,
                    action_type='return',
                    timestamp=return_record.returned_at,
                    action_details=f"Returned {Item.query.get(return_record.item_id).name}"
                )
                db.session.add(log)
                logs.append(log)
    
    # Payment logs
    for payment in payments:
        log = Log(
            user_id=payment.user_id,
            action_type='payment',
            timestamp=payment.processed_at,
            action_details=f"{payment.payment_type} of ${payment.amount} via {payment.payment_method}"
        )
        db.session.add(log)
        logs.append(log)
    
    # Commit all data
    db.session.commit()
    
    print(f"Comprehensive demo data created successfully!")
    print(f"- {len(users)} users (including admin)")
    print(f"- {len(lockers)} lockers")
    print(f"- {len(items)} items")
    print(f"- {len(borrows)} borrow records")
    print(f"- {len(returns)} return records")
    print(f"- {len(payments)} payment records")
    print(f"- {len(notifications)} notifications")
    print(f"- {len(logs)} system logs")
    print("\nDemo credentials:")
    print("Username: admin, Password: admin123 (Admin)")
    for user in users[1:4]:  # Show first 3 students
        print(f"Username: {user.username}, Password: password123 (Student)")

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