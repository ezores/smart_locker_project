#!/usr/bin/env python3

from flask import Flask, jsonify, request, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import logging
import json
import io
import csv
from functools import wraps
from utils.rs485 import open_locker, close_locker, get_locker_status, test_rs485_connection
from utils.export import export_data_csv, export_data_excel, export_data_pdf, export_system_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Database configuration - supports both SQLite and PostgreSQL
database_url = os.getenv('DATABASE_URL', 'sqlite:///smart_locker.db')
if database_url.startswith('postgresql://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Models
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
    role = db.Column(db.String(16), nullable=False, default='student')
    department = db.Column(db.String(50))
    balance = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    __tablename__ = 'lockers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    number = db.Column(db.String(10), unique=True, nullable=False)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='available')
    capacity = db.Column(db.Integer, default=1)
    current_occupancy = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    condition = db.Column(db.String(20), default='good')
    status = db.Column(db.String(20), default='available')
    locker_id = db.Column(db.Integer, db.ForeignKey('lockers.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    locker = db.relationship('Locker', backref='items')

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

class Borrow(db.Model):
    __tablename__ = 'borrows'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    locker_id = db.Column(db.Integer, db.ForeignKey('lockers.id'), nullable=False)
    borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    returned_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='borrows')
    item = db.relationship('Item', backref='borrows')
    locker = db.relationship('Locker', backref='borrows')

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

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    locker_id = db.Column(db.Integer, db.ForeignKey('lockers.id'))
    borrow_id = db.Column(db.Integer, db.ForeignKey('borrows.id'))
    return_id = db.Column(db.Integer, db.ForeignKey('returns.id'))
    action_type = db.Column(db.String(50), nullable=False)
    action_details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='logs')
    item = db.relationship('Item', backref='logs')
    locker = db.relationship('Locker', backref='logs')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'locker_id': self.locker_id,
            'action_type': self.action_type,
            'action_details': self.action_details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_name': f"{self.user.first_name} {self.user.last_name}" if self.user else None,
            'item_name': self.item.name if self.item else None,
            'locker_name': self.locker.name if self.locker else None
        }

class Return(db.Model):
    __tablename__ = 'returns'
    
    id = db.Column(db.Integer, primary_key=True)
    borrow_id = db.Column(db.Integer, db.ForeignKey('borrows.id'), nullable=False)
    returned_at = db.Column(db.DateTime, default=datetime.utcnow)
    condition = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrow = db.relationship('Borrow', backref='returns')

    def to_dict(self):
        return {
            'id': self.id,
            'borrow_id': self.borrow_id,
            'returned_at': self.returned_at.isoformat() if self.returned_at else None,
            'condition': self.condition,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Helper functions
def log_action(action_type, user_id=None, item_id=None, locker_id=None, details=None):
    """Log an action to the database"""
    try:
        log = Log(
            user_id=user_id,
            item_id=item_id,
            locker_id=locker_id,
            action_type=action_type,
            action_details=details,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        db.session.add(log)
        db.session.commit()
        logger.info(f"Action logged: {action_type} - {details}")
    except Exception as e:
        logger.error(f"Failed to log action: {e}")

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

# Routes
@app.route('/')
def home():
    return jsonify({
        "message": "Smart Locker System API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth/*",
            "users": "/api/users/*",
            "lockers": "/api/lockers/*",
            "items": "/api/items/*",
            "borrows": "/api/borrows/*",
            "logs": "/api/logs/*",
            "admin": "/api/admin/*"
        }
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            
            # Log the login
            log_action('login', user.id, details=f"User {username} logged in")
            
            return jsonify({
                "access_token": access_token,
                "user": user.to_dict()
            })
        else:
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        role = data.get('role', 'student')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        log_action('register', user.id, details=f"New user {username} registered")
        
        return jsonify({"message": "User registered successfully", "user": user.to_dict()}), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "users": [user.to_dict() for user in users.items],
            "total": users.total,
            "pages": users.pages,
            "current_page": page
        })
    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({"user": user.to_dict()})
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/lockers', methods=['GET'])
@jwt_required()
def get_lockers():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Locker.query
        if status:
            query = query.filter_by(status=status)
        
        lockers = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "lockers": [locker.to_dict() for locker in lockers.items],
            "total": lockers.total,
            "pages": lockers.pages,
            "current_page": page
        })
    except Exception as e:
        logger.error(f"Get lockers error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/items', methods=['GET'])
@jwt_required()
def get_items():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        category = request.args.get('category')
        
        query = Item.query
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        
        items = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "items": [item.to_dict() for item in items.items],
            "total": items.total,
            "pages": items.pages,
            "current_page": page
        })
    except Exception as e:
        logger.error(f"Get items error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/borrows', methods=['GET'])
@jwt_required()
def get_borrows():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        
        query = Borrow.query
        if status:
            query = query.filter_by(status=status)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        borrows = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "borrows": [borrow.to_dict() for borrow in borrows.items],
            "total": borrows.total,
            "pages": borrows.pages,
            "current_page": page
        })
    except Exception as e:
        logger.error(f"Get borrows error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/borrows', methods=['POST'])
@jwt_required()
def create_borrow():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        item_id = data.get('item_id')
        due_date = data.get('due_date')
        
        if not user_id or not item_id:
            return jsonify({"error": "User ID and Item ID required"}), 400
        
        # Check if item is available
        item = Item.query.get(item_id)
        if not item or item.status != 'available':
            return jsonify({"error": "Item not available"}), 400
        
        # Create borrow
        borrow = Borrow(
            user_id=user_id,
            item_id=item_id,
            locker_id=item.locker_id,
            due_date=datetime.fromisoformat(due_date) if due_date else None
        )
        
        # Update item status
        item.status = 'borrowed'
        
        db.session.add(borrow)
        db.session.commit()
        
        log_action('borrow', user_id, item_id, item.locker_id, f"Item {item.name} borrowed")
        
        return jsonify({"message": "Item borrowed successfully", "borrow": borrow.to_dict()}), 201
        
    except Exception as e:
        logger.error(f"Create borrow error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/borrows/<int:borrow_id>/return', methods=['POST'])
@jwt_required()
def return_item(borrow_id):
    try:
        data = request.get_json()
        condition = data.get('condition', 'good')
        notes = data.get('notes')
        
        borrow = Borrow.query.get_or_404(borrow_id)
        
        if borrow.status != 'active':
            return jsonify({"error": "Borrow is not active"}), 400
        
        # Create return record
        return_record = Return(
            borrow_id=borrow_id,
            condition=condition,
            notes=notes
        )
        
        # Update borrow status
        borrow.status = 'returned'
        borrow.returned_at = datetime.utcnow()
        
        # Update item status
        item = borrow.item
        item.status = 'available'
        
        db.session.add(return_record)
        db.session.commit()
        
        log_action('return', borrow.user_id, borrow.item_id, borrow.locker_id, f"Item {item.name} returned")
        
        return jsonify({"message": "Item returned successfully", "return": return_record.to_dict()})
        
    except Exception as e:
        logger.error(f"Return item error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/logs', methods=['GET'])
@jwt_required()
@admin_required
def get_logs():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action_type = request.args.get('action_type')
        user_id = request.args.get('user_id', type=int)
        
        query = Log.query
        if action_type:
            query = query.filter_by(action_type=action_type)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        logs = query.order_by(Log.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "logs": [log.to_dict() for log in logs.items],
            "total": logs.total,
            "pages": logs.pages,
            "current_page": page
        })
    except Exception as e:
        logger.error(f"Get logs error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_stats():
    try:
        total_users = User.query.count()
        total_lockers = Locker.query.count()
        total_items = Item.query.count()
        active_borrows = Borrow.query.filter_by(status='active').count()
        available_items = Item.query.filter_by(status='available').count()
        
        return jsonify({
            "total_users": total_users,
            "total_lockers": total_lockers,
            "total_items": total_items,
            "active_borrows": active_borrows,
            "available_items": available_items
        })
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/admin/export/logs', methods=['GET'])
@jwt_required()
@admin_required
def export_logs():
    try:
        logs = Log.query.order_by(Log.timestamp.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'User', 'Item', 'Locker', 'Action', 'Details', 'IP', 'Timestamp'])
        
        for log in logs:
            writer.writerow([
                log.id,
                f"{log.user.first_name} {log.user.last_name}" if log.user else '',
                log.item.name if log.item else '',
                log.locker.name if log.locker else '',
                log.action_type,
                log.action_details,
                log.ip_address,
                log.timestamp
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=logs.csv'}
        )
        
    except Exception as e:
        logger.error(f"Export logs error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# RS485 Locker Control Endpoints
@app.route('/api/lockers/<int:locker_id>/open', methods=['POST'])
@jwt_required()
@admin_required
def open_locker_endpoint(locker_id):
    """Open a locker using RS485"""
    try:
        # Check if locker exists
        locker = Locker.query.get_or_404(locker_id)
        
        # Open locker using RS485
        result = open_locker(locker_id)
        
        # Log the action
        log_action('open_locker', get_jwt_identity(), locker_id=locker_id, 
                  details=f"Locker {locker.name} opened via RS485")
        
        return jsonify({
            "message": "Locker opening command sent",
            "locker_id": locker_id,
            "locker_name": locker.name,
            "rs485_result": result
        })
        
    except Exception as e:
        logger.error(f"Open locker error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/lockers/<int:locker_id>/close', methods=['POST'])
@jwt_required()
@admin_required
def close_locker_endpoint(locker_id):
    """Close a locker using RS485"""
    try:
        # Check if locker exists
        locker = Locker.query.get_or_404(locker_id)
        
        # Close locker using RS485
        result = close_locker(locker_id)
        
        # Log the action
        log_action('close_locker', get_jwt_identity(), locker_id=locker_id, 
                  details=f"Locker {locker.name} closed via RS485")
        
        return jsonify({
            "message": "Locker closing command sent",
            "locker_id": locker_id,
            "locker_name": locker.name,
            "rs485_result": result
        })
        
    except Exception as e:
        logger.error(f"Close locker error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/lockers/<int:locker_id>/status', methods=['GET'])
@jwt_required()
@admin_required
def get_locker_status_endpoint(locker_id):
    """Get locker status via RS485"""
    try:
        # Check if locker exists
        locker = Locker.query.get_or_404(locker_id)
        
        # Get locker status using RS485
        result = get_locker_status(locker_id)
        
        return jsonify({
            "locker_id": locker_id,
            "locker_name": locker.name,
            "rs485_status": result
        })
        
    except Exception as e:
        logger.error(f"Get locker status error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/admin/rs485/test', methods=['GET'])
@jwt_required()
@admin_required
def test_rs485_endpoint():
    """Test RS485 connection"""
    try:
        result = test_rs485_connection()
        return jsonify({
            "message": "RS485 connection test completed",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"RS485 test error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Export Endpoints
@app.route('/api/admin/export/users', methods=['GET'])
@jwt_required()
@admin_required
def export_users():
    """Export users data in various formats"""
    try:
        format_type = request.args.get('format', 'csv')
        users = User.query.all()
        user_data = [user.to_dict() for user in users]
        
        if format_type == 'csv':
            csv_content = export_data_csv(user_data)
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=users.csv'}
            )
        elif format_type == 'excel':
            excel_content = export_data_excel(user_data)
            return Response(
                excel_content,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': 'attachment; filename=users.xlsx'}
            )
        elif format_type == 'pdf':
            sections = [{"title": "Users", "content": user_data}]
            pdf_content = export_data_pdf("Users Report", sections)
            return Response(
                pdf_content,
                mimetype='application/pdf',
                headers={'Content-Disposition': 'attachment; filename=users.pdf'}
            )
        else:
            return jsonify({"error": "Unsupported format"}), 400
            
    except Exception as e:
        logger.error(f"Export users error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/admin/export/borrows', methods=['GET'])
@jwt_required()
@admin_required
def export_borrows():
    """Export borrows data in various formats"""
    try:
        format_type = request.args.get('format', 'csv')
        borrows = Borrow.query.all()
        borrow_data = [borrow.to_dict() for borrow in borrows]
        
        if format_type == 'csv':
            csv_content = export_data_csv(borrow_data)
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=borrows.csv'}
            )
        elif format_type == 'excel':
            excel_content = export_data_excel(borrow_data)
            return Response(
                excel_content,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': 'attachment; filename=borrows.xlsx'}
            )
        elif format_type == 'pdf':
            sections = [{"title": "Borrows", "content": borrow_data}]
            pdf_content = export_data_pdf("Borrows Report", sections)
            return Response(
                pdf_content,
                mimetype='application/pdf',
                headers={'Content-Disposition': 'attachment; filename=borrows.pdf'}
            )
        else:
            return jsonify({"error": "Unsupported format"}), 400
            
    except Exception as e:
        logger.error(f"Export borrows error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/admin/export/system', methods=['GET'])
@jwt_required()
@admin_required
def export_system_report():
    """Export comprehensive system report"""
    try:
        format_type = request.args.get('format', 'pdf')
        report_type = request.args.get('type', 'comprehensive')
        
        report_content = export_system_report(db, format_type, report_type)
        
        if format_type == 'csv':
            return Response(
                report_content,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=system_report.csv'}
            )
        elif format_type == 'excel':
            return Response(
                report_content,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': 'attachment; filename=system_report.xlsx'}
            )
        elif format_type == 'pdf':
            return Response(
                report_content,
                mimetype='application/pdf',
                headers={'Content-Disposition': 'attachment; filename=system_report.pdf'}
            )
        else:
            return jsonify({"error": "Unsupported format"}), 400
            
    except Exception as e:
        logger.error(f"Export system report error: {e}")
        return jsonify({"error": "Internal server error"}), 500

def init_db(minimal=False):
    """Initialize the database with default data"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@smartlocker.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                department='IT'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create test student
            student = User(
                username='student',
                email='student@smartlocker.com',
                first_name='Student',
                last_name='User',
                role='student',
                department='CS'
            )
            student.set_password('password123')
            db.session.add(student)
            
            if not minimal:
                # Create test lockers
                for i in range(1, 6):
                    locker = Locker(
                        name=f'Locker {i}',
                        number=f'L{i:03d}',
                        location=f'Room {i}',
                        status='available',
                        capacity=5,
                        current_occupancy=0
                    )
                    db.session.add(locker)
                
                # Create test items
                categories = ['Electronics', 'Books', 'Tools', 'Sports']
                for i in range(1, 11):
                    item = Item(
                        name=f'Item {i}',
                        description=f'Test item {i}',
                        category=categories[i % len(categories)],
                        condition='good',
                        status='available',
                        locker_id=(i % 5) + 1
                    )
                    db.session.add(item)
            
            db.session.commit()
            logger.info("Database initialized with default data")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Locker System')
    parser.add_argument('--port', type=int, default=5050, help='Port to run on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run on')
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--minimal', action='store_true', help='Run in minimal mode (no demo data)')
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    if args.init_db:
        print("Initializing database...")
        init_db(minimal=args.minimal)
        print("Database initialization complete!")
    
    print(f"Starting Smart Locker System on {args.host}:{args.port}")
    if args.minimal:
        print("Running in minimal mode")
    app.run(host=args.host, port=args.port, debug=True) 