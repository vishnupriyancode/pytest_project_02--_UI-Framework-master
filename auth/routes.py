from flask import render_template, request, jsonify, redirect, url_for, flash, make_response, session
from werkzeug.security import check_password_hash
from . import auth
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os

# Demo user (replace with database in production)
DEMO_USER = {
    'username': 'admin',
    'password': 'pbkdf2:sha256:260000$rqGBWXNZ$47b6a4d382b4f31e4a92ff6b9e3829e1b6c935f3e73fe37c593e9bd5c9c95062'  # Hash for 'Admin123!'
}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token') or request.cookies.get('token')
        
        if not token:
            if request.is_json:
                return jsonify({'message': 'Token is missing'}), 401
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
            
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY', 'your-secret-key'), algorithms=['HS256'])
            current_user = data.get('user')
        except jwt.ExpiredSignatureError:
            if request.is_json:
                return jsonify({'message': 'Token has expired'}), 401
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        except jwt.InvalidTokenError:
            if request.is_json:
                return jsonify({'message': 'Invalid token'}), 401
            flash('Invalid session. Please login again.', 'error')
            return redirect(url_for('auth.login'))
            
        return f(*args, **kwargs)
    return decorated

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Check if user is already logged in
        token = request.cookies.get('token')
        if token:
            try:
                jwt.decode(token, os.getenv('SECRET_KEY', 'your-secret-key'), algorithms=['HS256'])
                return redirect(url_for('auth.dashboard'))
            except:
                pass
        return render_template('login.html')
    
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember', False)

    if not username or not password:
        if request.is_json:
            return jsonify({'message': 'Username and password are required'}), 400
        flash('Username and password are required', 'error')
        return redirect(url_for('auth.login'))

    if username == DEMO_USER['username'] and check_password_hash(DEMO_USER['password'], password):
        token = jwt.encode({
            'user': username,
            'exp': datetime.utcnow() + timedelta(days=30 if remember else 1)
        }, os.getenv('SECRET_KEY', 'your-secret-key'))

        if request.is_json:
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'redirect': url_for('auth.dashboard')
            })
        
        response = make_response(redirect(url_for('auth.dashboard')))
        response.set_cookie(
            'token', 
            token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=30*24*60*60 if remember else 24*60*60
        )
        return response

    if request.is_json:
        return jsonify({'message': 'Invalid username or password'}), 401
    flash('Invalid username or password', 'error')
    return redirect(url_for('auth.login'))

@auth.route('/dashboard')
@token_required
def dashboard():
    token = request.args.get('token') or request.cookies.get('token')
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY', 'your-secret-key'), algorithms=['HS256'])
        username = payload.get('user')
        if request.is_json:
            return jsonify({
                'message': 'Dashboard data retrieved successfully',
                'username': username,
                'data': {
                    'tests_run': 150,
                    'success_rate': '95%',
                    'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        return render_template('dashboard.html', username=username)
    except Exception as e:
        if request.is_json:
            return jsonify({'message': str(e)}), 401
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    response = make_response(redirect(url_for('auth.login')))
    response.delete_cookie('token')
    flash('Successfully logged out', 'success')
    return response

@auth.route('/check-auth')
def check_auth():
    token = request.cookies.get('token')
    if not token:
        return jsonify({'authenticated': False}), 401
    
    try:
        jwt.decode(token, os.getenv('SECRET_KEY', 'your-secret-key'), algorithms=['HS256'])
        return jsonify({'authenticated': True})
    except:
        return jsonify({'authenticated': False}), 401 