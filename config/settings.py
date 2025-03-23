import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
SOURCE_DIR = BASE_DIR / "Edit1_jsons"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

# API Settings
API_HOST = "localhost"
API_PORT = 5000
API_DEBUG = True

# Frontend Settings
FRONTEND_PORT = 3000
FRONTEND_HOST = "localhost"

# Processing Settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
BATCH_SIZE = 10

# File Settings
ALLOWED_EXTENSIONS = {'json'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
for directory in [SOURCE_DIR, UPLOAD_DIR, OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'
LOG_FILE = LOG_DIR / "app.log"

# Database Settings (if needed)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

# Security Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000'] 