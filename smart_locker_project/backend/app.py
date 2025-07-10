#!/usr/bin/env python3

from flask import Flask, jsonify, request, render_template, Response, g, session, redirect, url_for
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
from flask_babel import Babel

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

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================

# Set up base directory and database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PostgreSQL Database Configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'smart_locker')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')

# Initialize Flask application
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

# Initialize Babel
babel = Babel(app)

# Babel configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'fr', 'es', 'tr']

def get_locale():
    """Get the locale for the current request"""
    # Try to get locale from session
    if 'language' in session:
        return session['language']
    # Try to get locale from request
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

# Import and initialize models from models.py
from models import init_models
User, Locker, Item, Log, Borrow, init_db_func, generate_dummy_data = init_models(db)

# Keep only the User model definition here since it's used by existing code
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

# Remove all other model definitions (Locker, Item, Borrow, Log, Return) from app.py
# They will be imported from models.py when needed

# Helper functions
def log_action(action_type, user_id=None, item_id=None, locker_id=None, details=None, ip_address=None, user_agent=None):
    """Log an action to the database"""
    try:
        log = Log(
            user_id=user_id,
            item_id=item_id,
            locker_id=locker_id,
            action_type=action_type,
            notes=details,
            ip_address=ip_address,
            user_agent=user_agent
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
@app.before_request
def before_request():
    """
    Set up global variables before each request.
    """
    g.locale = get_locale()

# --- Language selection ---
@app.route('/language/<language>')
def set_language(language):
    if language in app.config['BABEL_SUPPORTED_LOCALES']:
        session['language'] = language
    return redirect(request.referrer or url_for('main_menu'))

# --- Auth routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
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
    # Optionally handle GET requests here
    return jsonify({"message": "Login endpoint"})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API login endpoint for frontend"""
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
                "token": access_token,  # Frontend expects 'token' not 'access_token'
                "user": user.to_dict()
            })
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logger.error(f"API login error: {e}")
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
                log.notes,
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 500

def init_db(minimal=False):
    """Initialize the database with default data"""
    with app.app_context():
        db.create_all()
        
        if not minimal:
            # Generate comprehensive demo data
            generate_dummy_data()
            logger.info("Database initialized with comprehensive demo data (from models.py)")
        else:
            # Minimal admin only - use real tables (empty for now)
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
                db.session.commit()
                logger.info("Database initialized with minimal admin user (real tables, empty for now)")

@app.route('/api/admin/active-borrows', methods=['GET'])
@jwt_required()
@admin_required
def get_active_borrows():
    """Get active borrows for admin dashboard"""
    try:
        limit = request.args.get('limit', 25, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get active borrows with pagination
        borrows = Borrow.query.filter_by(status='active').offset(offset).limit(limit).all()
        
        return jsonify({
            "borrows": [borrow.to_dict() for borrow in borrows],
            "total": Borrow.query.filter_by(status='active').count(),
            "limit": limit,
            "offset": offset
        })
    except Exception as e:
        logger.error(f"Get active borrows error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_users():
    """Get all users for admin dashboard"""
    try:
        limit = request.args.get('limit', 25, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get all users with pagination
        users = User.query.offset(offset).limit(limit).all()
        
        return jsonify({
            "users": [user.to_dict() for user in users],
            "total": User.query.count(),
            "limit": limit,
            "offset": offset
        })
    except Exception as e:
        logger.error(f"Get admin users error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(user.to_dict())
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Locker System')
    parser.add_argument('--port', type=int, default=5050, help='Port to run on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run on')
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--minimal', action='store_true', help='Run in minimal mode (no demo data)')
    parser.add_argument('--demo', action='store_true', help='Load demo data (not minimal)')
    parser.add_argument('--reset-db', action='store_true', help='Drop and recreate all tables')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose (DEBUG) logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Handle --reset-db or --init-db
    if args.reset_db or args.init_db:
        print("Initializing database...")
        # If minimal is set, or demo is not set, use minimal
        minimal = args.minimal or not args.demo
        init_db(minimal=minimal)
        print("Database initialization complete!")
    
    print(f"Starting Smart Locker System on {args.host}:{args.port}")
    if args.minimal:
        print("Running in minimal mode")
    if args.demo:
        print("Loading comprehensive demo data")
    app.run(host=args.host, port=args.port, debug=True) 