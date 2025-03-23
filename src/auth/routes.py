from flask import (
    render_template, request, jsonify, redirect,
    url_for, flash, session, current_app
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from functools import wraps
import jwt
from datetime import datetime, timedelta
import re
from . import auth
import sqlite3
import logging
import os
import requests
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path for the database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'auth.db')

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize CSRF protection
csrf = CSRFProtect()

def init_db():
    """Initialize the SQLite database with users table"""
    logger.info(f"Initializing database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Drop existing users table if it exists
    c.execute('DROP TABLE IF EXISTS users')
    
    # Create fresh users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP
        )
    ''')
    
    # Add default admin user
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                 ('admin', generate_password_hash('Admin123!')))
        conn.commit()
        logger.info("Default admin user created successfully")
    except sqlite3.IntegrityError:
        logger.info("Default admin user already exists")
    
    conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        if not token:
            return jsonify({'message': 'Authentication required'}), 401
        try:
            jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Invalid or expired token'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth.before_app_first_request
def before_first_request():
    """Initialize database before first request"""
    init_db()

def validate_password(password):
    """
    Validate password strength
    - At least 8 characters
    - Contains uppercase and lowercase letters
    - Contains numbers
    - Contains special characters
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember', False)

    if not username or not password:
        if request.is_json:
            return jsonify({'message': 'Username and password are required'}), 400
        flash('Username and password are required', 'error')
        return redirect(url_for('auth.login'))

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    if user:
        if user['locked_until'] and datetime.now() < datetime.fromisoformat(user['locked_until']):
            message = 'Account is locked. Please try again later.'
            if request.is_json:
                return jsonify({'message': message}), 403
            flash(message, 'error')
            return redirect(url_for('auth.login'))

        if check_password_hash(user['password'], password):
            # Reset failed attempts on successful login
            db.execute('''
                UPDATE users 
                SET failed_attempts = 0, 
                    locked_until = NULL,
                    last_login = CURRENT_TIMESTAMP 
                WHERE username = ?
            ''', (username,))
            db.commit()

            # Generate JWT token
            token = jwt.encode({
                'user_id': user['id'],
                'username': user['username'],
                'exp': datetime.utcnow() + timedelta(days=30 if remember else 1)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')

            session['token'] = token
            
            # Redirect to the application on port 3002
            application_url = 'http://localhost:3002'
            
            if request.is_json:
                return jsonify({
                    'message': 'Login successful',
                    'redirect': application_url,
                    'token': token,
                    'fallback_url': url_for('auth.dashboard')  # Fallback URL if app is not accessible
                }), 200
            
            # For form submission, try to check if the application is available
            try:
                # Try to connect to the application with a timeout
                requests.head(application_url, timeout=2)
                
                response = redirect(application_url)
                response.set_cookie('auth_token', token, 
                                  httponly=True, 
                                  secure=True, 
                                  samesite='Lax',
                                  max_age=30*24*60*60 if remember else 24*60*60)
                return response
            except RequestException:
                # If application is not accessible, show an error message
                flash('Application is not accessible. Please ensure it is running on port 3002.', 'error')
                return redirect(url_for('auth.dashboard'))

        else:
            # Increment failed attempts
            failed_attempts = user['failed_attempts'] + 1
            lock_until = None

            if failed_attempts >= 5:
                lock_until = (datetime.now() + timedelta(minutes=15)).isoformat()

            db.execute('''
                UPDATE users 
                SET failed_attempts = ?,
                    locked_until = ?
                WHERE username = ?
            ''', (failed_attempts, lock_until, username))
            db.commit()

            if lock_until:
                message = 'Too many failed attempts. Account locked for 15 minutes.'
                if request.is_json:
                    return jsonify({'message': message}), 403
                flash(message, 'error')
                return redirect(url_for('auth.login'))

    message = 'Invalid username or password'
    if request.is_json:
        return jsonify({'message': message}), 401
    flash(message, 'error')
    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if not validate_password(password):
        return jsonify({
            'message': 'Password must be at least 8 characters long and contain uppercase, lowercase, numbers, and special characters'
        }), 400

    db = get_db()
    try:
        db.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        db.commit()
        return jsonify({'message': 'Registration successful'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already registered'}), 409

@auth.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    # Implement password reset logic here
    # This would typically involve:
    # 1. Generating a secure reset token
    # 2. Sending an email with reset instructions
    # 3. Creating a reset password endpoint
    return jsonify({'message': 'Password reset instructions sent'}), 200

@auth.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html') 