import os
import logging
from datetime import datetime

# File paths
JSON_FILES_DIR = r"C:\json_files"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

# Create directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Excel output file
EXCEL_OUTPUT = os.path.join(OUTPUT_DIR, f"api_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

# Logging configuration
LOG_FILE = os.path.join(LOG_DIR, f"processing_log_{datetime.now().strftime('%Y%m%d')}.log")
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

# API configuration
API_PORT = 5000
API_HOST = '0.0.0.0' 