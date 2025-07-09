from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index, CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property

def init_models(db):
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=False)
        email = db.Column(db.String(120), unique=True)
        first_name = db.Column(db.String(50))
        last_name = db.Column(db.String(50))
        rfid_tag = db.Column(db.String(64), unique=True, index=True)
        qr_code = db.Column(db.String(128), unique=True)
        role = db.Column(db.String(16), nullable=False, default='student')  # student, admin
        is_active = db.Column(db.Boolean, default=True)
        balance = db.Column(db.Numeric(10, 2), default=0.00)
        phone = db.Column(db.String(20))
        department = db.Column(db.String(100))
        student_id = db.Column(db.String(20), unique=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        last_login = db.Column(db.DateTime)
        
        # Relationships
        borrows = db.relationship('Borrow', backref='user', lazy='dynamic')
        returns = db.relationship('Return', backref='user', lazy='dynamic')
        logs = db.relationship('Log', backref='user', lazy='dynamic')
        payments = db.relationship('Payment', backref='user', lazy='dynamic')
        notifications = db.relationship('Notification', backref='user', lazy='dynamic')
        
        # Indexes
        __table_args__ = (
            Index('idx_user_role', 'role'),
            Index('idx_user_active', 'is_active'),
            CheckConstraint('balance >= 0', name='check_balance_positive'),
        )
        
        def set_password(self, password):
            self.password_hash = generate_password_hash(password)
            
        def check_password(self, password):
            return check_password_hash(self.password_hash, password)
            
        @hybrid_property
        def full_name(self):
            return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.username
            
        @hybrid_property
        def active_borrows_count(self):
            return self.borrows.filter_by(returned_at=None).count()
            
        def to_dict(self):
            return {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'role': self.role,
                'is_active': self.is_active,
                'balance': float(self.balance),
                'department': self.department,
                'student_id': self.student_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'last_login': self.last_login.isoformat() if self.last_login else None,
                'active_borrows_count': self.active_borrows_count
            }

    class Locker(db.Model):
        __tablename__ = 'lockers'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(32), unique=True, nullable=False, index=True)
        number = db.Column(db.String(10), unique=True, nullable=False, index=True)
        location = db.Column(db.String(200))
        description = db.Column(db.Text)
        status = db.Column(db.String(20), default='available')  # available, occupied, maintenance, out_of_service
        capacity = db.Column(db.Integer, default=1)
        current_occupancy = db.Column(db.Integer, default=0)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        items = db.relationship('Item', backref='locker', lazy='dynamic')
        borrows = db.relationship('Borrow', backref='locker', lazy='dynamic')
        returns = db.relationship('Return', backref='locker', lazy='dynamic')
        logs = db.relationship('Log', backref='locker', lazy='dynamic')
        
        # Indexes
        __table_args__ = (
            Index('idx_locker_status', 'status'),
            Index('idx_locker_active', 'is_active'),
            CheckConstraint('current_occupancy <= capacity', name='check_occupancy_capacity'),
            CheckConstraint('current_occupancy >= 0', name='check_occupancy_positive'),
        )
        
        @hybrid_property
        def is_available(self):
            return self.status == 'available' and self.current_occupancy < self.capacity
            
        @hybrid_property
        def available_space(self):
            return max(0, self.capacity - self.current_occupancy)
            
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
                'is_available': self.is_available,
                'available_space': self.available_space,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class Item(db.Model):
        __tablename__ = 'items'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False, index=True)
        description = db.Column(db.Text)
        category = db.Column(db.String(50), index=True)
        brand = db.Column(db.String(50))
        model = db.Column(db.String(50))
        serial_number = db.Column(db.String(100), unique=True)
        barcode = db.Column(db.String(100), unique=True)
        qr_code = db.Column(db.String(100), unique=True)
        condition = db.Column(db.String(20), default='good')  # new, good, fair, poor, damaged
        status = db.Column(db.String(20), default='available')  # available, borrowed, maintenance, lost, retired
        value = db.Column(db.Numeric(10, 2))
        purchase_date = db.Column(db.Date)
        warranty_expiry = db.Column(db.Date)
        locker_id = db.Column(db.Integer, db.ForeignKey('lockers.id'), nullable=False)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        borrows = db.relationship('Borrow', backref='item', lazy='dynamic')
        returns = db.relationship('Return', backref='item', lazy='dynamic')
        logs = db.relationship('Log', backref='item', lazy='dynamic')
        
        # Indexes
        __table_args__ = (
            Index('idx_item_category', 'category'),
            Index('idx_item_status', 'status'),
            Index('idx_item_condition', 'condition'),
            Index('idx_item_active', 'is_active'),
        )
        
        @hybrid_property
        def is_available(self):
            return self.status == 'available' and self.is_active
            
        @hybrid_property
        def current_borrow(self):
            return self.borrows.filter_by(returned_at=None).first()
            
        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'category': self.category,
                'brand': self.brand,
                'model': self.model,
                'serial_number': self.serial_number,
                'condition': self.condition,
                'status': self.status,
                'value': float(self.value) if self.value else None,
                'locker_id': self.locker_id,
                'is_active': self.is_active,
                'is_available': self.is_available,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class Borrow(db.Model):
        __tablename__ = 'borrows'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
        item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, index=True)
        locker_id = db.Column(db.Integer, db.ForeignKey('lockers.id'), nullable=False, index=True)
        borrowed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        due_date = db.Column(db.DateTime, nullable=False)
        returned_at = db.Column(db.DateTime)
        notes = db.Column(db.Text)
        status = db.Column(db.String(20), default='active')  # active, returned, overdue, lost
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        returns = db.relationship('Return', backref='borrow', lazy='dynamic')
        
        # Indexes
        __table_args__ = (
            Index('idx_borrow_status', 'status'),
            Index('idx_borrow_due_date', 'due_date'),
            Index('idx_borrow_returned', 'returned_at'),
        )
        
        @hybrid_property
        def is_overdue(self):
            if self.returned_at:
                return False
            return datetime.utcnow() > self.due_date
            
        @hybrid_property
        def duration_days(self):
            if self.returned_at:
                return (self.returned_at - self.borrowed_at).days
            return (datetime.utcnow() - self.borrowed_at).days
            
        @hybrid_property
        def days_until_due(self):
            if self.returned_at:
                return None
            delta = self.due_date - datetime.utcnow()
            return delta.days if delta.days > 0 else 0
            
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'item_id': self.item_id,
                'locker_id': self.locker_id,
                'borrowed_at': self.borrowed_at.isoformat() if self.borrowed_at else None,
                'due_date': self.due_date.isoformat() if self.due_date else None,
                'returned_at': self.returned_at.isoformat() if self.returned_at else None,
                'notes': self.notes,
                'status': self.status,
                'is_overdue': self.is_overdue,
                'duration_days': self.duration_days,
                'days_until_due': self.days_until_due,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class Return(db.Model):
        __tablename__ = 'returns'
        
        id = db.Column(db.Integer, primary_key=True)
        borrow_id = db.Column(db.Integer, db.ForeignKey('borrows.id'), nullable=False, index=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
        item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, index=True)
        locker_id = db.Column(db.Integer, db.ForeignKey('lockers.id'), nullable=False, index=True)
        returned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        condition_returned = db.Column(db.String(20))  # same, damaged, missing_parts
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # Indexes
        __table_args__ = (
            Index('idx_return_date', 'returned_at'),
        )
        
        def to_dict(self):
            return {
                'id': self.id,
                'borrow_id': self.borrow_id,
                'user_id': self.user_id,
                'item_id': self.item_id,
                'locker_id': self.locker_id,
                'returned_at': self.returned_at.isoformat() if self.returned_at else None,
                'condition_returned': self.condition_returned,
                'notes': self.notes,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class Log(db.Model):
        __tablename__ = 'logs'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
        item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
        locker_id = db.Column(db.Integer, db.ForeignKey('lockers.id'))
        borrow_id = db.Column(db.Integer, db.ForeignKey('borrows.id'))
        return_id = db.Column(db.Integer, db.ForeignKey('returns.id'))
        action_type = db.Column(db.String(32), nullable=False, index=True)  # login, logout, borrow, return, payment, etc.
        action_details = db.Column(db.Text)
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.String(500))
        timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
        
        # Indexes
        __table_args__ = (
            Index('idx_log_action_type', 'action_type'),
            Index('idx_log_timestamp', 'timestamp'),
        )
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'item_id': self.item_id,
                'locker_id': self.locker_id,
                'borrow_id': self.borrow_id,
                'return_id': self.return_id,
                'action_type': self.action_type,
                'action_details': self.action_details,
                'ip_address': self.ip_address,
                'timestamp': self.timestamp.isoformat() if self.timestamp else None
            }

    class Payment(db.Model):
        __tablename__ = 'payments'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
        amount = db.Column(db.Numeric(10, 2), nullable=False)
        payment_type = db.Column(db.String(20), default='deposit')  # deposit, withdrawal, fee, refund
        payment_method = db.Column(db.String(20), default='cash')  # cash, card, online, transfer
        description = db.Column(db.Text)
        reference_number = db.Column(db.String(100), unique=True)
        status = db.Column(db.String(20), default='completed')  # pending, completed, failed, cancelled
        processed_at = db.Column(db.DateTime, default=datetime.utcnow)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # Indexes
        __table_args__ = (
            Index('idx_payment_type', 'payment_type'),
            Index('idx_payment_status', 'status'),
            Index('idx_payment_date', 'processed_at'),
            CheckConstraint('amount > 0', name='check_payment_amount_positive'),
        )
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'amount': float(self.amount),
                'payment_type': self.payment_type,
                'payment_method': self.payment_method,
                'description': self.description,
                'reference_number': self.reference_number,
                'status': self.status,
                'processed_at': self.processed_at.isoformat() if self.processed_at else None,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class Notification(db.Model):
        __tablename__ = 'notifications'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
        title = db.Column(db.String(200), nullable=False)
        message = db.Column(db.Text, nullable=False)
        notification_type = db.Column(db.String(20), default='info')  # info, warning, error, success
        is_read = db.Column(db.Boolean, default=False)
        read_at = db.Column(db.DateTime)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # Indexes
        __table_args__ = (
            Index('idx_notification_type', 'notification_type'),
            Index('idx_notification_read', 'is_read'),
            Index('idx_notification_created', 'created_at'),
        )
        
        def mark_as_read(self):
            self.is_read = True
            self.read_at = datetime.utcnow()
            
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'title': self.title,
                'message': self.message,
                'notification_type': self.notification_type,
                'is_read': self.is_read,
                'read_at': self.read_at.isoformat() if self.read_at else None,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class SystemSetting(db.Model):
        __tablename__ = 'system_settings'
        
        id = db.Column(db.Integer, primary_key=True)
        key = db.Column(db.String(100), unique=True, nullable=False, index=True)
        value = db.Column(db.Text)
        description = db.Column(db.Text)
        category = db.Column(db.String(50), default='general')
        is_public = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Indexes
        __table_args__ = (
            Index('idx_setting_category', 'category'),
            Index('idx_setting_public', 'is_public'),
        )
        
        def to_dict(self):
            return {
                'id': self.id,
                'key': self.key,
                'value': self.value,
                'description': self.description,
                'category': self.category,
                'is_public': self.is_public,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }

    class UserSession(db.Model):
        __tablename__ = 'user_sessions'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
        session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.String(500))
        is_active = db.Column(db.Boolean, default=True)
        expires_at = db.Column(db.DateTime, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        last_activity = db.Column(db.DateTime, default=datetime.utcnow)
        
        # Indexes
        __table_args__ = (
            Index('idx_session_active', 'is_active'),
            Index('idx_session_expires', 'expires_at'),
        )
        
        @hybrid_property
        def is_expired(self):
            return datetime.utcnow() > self.expires_at
            
        def refresh(self):
            self.last_activity = datetime.utcnow()
            
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'session_token': self.session_token,
                'ip_address': self.ip_address,
                'is_active': self.is_active,
                'expires_at': self.expires_at.isoformat() if self.expires_at else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'last_activity': self.last_activity.isoformat() if self.last_activity else None,
                'is_expired': self.is_expired
            }

    def init_db():
        db.create_all()
        
        # Create default admin and student users if they don't exist
        if not User.query.first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                balance=0.00
            )
            
            student = User(
                username='student',
                password_hash=generate_password_hash('password123'),
                email='student@example.com',
                first_name='Student',
                last_name='User',
                role='student',
                balance=0.00
            )
            
            db.session.add(admin)
            db.session.add(student)
            
            # Create default lockers
            locker1 = Locker(name='Locker A', number='A1', location='Building 1, Floor 1')
            locker2 = Locker(name='Locker B', number='B1', location='Building 1, Floor 1')
            locker3 = Locker(name='Locker C', number='C1', location='Building 2, Floor 1')
            
            db.session.add(locker1)
            db.session.add(locker2)
            db.session.add(locker3)
            
            # Create default items
            item1 = Item(name='Laptop', description='Dell XPS 13', category='Electronics', brand='Dell', model='XPS 13', condition='good', value=1200.00, locker_id=1)
            item2 = Item(name='Tablet', description='iPad Pro', category='Electronics', brand='Apple', model='iPad Pro', condition='new', value=800.00, locker_id=2)
            item3 = Item(name='Projector', description='Epson Projector', category='Electronics', brand='Epson', model='PowerLite', condition='good', value=500.00, locker_id=3)
            
            db.session.add(item1)
            db.session.add(item2)
            db.session.add(item3)
            
            # Create default system settings
            settings = [
                SystemSetting(key='max_borrow_duration', value='7', description='Maximum borrow duration in days', category='borrowing'),
                SystemSetting(key='max_items_per_user', value='3', description='Maximum items a user can borrow at once', category='borrowing'),
                SystemSetting(key='overdue_fee_per_day', value='5.00', description='Daily fee for overdue items', category='fees'),
                SystemSetting(key='system_name', value='Smart Locker System', description='System display name', category='general'),
                SystemSetting(key='maintenance_mode', value='false', description='Enable maintenance mode', category='system'),
                SystemSetting(key='session_timeout', value='3600', description='Session timeout in seconds', category='security'),
            ]
            
            for setting in settings:
                db.session.add(setting)
            
            db.session.commit()
            
            # Create some sample logs
            log1 = Log(user_id=1, action_type='login', action_details='Admin user logged in', ip_address='127.0.0.1')
            log2 = Log(user_id=2, action_type='login', action_details='Student user logged in', ip_address='127.0.0.1')
            
            db.session.add(log1)
            db.session.add(log2)
            db.session.commit()

    return User, Locker, Item, Log, Borrow, Return, Payment, Notification, SystemSetting, UserSession, init_db 