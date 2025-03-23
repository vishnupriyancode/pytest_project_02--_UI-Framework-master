from flask import Flask, request, jsonify
import os
import json
import pandas as pd
from flask_cors import CORS
import logging
from datetime import datetime
import requests
from auth import auth
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:5000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Secret key for session management
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    
    @app.route('/')
    def index():
        return jsonify({
            "message": "Welcome to API Testing Framework",
            "login_url": "/auth/login",
            "dashboard_url": "/auth/dashboard"
        })

    return app

if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting JSON Processing API on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 