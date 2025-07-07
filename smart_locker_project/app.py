from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/locker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db = SQLAlchemy(app)

# Import models using the new init_models function
def import_models():
    from models import init_models
    return init_models(db)

User, Locker, Item, Log, init_db = import_models()

# --- Auth routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Placeholder
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Placeholder
    return redirect(url_for('login'))

# --- Main menu ---
@app.route('/')
def main_menu():
    # Placeholder
    return render_template('main_menu.html')

# --- Borrow/Return ---
@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    # Placeholder
    return render_template('borrow.html')

@app.route('/return', methods=['GET', 'POST'])
def return_item():
    # Placeholder
    return render_template('return.html')

# --- Admin Dashboard ---
@app.route('/admin')
def admin_dashboard():
    # Placeholder
    return render_template('admin_dashboard.html')

# --- Users CRUD ---
@app.route('/users')
def users():
    # Placeholder
    return render_template('users.html')

# --- Items CRUD ---
@app.route('/items')
def items():
    # Placeholder
    return render_template('items.html')

# --- Lockers CRUD ---
@app.route('/lockers')
def lockers():
    # Placeholder
    return render_template('lockers.html')

# --- Logs ---
@app.route('/logs')
def logs():
    # Placeholder
    return render_template('logs.html')

if __name__ == '__main__':
    if not os.path.exists('db'):
        os.makedirs('db')
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000) 