from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import jwt
from functools import wraps
import os
import secrets

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Use the same secret key as the auth service
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in various places
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        elif 'auth_token' in request.cookies:
            token = request.cookies['auth_token']
        elif 'token' in request.args:
            token = request.args['token']
            
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        try:
            # Verify token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except Exception as e:
            print(f"Token verification error: {str(e)}")
            return jsonify({'message': 'Token is invalid'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
@token_required
def index(current_user):
    return render_template('index.html', username=current_user)

@app.route('/api/user-info')
@token_required
def user_info(current_user):
    return jsonify({
        'username': current_user,
        'status': 'authenticated'
    })

if __name__ == '__main__':
    app.run(port=3002, debug=True)