from flask import Flask, jsonify
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
import secrets
import os
from auth.routes import auth

def create_app(testing=False):
    app = Flask(__name__, 
                static_folder='auth/static',
                template_folder='auth/templates')
    
    # Enable CORS
    CORS(app, resources={
        r"/auth/*": {
            "origins": ["http://localhost:3002"],
            "supports_credentials": True
        }
    })
    
    # Security configurations
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    app.config['SESSION_COOKIE_SECURE'] = not testing
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens
    
    # Initialize extensions
    csrf = CSRFProtect()
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    if not testing:
        Talisman(app, 
            content_security_policy={
                'default-src': "'self'",
                'img-src': "'self' data: https:",
                'script-src': "'self' 'unsafe-inline'",
                'style-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
                'connect-src': "'self' http://localhost:3002",
                'frame-ancestors': "'self' http://localhost:3002"
            },
            force_https=False  # Set to False for local development
        )
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    csrf.init_app(app)
    
    # Basic error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {'message': 'Resource not found'}, 404

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {'message': 'Rate limit exceeded'}, 429

    @app.errorhandler(500)
    def internal_error(e):
        return {'message': 'Internal server error'}, 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 