import os
import argparse
from flask import Flask, render_template, redirect, url_for, session, request, flash, g  # type: ignore[import]
from flask_sqlalchemy import SQLAlchemy  # type: ignore[import]
from flask_babel import Babel, gettext, ngettext  # type: ignore[import]
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore[import]
from datetime import timedelta

# Set up base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'db')
DB_PATH = os.path.join(DB_DIR, 'locker.db')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Smart Locker System')
    parser.add_argument('--port', type=int, default=5050, help='Port to run the server on (default: 5050)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    args = parser.parse_args()
    
    with app.app_context():
        init_db()
    print(f"Starting Smart Locker System on http://{args.host}:{args.port}")
    app.run(debug=True, host=args.host, port=args.port) 