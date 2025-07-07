import os
import argparse
from flask import Flask, render_template, redirect, url_for, session, request, flash, g, jsonify  # type: ignore[import]
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy  # type: ignore[import]
from flask_babel import Babel, gettext, ngettext  # type: ignore[import]
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore[import]
import jwt
from datetime import datetime, timedelta
from datetime import timedelta

# Set up base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'db')
DB_PATH = os.path.join(DB_DIR, 'locker.db')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Babel configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'fr', 'es', 'tr']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

db = SQLAlchemy(app)

def get_locale():
    # Check if user has selected a language
    if 'language' in session:
        return session['language']
    # Try to guess the language from the user accept header
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

babel = Babel(app, locale_selector=get_locale)

def import_models():
    from models import init_models
    return init_models(db)

User, Locker, Item, Log, init_db = import_models()

@app.before_request
def before_request():
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
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('main_menu'))
        else:
            flash(gettext('Invalid username or password'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Main menu ---
@app.route('/')
def main_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('main_menu.html')

# --- Borrow/Return ---
@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('borrow.html')

@app.route('/return', methods=['GET', 'POST'])
def return_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('return.html')

# --- Admin Dashboard ---
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('main_menu'))
    return render_template('admin_dashboard.html')

# --- Users CRUD ---
@app.route('/users')
def users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('main_menu'))
    return render_template('users.html')

# --- Items CRUD ---
@app.route('/items')
def items():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('main_menu'))
    return render_template('items.html')

# --- Lockers CRUD ---
@app.route('/lockers')
def lockers():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('main_menu'))
    return render_template('lockers.html')

# --- Logs ---
@app.route('/logs')
def logs():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('main_menu'))
    return render_template('logs.html')

# --- API Routes for React Frontend ---
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        # Create JWT token
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        })
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/api/user/profile')
def api_user_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        if user:
            return jsonify({
                'id': user.id,
                'username': user.username,
                'role': user.role
            })
        else:
            return jsonify({'message': 'User not found'}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

@app.route('/api/items')
def api_items():
    items = Item.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'locker_id': item.locker_id
    } for item in items])

@app.route('/api/lockers')
def api_lockers():
    lockers = Locker.query.all()
    return jsonify([{
        'id': locker.id,
        'number': locker.name,
        'location': f'Location {locker.id}',
        'status': 'available'
    } for locker in lockers])

@app.route('/api/borrow', methods=['POST'])
def api_borrow():
    data = request.get_json()
    # Mock borrow functionality
    return jsonify({'message': 'Item borrowed successfully'})

@app.route('/api/return', methods=['POST'])
def api_return():
    data = request.get_json()
    # Mock return functionality
    return jsonify({'message': 'Item returned successfully'})

@app.route('/api/admin/stats')
def api_admin_stats():
    return jsonify({
        'totalUsers': User.query.count(),
        'totalItems': Item.query.count(),
        'totalLockers': Locker.query.count(),
        'activeBorrows': Log.query.filter_by(action_type='borrow').count()
    })

@app.route('/api/admin/recent-activity')
def api_recent_activity():
    logs = Log.query.order_by(Log.timestamp.desc()).limit(10).all()
    return jsonify([{
        'id': log.id,
        'type': log.action_type,
        'user': User.query.get(log.user_id).username if log.user_id else 'Unknown',
        'item': Item.query.get(log.item_id).name if log.item_id else 'Unknown',
        'timestamp': log.timestamp.isoformat(),
        'status': 'completed'
    } for log in logs])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Smart Locker System')
    parser.add_argument('--port', type=int, default=5050, help='Port to run the server on (default: 5050)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    args = parser.parse_args()
    
    with app.app_context():
        init_db()
    print(f"Starting Smart Locker System on http://{args.host}:{args.port}")
    app.run(debug=True, host=args.host, port=args.port) 