from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash  # type: ignore[import]
import random
import string

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
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        is_active = db.Column(db.Boolean, default=True)

    class Locker(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(32), unique=True, nullable=False)
        location = db.Column(db.String(100))
        capacity = db.Column(db.Integer, default=10)
        status = db.Column(db.String(20), default='active')  # active, maintenance, inactive
        items = db.relationship('Item', backref='locker', lazy=True)

    class Item(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        category = db.Column(db.String(50))  # electronics, books, tools, etc.
        condition = db.Column(db.String(20), default='good')  # excellent, good, fair, poor
        serial_number = db.Column(db.String(100), unique=True)
        purchase_date = db.Column(db.DateTime)
        warranty_expiry = db.Column(db.DateTime)
        locker_id = db.Column(db.Integer, db.ForeignKey('locker.id'))
        is_available = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class Log(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
        locker_id = db.Column(db.Integer, db.ForeignKey('locker.id'))
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        action_type = db.Column(db.String(32), nullable=False)  # borrow, return, maintenance
        notes = db.Column(db.Text)
        due_date = db.Column(db.DateTime)
        returned_at = db.Column(db.DateTime)

    class Borrow(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
        borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
        due_date = db.Column(db.DateTime)
        returned_at = db.Column(db.DateTime)
        status = db.Column(db.String(20), default='borrowed')  # borrowed, returned, overdue
        notes = db.Column(db.Text)

    def generate_dummy_data():
        """Generate comprehensive dummy data for testing"""
        
        # Clear existing data
        db.session.query(Borrow).delete()
        db.session.query(Log).delete()
        db.session.query(Item).delete()
        db.session.query(Locker).delete()
        db.session.query(User).delete()
        
        # Create users
        users_data = [
            # Admins
            {'username': 'admin', 'password': 'admin123', 'role': 'admin', 'email': 'admin@ets.com', 'first_name': 'Admin', 'last_name': 'User'},
            {'username': 'manager', 'password': 'manager123', 'role': 'admin', 'email': 'manager@ets.com', 'first_name': 'Manager', 'last_name': 'User'},
            
            # Students
            {'username': 'student1', 'password': 'student123', 'role': 'student', 'email': 'student1@ets.com', 'first_name': 'John', 'last_name': 'Doe', 'student_id': '2024001'},
            {'username': 'student2', 'password': 'student123', 'role': 'student', 'email': 'student2@ets.com', 'first_name': 'Jane', 'last_name': 'Smith', 'student_id': '2024002'},
            {'username': 'student3', 'password': 'student123', 'role': 'student', 'email': 'student3@ets.com', 'first_name': 'Mike', 'last_name': 'Johnson', 'student_id': '2024003'},
            {'username': 'student4', 'password': 'student123', 'role': 'student', 'email': 'student4@ets.com', 'first_name': 'Sarah', 'last_name': 'Wilson', 'student_id': '2024004'},
            {'username': 'student5', 'password': 'student123', 'role': 'student', 'email': 'student5@ets.com', 'first_name': 'David', 'last_name': 'Brown', 'student_id': '2024005'},
            {'username': 'student6', 'password': 'student123', 'role': 'student', 'email': 'student6@ets.com', 'first_name': 'Emily', 'last_name': 'Davis', 'student_id': '2024006'},
            {'username': 'student7', 'password': 'student123', 'role': 'student', 'email': 'student7@ets.com', 'first_name': 'Alex', 'last_name': 'Miller', 'student_id': '2024007'},
            {'username': 'student8', 'password': 'student123', 'role': 'student', 'email': 'student8@ets.com', 'first_name': 'Lisa', 'last_name': 'Garcia', 'student_id': '2024008'},
            {'username': 'student9', 'password': 'student123', 'role': 'student', 'email': 'student9@ets.com', 'first_name': 'Tom', 'last_name': 'Martinez', 'student_id': '2024009'},
            {'username': 'student10', 'password': 'student123', 'role': 'student', 'email': 'student10@ets.com', 'first_name': 'Anna', 'last_name': 'Rodriguez', 'student_id': '2024010'},
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                username=user_data['username'],
                password_hash=generate_password_hash(user_data['password']),
                role=user_data['role'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                rfid_tag=f"RFID_{user_data['username'].upper()}",
                qr_code=f"QR_{user_data['username'].upper()}",
                student_id=user_data.get('student_id')
            )
            users.append(user)
            db.session.add(user)
        
        # Create lockers
        lockers_data = [
            {'name': 'Locker A1', 'location': 'Building A - Ground Floor', 'capacity': 15},
            {'name': 'Locker A2', 'location': 'Building A - Ground Floor', 'capacity': 12},
            {'name': 'Locker B1', 'location': 'Building B - First Floor', 'capacity': 10},
            {'name': 'Locker B2', 'location': 'Building B - First Floor', 'capacity': 8},
            {'name': 'Locker C1', 'location': 'Building C - Second Floor', 'capacity': 20},
            {'name': 'Locker C2', 'location': 'Building C - Second Floor', 'capacity': 18},
            {'name': 'Locker D1', 'location': 'Library - Main Hall', 'capacity': 25},
            {'name': 'Locker D2', 'location': 'Library - Main Hall', 'capacity': 22},
        ]
        
        lockers = []
        for locker_data in lockers_data:
            locker = Locker(**locker_data)
            lockers.append(locker)
            db.session.add(locker)
        
        # Create items
        items_data = [
            # Electronics
            {'name': 'MacBook Pro 16"', 'description': 'Apple MacBook Pro with M2 chip', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'MBP001'},
            {'name': 'MacBook Air 13"', 'description': 'Apple MacBook Air M1', 'category': 'electronics', 'condition': 'good', 'serial_number': 'MBA001'},
            {'name': 'Dell XPS 15', 'description': 'Dell XPS 15 Laptop', 'category': 'electronics', 'condition': 'good', 'serial_number': 'DXP001'},
            {'name': 'iPad Pro 12.9"', 'description': 'Apple iPad Pro with Apple Pencil', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'IPP001'},
            {'name': 'iPad Air', 'description': 'Apple iPad Air', 'category': 'electronics', 'condition': 'good', 'serial_number': 'IPA001'},
            {'name': 'Samsung Galaxy Tab', 'description': 'Samsung Galaxy Tab S8', 'category': 'electronics', 'condition': 'good', 'serial_number': 'SGT001'},
            {'name': 'iPhone 15 Pro', 'description': 'Apple iPhone 15 Pro', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'IPH001'},
            {'name': 'Samsung Galaxy S24', 'description': 'Samsung Galaxy S24 Ultra', 'category': 'electronics', 'condition': 'good', 'serial_number': 'SGS001'},
            {'name': 'Canon EOS R5', 'description': 'Canon EOS R5 Camera', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'CER001'},
            {'name': 'Sony A7 IV', 'description': 'Sony A7 IV Mirrorless Camera', 'category': 'electronics', 'condition': 'good', 'serial_number': 'SAV001'},
            
            # Books
            {'name': 'Python Programming', 'description': 'Python Programming for Beginners', 'category': 'books', 'condition': 'good', 'serial_number': 'BPY001'},
            {'name': 'Data Science Handbook', 'description': 'Complete Data Science Guide', 'category': 'books', 'condition': 'good', 'serial_number': 'BDS001'},
            {'name': 'Machine Learning', 'description': 'Introduction to Machine Learning', 'category': 'books', 'condition': 'fair', 'serial_number': 'BML001'},
            {'name': 'Web Development', 'description': 'Modern Web Development', 'category': 'books', 'condition': 'good', 'serial_number': 'BWD001'},
            {'name': 'Database Design', 'description': 'Database Design Principles', 'category': 'books', 'condition': 'excellent', 'serial_number': 'BDD001'},
            
            # Tools
            {'name': 'Arduino Kit', 'description': 'Arduino Starter Kit with Components', 'category': 'tools', 'condition': 'good', 'serial_number': 'TAR001'},
            {'name': 'Raspberry Pi 4', 'description': 'Raspberry Pi 4 Model B', 'category': 'tools', 'condition': 'excellent', 'serial_number': 'TRP001'},
            {'name': 'Soldering Iron', 'description': 'Professional Soldering Iron', 'category': 'tools', 'condition': 'good', 'serial_number': 'TSI001'},
            {'name': 'Multimeter', 'description': 'Digital Multimeter', 'category': 'tools', 'condition': 'good', 'serial_number': 'TMM001'},
            {'name': 'Oscilloscope', 'description': 'Digital Oscilloscope', 'category': 'tools', 'condition': 'excellent', 'serial_number': 'TOS001'},
            
            # Audio/Video
            {'name': 'Microphone Set', 'description': 'Professional USB Microphone', 'category': 'audio', 'condition': 'good', 'serial_number': 'AMS001'},
            {'name': 'Video Camera', 'description': '4K Video Camera', 'category': 'audio', 'condition': 'excellent', 'serial_number': 'AVC001'},
            {'name': 'Audio Interface', 'description': 'USB Audio Interface', 'category': 'audio', 'condition': 'good', 'serial_number': 'AAI001'},
            {'name': 'Studio Lights', 'description': 'LED Studio Lighting Kit', 'category': 'audio', 'condition': 'good', 'serial_number': 'ASL001'},
            {'name': 'Green Screen', 'description': 'Professional Green Screen', 'category': 'audio', 'condition': 'fair', 'serial_number': 'AGS001'},
        ]
        
        items = []
        for i, item_data in enumerate(items_data):
            item = Item(
                **item_data,
                locker_id=lockers[i % len(lockers)].id,
                purchase_date=datetime.now() - timedelta(days=random.randint(30, 365)),
                warranty_expiry=datetime.now() + timedelta(days=random.randint(100, 1000))
            )
            items.append(item)
            db.session.add(item)
        
        # Create logs and borrows
        action_types = ['borrow', 'return', 'maintenance']
        for i in range(100):  # Create 100 log entries
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
                timestamp=datetime.now() - timedelta(days=random.randint(1, 30)),
                notes=f"Log entry {i+1} for {action} action"
            )
            db.session.add(log)
            
            # Create borrow entries (for active borrows)
            if action == 'borrow' and random.random() < 0.3:  # 30% chance of active borrow
                borrow = Borrow(
                    user_id=user.id,
                    item_id=item.id,
                    borrowed_at=datetime.now() - timedelta(days=random.randint(1, 7)),
                    due_date=datetime.now() + timedelta(days=random.randint(1, 14)),
                    status='borrowed',
                    notes=f"Active borrow for {item.name}"
                )
                db.session.add(borrow)
                
                # Mark item as unavailable
                item.is_available = False
        
        db.session.commit()
        print(f"Created {len(users)} users, {len(lockers)} lockers, {len(items)} items, and 100 log entries")

    def init_db():
        db.create_all()
        if not User.query.first():
            generate_dummy_data()
    
    return User, Locker, Item, Log, Borrow, init_db 