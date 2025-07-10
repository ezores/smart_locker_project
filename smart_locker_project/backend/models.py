from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore[import]
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
        department = db.Column(db.String(50))
        balance = db.Column(db.Float, default=0.0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        is_active = db.Column(db.Boolean, default=True)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)
            
        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

        def to_dict(self):
            return {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'role': self.role,
                'department': self.department,
                'balance': self.balance,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class Locker(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(32), unique=True, nullable=False)
        number = db.Column(db.String(10), unique=True, nullable=False)
        location = db.Column(db.String(100))
        description = db.Column(db.Text)
        capacity = db.Column(db.Integer, default=10)
        current_occupancy = db.Column(db.Integer, default=0)
        status = db.Column(db.String(20), default='active')  # active, maintenance, inactive
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        items = db.relationship('Item', backref='locker', lazy=True)

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'number': self.number,
                'location': self.location,
                'description': self.description,
                'status': self.status,
                'capacity': self.capacity,
                'current_occupancy': self.current_occupancy,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class Item(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        category = db.Column(db.String(50))  # electronics, books, tools, etc.
        condition = db.Column(db.String(20), default='good')  # excellent, good, fair, poor
        status = db.Column(db.String(20), default='available')  # available, borrowed, maintenance
        serial_number = db.Column(db.String(100), unique=True)
        purchase_date = db.Column(db.DateTime)
        warranty_expiry = db.Column(db.DateTime)
        locker_id = db.Column(db.Integer, db.ForeignKey('locker.id'))
        is_available = db.Column(db.Boolean, default=True)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'category': self.category,
                'condition': self.condition,
                'status': self.status,
                'locker_id': self.locker_id,
                'locker_name': self.locker.name if self.locker else None,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

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
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.Text)

        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'item_id': self.item_id,
                'locker_id': self.locker_id,
                'action_type': self.action_type,
                'notes': self.notes,
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'timestamp': self.timestamp.isoformat() if self.timestamp else None,
                'user_name': f"{self.user.first_name} {self.user.last_name}" if self.user else None,
                'item_name': self.item.name if self.item else None,
                'locker_name': self.locker.name if self.locker else None
            }

    class Borrow(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
        locker_id = db.Column(db.Integer, db.ForeignKey('locker.id'))
        borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
        due_date = db.Column(db.DateTime)
        returned_at = db.Column(db.DateTime)
        status = db.Column(db.String(20), default='borrowed')  # borrowed, returned, overdue
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'item_id': self.item_id,
                'locker_id': self.locker_id,
                'borrowed_at': self.borrowed_at.isoformat() if self.borrowed_at else None,
                'due_date': self.due_date.isoformat() if self.due_date else None,
                'returned_at': self.returned_at.isoformat() if self.returned_at else None,
                'status': self.status,
                'notes': self.notes,
                'user_name': f"{self.user.first_name} {self.user.last_name}" if self.user else None,
                'item_name': self.item.name if self.item else None,
                'locker_name': self.locker.name if self.locker else None,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    def generate_dummy_data():
        """Generate comprehensive dummy data for testing"""
        
        # Clear existing data
        db.session.query(Borrow).delete()
        db.session.query(Log).delete()
        db.session.query(Item).delete()
        db.session.query(Locker).delete()
        db.session.query(User).delete()
        
        # Create users - much more comprehensive
        users_data = [
            # Admins
            {'username': 'admin', 'password': 'admin123', 'role': 'admin', 'email': 'admin@ets.com', 'first_name': 'Admin', 'last_name': 'User'},
            {'username': 'manager', 'password': 'manager123', 'role': 'admin', 'email': 'manager@ets.com', 'first_name': 'Manager', 'last_name': 'User'},
            {'username': 'supervisor', 'password': 'supervisor123', 'role': 'admin', 'email': 'supervisor@ets.com', 'first_name': 'Supervisor', 'last_name': 'User'},
            
            # Students - Create 50 students
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
            {'username': 'student11', 'password': 'student123', 'role': 'student', 'email': 'student11@ets.com', 'first_name': 'James', 'last_name': 'Taylor', 'student_id': '2024011'},
            {'username': 'student12', 'password': 'student123', 'role': 'student', 'email': 'student12@ets.com', 'first_name': 'Maria', 'last_name': 'Anderson', 'student_id': '2024012'},
            {'username': 'student13', 'password': 'student123', 'role': 'student', 'email': 'student13@ets.com', 'first_name': 'Robert', 'last_name': 'Thomas', 'student_id': '2024013'},
            {'username': 'student14', 'password': 'student123', 'role': 'student', 'email': 'student14@ets.com', 'first_name': 'Jennifer', 'last_name': 'Jackson', 'student_id': '2024014'},
            {'username': 'student15', 'password': 'student123', 'role': 'student', 'email': 'student15@ets.com', 'first_name': 'William', 'last_name': 'White', 'student_id': '2024015'},
            {'username': 'student16', 'password': 'student123', 'role': 'student', 'email': 'student16@ets.com', 'first_name': 'Linda', 'last_name': 'Harris', 'student_id': '2024016'},
            {'username': 'student17', 'password': 'student123', 'role': 'student', 'email': 'student17@ets.com', 'first_name': 'Michael', 'last_name': 'Clark', 'student_id': '2024017'},
            {'username': 'student18', 'password': 'student123', 'role': 'student', 'email': 'student18@ets.com', 'first_name': 'Barbara', 'last_name': 'Lewis', 'student_id': '2024018'},
            {'username': 'student19', 'password': 'student123', 'role': 'student', 'email': 'student19@ets.com', 'first_name': 'Richard', 'last_name': 'Lee', 'student_id': '2024019'},
            {'username': 'student20', 'password': 'student123', 'role': 'student', 'email': 'student20@ets.com', 'first_name': 'Susan', 'last_name': 'Walker', 'student_id': '2024020'},
            {'username': 'student21', 'password': 'student123', 'role': 'student', 'email': 'student21@ets.com', 'first_name': 'Joseph', 'last_name': 'Hall', 'student_id': '2024021'},
            {'username': 'student22', 'password': 'student123', 'role': 'student', 'email': 'student22@ets.com', 'first_name': 'Jessica', 'last_name': 'Allen', 'student_id': '2024022'},
            {'username': 'student23', 'password': 'student123', 'role': 'student', 'email': 'student23@ets.com', 'first_name': 'Christopher', 'last_name': 'Young', 'student_id': '2024023'},
            {'username': 'student24', 'password': 'student123', 'role': 'student', 'email': 'student24@ets.com', 'first_name': 'Amanda', 'last_name': 'King', 'student_id': '2024024'},
            {'username': 'student25', 'password': 'student123', 'role': 'student', 'email': 'student25@ets.com', 'first_name': 'Daniel', 'last_name': 'Wright', 'student_id': '2024025'},
            {'username': 'student26', 'password': 'student123', 'role': 'student', 'email': 'student26@ets.com', 'first_name': 'Melissa', 'last_name': 'Lopez', 'student_id': '2024026'},
            {'username': 'student27', 'password': 'student123', 'role': 'student', 'email': 'student27@ets.com', 'first_name': 'Matthew', 'last_name': 'Hill', 'student_id': '2024027'},
            {'username': 'student28', 'password': 'student123', 'role': 'student', 'email': 'student28@ets.com', 'first_name': 'Nicole', 'last_name': 'Scott', 'student_id': '2024028'},
            {'username': 'student29', 'password': 'student123', 'role': 'student', 'email': 'student29@ets.com', 'first_name': 'Anthony', 'last_name': 'Green', 'student_id': '2024029'},
            {'username': 'student30', 'password': 'student123', 'role': 'student', 'email': 'student30@ets.com', 'first_name': 'Stephanie', 'last_name': 'Adams', 'student_id': '2024030'},
            {'username': 'student31', 'password': 'student123', 'role': 'student', 'email': 'student31@ets.com', 'first_name': 'Mark', 'last_name': 'Baker', 'student_id': '2024031'},
            {'username': 'student32', 'password': 'student123', 'role': 'student', 'email': 'student32@ets.com', 'first_name': 'Laura', 'last_name': 'Gonzalez', 'student_id': '2024032'},
            {'username': 'student33', 'password': 'student123', 'role': 'student', 'email': 'student33@ets.com', 'first_name': 'Donald', 'last_name': 'Nelson', 'student_id': '2024033'},
            {'username': 'student34', 'password': 'student123', 'role': 'student', 'email': 'student34@ets.com', 'first_name': 'Michelle', 'last_name': 'Carter', 'student_id': '2024034'},
            {'username': 'student35', 'password': 'student123', 'role': 'student', 'email': 'student35@ets.com', 'first_name': 'Steven', 'last_name': 'Mitchell', 'student_id': '2024035'},
            {'username': 'student36', 'password': 'student123', 'role': 'student', 'email': 'student36@ets.com', 'first_name': 'Kimberly', 'last_name': 'Perez', 'student_id': '2024036'},
            {'username': 'student37', 'password': 'student123', 'role': 'student', 'email': 'student37@ets.com', 'first_name': 'Paul', 'last_name': 'Roberts', 'student_id': '2024037'},
            {'username': 'student38', 'password': 'student123', 'role': 'student', 'email': 'student38@ets.com', 'first_name': 'Deborah', 'last_name': 'Turner', 'student_id': '2024038'},
            {'username': 'student39', 'password': 'student123', 'role': 'student', 'email': 'student39@ets.com', 'first_name': 'Andrew', 'last_name': 'Phillips', 'student_id': '2024039'},
            {'username': 'student40', 'password': 'student123', 'role': 'student', 'email': 'student40@ets.com', 'first_name': 'Dorothy', 'last_name': 'Campbell', 'student_id': '2024040'},
            {'username': 'student41', 'password': 'student123', 'role': 'student', 'email': 'student41@ets.com', 'first_name': 'Joshua', 'last_name': 'Parker', 'student_id': '2024041'},
            {'username': 'student42', 'password': 'student123', 'role': 'student', 'email': 'student42@ets.com', 'first_name': 'Helen', 'last_name': 'Evans', 'student_id': '2024042'},
            {'username': 'student43', 'password': 'student123', 'role': 'student', 'email': 'student43@ets.com', 'first_name': 'Kenneth', 'last_name': 'Edwards', 'student_id': '2024043'},
            {'username': 'student44', 'password': 'student123', 'role': 'student', 'email': 'student44@ets.com', 'first_name': 'Sandra', 'last_name': 'Collins', 'student_id': '2024044'},
            {'username': 'student45', 'password': 'student123', 'role': 'student', 'email': 'student45@ets.com', 'first_name': 'Kevin', 'last_name': 'Stewart', 'student_id': '2024045'},
            {'username': 'student46', 'password': 'student123', 'role': 'student', 'email': 'student46@ets.com', 'first_name': 'Donna', 'last_name': 'Sanchez', 'student_id': '2024046'},
            {'username': 'student47', 'password': 'student123', 'role': 'student', 'email': 'student47@ets.com', 'first_name': 'Brian', 'last_name': 'Morris', 'student_id': '2024047'},
            {'username': 'student48', 'password': 'student123', 'role': 'student', 'email': 'student48@ets.com', 'first_name': 'Carol', 'last_name': 'Rogers', 'student_id': '2024048'},
            {'username': 'student49', 'password': 'student123', 'role': 'student', 'email': 'student49@ets.com', 'first_name': 'George', 'last_name': 'Reed', 'student_id': '2024049'},
            {'username': 'student50', 'password': 'student123', 'role': 'student', 'email': 'student50@ets.com', 'first_name': 'Ruth', 'last_name': 'Cook', 'student_id': '2024050'},
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
        
        # Create lockers - ensure each has a unique 'number' field
        lockers = []
        for i in range(1, 41):
            locker = Locker(
                name=f'Locker {i}',
                number=f'L{i}',
                location=f'Building {((i-1)//10)+1} - Floor {((i-1)%10)+1}',
                description=f'Locker {i} description',
                capacity=10,
                current_occupancy=0,
                status='active',
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(locker)
            lockers.append(locker)
        db.session.commit()
        
        # Create items - much more comprehensive (100+ items)
        items_data = [
            # Electronics (30 items)
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
            {'name': 'MacBook Pro 14"', 'description': 'Apple MacBook Pro 14" M3', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'MBP002'},
            {'name': 'Dell Latitude', 'description': 'Dell Latitude Business Laptop', 'category': 'electronics', 'condition': 'good', 'serial_number': 'DLT001'},
            {'name': 'HP EliteBook', 'description': 'HP EliteBook 840', 'category': 'electronics', 'condition': 'good', 'serial_number': 'HEB001'},
            {'name': 'Lenovo ThinkPad', 'description': 'Lenovo ThinkPad X1 Carbon', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'LTC001'},
            {'name': 'iPad Mini', 'description': 'Apple iPad Mini 6', 'category': 'electronics', 'condition': 'good', 'serial_number': 'IPM001'},
            {'name': 'Surface Pro', 'description': 'Microsoft Surface Pro 9', 'category': 'electronics', 'condition': 'good', 'serial_number': 'MSP001'},
            {'name': 'iPhone 14', 'description': 'Apple iPhone 14', 'category': 'electronics', 'condition': 'good', 'serial_number': 'IPH002'},
            {'name': 'Google Pixel 8', 'description': 'Google Pixel 8 Pro', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'GPP001'},
            {'name': 'Nikon Z6', 'description': 'Nikon Z6 Mirrorless Camera', 'category': 'electronics', 'condition': 'good', 'serial_number': 'NZ6001'},
            {'name': 'Fujifilm X-T5', 'description': 'Fujifilm X-T5 Camera', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'FXT001'},
            {'name': 'GoPro Hero 11', 'description': 'GoPro Hero 11 Black', 'category': 'electronics', 'condition': 'good', 'serial_number': 'GPH001'},
            {'name': 'DJI Mini 3', 'description': 'DJI Mini 3 Pro Drone', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'DJM001'},
            {'name': 'AirPods Pro', 'description': 'Apple AirPods Pro 2', 'category': 'electronics', 'condition': 'good', 'serial_number': 'APP001'},
            {'name': 'Sony WH-1000XM5', 'description': 'Sony WH-1000XM5 Headphones', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'SWH001'},
            {'name': 'Bose QuietComfort', 'description': 'Bose QuietComfort 45', 'category': 'electronics', 'condition': 'good', 'serial_number': 'BQC001'},
            {'name': 'Apple Watch', 'description': 'Apple Watch Series 9', 'category': 'electronics', 'condition': 'excellent', 'serial_number': 'AW9001'},
            {'name': 'Samsung Galaxy Watch', 'description': 'Samsung Galaxy Watch 6', 'category': 'electronics', 'condition': 'good', 'serial_number': 'SGW001'},
            {'name': 'Kindle Paperwhite', 'description': 'Amazon Kindle Paperwhite', 'category': 'electronics', 'condition': 'good', 'serial_number': 'KPP001'},
            {'name': 'Roku Ultra', 'description': 'Roku Ultra Streaming Device', 'category': 'electronics', 'condition': 'good', 'serial_number': 'RKU001'},
            {'name': 'Chromecast', 'description': 'Google Chromecast 4K', 'category': 'electronics', 'condition': 'good', 'serial_number': 'GCC001'},
            {'name': 'Fire TV Stick', 'description': 'Amazon Fire TV Stick 4K', 'category': 'electronics', 'condition': 'good', 'serial_number': 'AFS001'},
            
            # Books (25 items)
            {'name': 'Python Programming', 'description': 'Python Programming for Beginners', 'category': 'books', 'condition': 'good', 'serial_number': 'BPY001'},
            {'name': 'Data Science Handbook', 'description': 'Complete Data Science Guide', 'category': 'books', 'condition': 'good', 'serial_number': 'BDS001'},
            {'name': 'Machine Learning', 'description': 'Introduction to Machine Learning', 'category': 'books', 'condition': 'fair', 'serial_number': 'BML001'},
            {'name': 'Web Development', 'description': 'Modern Web Development', 'category': 'books', 'condition': 'good', 'serial_number': 'BWD001'},
            {'name': 'Database Design', 'description': 'Database Design Principles', 'category': 'books', 'condition': 'excellent', 'serial_number': 'BDD001'},
            {'name': 'JavaScript Guide', 'description': 'JavaScript: The Definitive Guide', 'category': 'books', 'condition': 'good', 'serial_number': 'BJS001'},
            {'name': 'React Development', 'description': 'Learning React', 'category': 'books', 'condition': 'good', 'serial_number': 'BRD001'},
            {'name': 'Node.js Guide', 'description': 'Node.js Design Patterns', 'category': 'books', 'condition': 'fair', 'serial_number': 'BND001'},
            {'name': 'Docker Handbook', 'description': 'Docker in Practice', 'category': 'books', 'condition': 'good', 'serial_number': 'BDH001'},
            {'name': 'Kubernetes Guide', 'description': 'Kubernetes: Up and Running', 'category': 'books', 'condition': 'excellent', 'serial_number': 'BKG001'},
            {'name': 'AWS Solutions', 'description': 'AWS Solutions Architect', 'category': 'books', 'condition': 'good', 'serial_number': 'BAS001'},
            {'name': 'Azure Fundamentals', 'description': 'Microsoft Azure Fundamentals', 'category': 'books', 'condition': 'good', 'serial_number': 'BAF001'},
            {'name': 'Google Cloud', 'description': 'Google Cloud Platform', 'category': 'books', 'condition': 'fair', 'serial_number': 'BGC001'},
            {'name': 'DevOps Handbook', 'description': 'The DevOps Handbook', 'category': 'books', 'condition': 'excellent', 'serial_number': 'BDH002'},
            {'name': 'Clean Code', 'description': 'Clean Code: A Handbook', 'category': 'books', 'condition': 'good', 'serial_number': 'BCC001'},
            {'name': 'Design Patterns', 'description': 'Design Patterns: Elements', 'category': 'books', 'condition': 'good', 'serial_number': 'BDP001'},
            {'name': 'Refactoring', 'description': 'Refactoring: Improving Design', 'category': 'books', 'condition': 'fair', 'serial_number': 'BRF001'},
            {'name': 'Test Driven Development', 'description': 'Test-Driven Development', 'category': 'books', 'condition': 'good', 'serial_number': 'BTD001'},
            {'name': 'Agile Development', 'description': 'Agile Software Development', 'category': 'books', 'condition': 'good', 'serial_number': 'BAD001'},
            {'name': 'Scrum Guide', 'description': 'The Scrum Guide', 'category': 'books', 'condition': 'excellent', 'serial_number': 'BSG001'},
            {'name': 'Git Version Control', 'description': 'Pro Git', 'category': 'books', 'condition': 'good', 'serial_number': 'BGV001'},
            {'name': 'Linux Administration', 'description': 'Linux System Administration', 'category': 'books', 'condition': 'good', 'serial_number': 'BLA001'},
            {'name': 'Network Security', 'description': 'Network Security Essentials', 'category': 'books', 'condition': 'fair', 'serial_number': 'BNS001'},
            {'name': 'Cryptography', 'description': 'Applied Cryptography', 'category': 'books', 'condition': 'excellent', 'serial_number': 'BCR001'},
            {'name': 'Computer Networks', 'description': 'Computer Networks', 'category': 'books', 'condition': 'good', 'serial_number': 'BCN001'},
            
            # Tools (25 items)
            {'name': 'Arduino Kit', 'description': 'Arduino Starter Kit with Components', 'category': 'tools', 'condition': 'good', 'serial_number': 'TAR001'},
            {'name': 'Raspberry Pi 4', 'description': 'Raspberry Pi 4 Model B', 'category': 'tools', 'condition': 'excellent', 'serial_number': 'TRP001'},
            {'name': 'Soldering Iron', 'description': 'Professional Soldering Iron', 'category': 'tools', 'condition': 'good', 'serial_number': 'TSI001'},
            {'name': 'Multimeter', 'description': 'Digital Multimeter', 'category': 'tools', 'condition': 'good', 'serial_number': 'TMM001'},
            {'name': 'Oscilloscope', 'description': 'Digital Oscilloscope', 'category': 'tools', 'condition': 'excellent', 'serial_number': 'TOS001'},
            {'name': '3D Printer', 'description': 'Creality Ender 3 Pro', 'category': 'tools', 'condition': 'good', 'serial_number': 'T3P001'},
            {'name': 'Laser Cutter', 'description': 'CO2 Laser Cutter', 'category': 'tools', 'condition': 'excellent', 'serial_number': 'TLC001'},
            {'name': 'CNC Machine', 'description': 'Desktop CNC Router', 'category': 'tools', 'condition': 'good', 'serial_number': 'TCM001'},
            {'name': 'Drill Press', 'description': 'Bench Drill Press', 'category': 'tools', 'condition': 'good', 'serial_number': 'TDP001'},
            {'name': 'Band Saw', 'description': 'Table Band Saw', 'category': 'tools', 'condition': 'fair', 'serial_number': 'TBS001'},
            {'name': 'Circular Saw', 'description': 'Portable Circular Saw', 'category': 'tools', 'condition': 'good', 'serial_number': 'TCS001'},
            {'name': 'Jigsaw', 'description': 'Electric Jigsaw', 'category': 'tools', 'condition': 'good', 'serial_number': 'TJS001'},
            {'name': 'Router', 'description': 'Wood Router', 'category': 'tools', 'condition': 'excellent', 'serial_number': 'TWR001'},
            {'name': 'Sander', 'description': 'Orbital Sander', 'category': 'tools', 'condition': 'good', 'serial_number': 'TOS002'},
            {'name': 'Air Compressor', 'description': 'Portable Air Compressor', 'category': 'tools', 'condition': 'good', 'serial_number': 'TAC001'},
            {'name': 'Welding Machine', 'description': 'MIG Welding Machine', 'category': 'tools', 'condition': 'excellent', 'serial_number': 'TWM001'},
            {'name': 'Plasma Cutter', 'description': 'Plasma Cutting Machine', 'category': 'tools', 'condition': 'good', 'serial_number': 'TPC001'},
            {'name': 'Heat Gun', 'description': 'Industrial Heat Gun', 'category': 'tools', 'condition': 'good', 'serial_number': 'THG001'},
            {'name': 'Hot Air Station', 'description': 'SMD Hot Air Station', 'category': 'tools', 'condition': 'excellent', 'serial_number': 'THS001'},
            {'name': 'Logic Analyzer', 'description': 'USB Logic Analyzer', 'category': 'tools', 'condition': 'good', 'serial_number': 'TLA001'},
            {'name': 'Function Generator', 'description': 'Signal Function Generator', 'category': 'tools', 'condition': 'good', 'serial_number': 'TFG001'},
            {'name': 'Power Supply', 'description': 'Variable Power Supply', 'category': 'tools', 'condition': 'excellent', 'serial_number': 'TPS001'},
            {'name': 'Microscope', 'description': 'Digital Microscope', 'category': 'tools', 'condition': 'good', 'serial_number': 'TDM001'},
            {'name': 'Calipers', 'description': 'Digital Calipers', 'category': 'tools', 'condition': 'good', 'serial_number': 'TDC001'},
            {'name': 'Micrometer', 'description': 'Digital Micrometer', 'category': 'tools', 'condition': 'excellent', 'serial_number': 'TDM002'},
            
            # Audio/Video (20 items)
            {'name': 'Microphone Set', 'description': 'Professional USB Microphone', 'category': 'audio', 'condition': 'good', 'serial_number': 'AMS001'},
            {'name': 'Video Camera', 'description': '4K Video Camera', 'category': 'audio', 'condition': 'excellent', 'serial_number': 'AVC001'},
            {'name': 'Audio Interface', 'description': 'USB Audio Interface', 'category': 'audio', 'condition': 'good', 'serial_number': 'AAI001'},
            {'name': 'Studio Lights', 'description': 'LED Studio Lighting Kit', 'category': 'audio', 'condition': 'good', 'serial_number': 'ASL001'},
            {'name': 'Green Screen', 'description': 'Professional Green Screen', 'category': 'audio', 'condition': 'fair', 'serial_number': 'AGS001'},
            {'name': 'Tripod', 'description': 'Professional Camera Tripod', 'category': 'audio', 'condition': 'good', 'serial_number': 'ATP001'},
            {'name': 'Gimbal', 'description': '3-Axis Camera Gimbal', 'category': 'audio', 'condition': 'excellent', 'serial_number': 'AGM001'},
            {'name': 'Wireless Mic', 'description': 'Wireless Lavalier Microphone', 'category': 'audio', 'condition': 'good', 'serial_number': 'AWM001'},
            {'name': 'Mixer', 'description': 'Audio Mixer Console', 'category': 'audio', 'condition': 'good', 'serial_number': 'AMX001'},
            {'name': 'Speakers', 'description': 'Studio Monitor Speakers', 'category': 'audio', 'condition': 'excellent', 'serial_number': 'ASP001'},
            {'name': 'Headphones', 'description': 'Studio Headphones', 'category': 'audio', 'condition': 'good', 'serial_number': 'AHD001'},
            {'name': 'MIDI Controller', 'description': 'USB MIDI Controller', 'category': 'audio', 'condition': 'good', 'serial_number': 'AMC001'},
            {'name': 'Synthesizer', 'description': 'Digital Synthesizer', 'category': 'audio', 'condition': 'excellent', 'serial_number': 'ASY001'},
            {'name': 'Drum Machine', 'description': 'Electronic Drum Machine', 'category': 'audio', 'condition': 'good', 'serial_number': 'ADM001'},
            {'name': 'Guitar Amp', 'description': 'Electric Guitar Amplifier', 'category': 'audio', 'condition': 'fair', 'serial_number': 'AGA001'},
            {'name': 'Bass Amp', 'description': 'Bass Guitar Amplifier', 'category': 'audio', 'condition': 'good', 'serial_number': 'ABA001'},
            {'name': 'Effects Pedal', 'description': 'Guitar Effects Pedal', 'category': 'audio', 'condition': 'good', 'serial_number': 'AEP001'},
            {'name': 'Cables', 'description': 'Professional Audio Cables', 'category': 'audio', 'condition': 'good', 'serial_number': 'ACB001'},
            {'name': 'Stand', 'description': 'Microphone Stand', 'category': 'audio', 'condition': 'good', 'serial_number': 'AMS002'},
            {'name': 'Pop Filter', 'description': 'Microphone Pop Filter', 'category': 'audio', 'condition': 'fair', 'serial_number': 'APF001'},
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
        
        # Create logs and borrows - much more comprehensive
        action_types = ['borrow', 'return', 'maintenance', 'check_in', 'check_out']
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
                notes=f"Log entry {i+1} for {action} action"
            )
            db.session.add(log)
            
            # Create borrow entries (for active borrows) - more active borrows
            if action == 'borrow' and random.random() < 0.4:  # 40% chance of active borrow
                borrow = Borrow(
                    user_id=user.id,
                    item_id=item.id,
                    borrowed_at=datetime.now() - timedelta(days=random.randint(1, 14)),
                    due_date=datetime.now() + timedelta(days=random.randint(1, 21)),
                    status='borrowed',
                    notes=f"Active borrow for {item.name}"
                )
                db.session.add(borrow)
                
                # Mark item as unavailable
                item.is_available = False
        
        db.session.commit()
        print(f"Created {len(users)} users, {len(lockers)} lockers, {len(items)} items, and 500 log entries with active borrows")

    def init_db():
        db.create_all()
        if not User.query.first():
            generate_dummy_data()
    
    return User, Locker, Item, Log, Borrow, init_db, generate_dummy_data 