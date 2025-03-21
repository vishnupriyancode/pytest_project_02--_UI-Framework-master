"""
API Server Starter Script

This script starts the API server with CORS support.
"""

import os
import sys
import time
import logging
import subprocess
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_api_server():
    """Check if the API server is running."""
    try:
        response = requests.get("http://localhost:5000/health-check", timeout=3)
        if response.status_code == 200:
            logger.info("API server is running.")
            return True
        else:
            logger.warning(f"API server responded with status code {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.warning(f"API server is not running: {e}")
        return False

def start_api_server():
    """Start the API server."""
    try:
        # Use the enhanced_main.py to start the server
        process = subprocess.Popen(
            [sys.executable, "enhanced_main.py", "--db_type", "sqlite"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the server to start
        logger.info("Waiting for API server to start...")
        for _ in range(10):  # Try for 10 seconds
            time.sleep(1)
            if check_api_server():
                logger.info("API server started successfully.")
                return True
        
        logger.error("Failed to start API server within timeout.")
        return False
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        return False

def main():
    """Main entry point."""
    logger.info("Checking if API server is running...")
    if not check_api_server():
        logger.info("Starting API server...")
        if start_api_server():
            logger.info("API server is now running.")
            print("""
            ================================
            API server is now running at:
            http://localhost:5000
            
            Health check endpoint:
            http://localhost:5000/health-check
            
            React app should connect automatically.
            ================================
            """)
        else:
            logger.error("Failed to start API server.")
            return 1
    else:
        logger.info("API server is already running.")
        print("""
        ================================
        API server is already running at:
        http://localhost:5000
        
        Health check endpoint:
        http://localhost:5000/health-check
        
        React app should connect automatically.
        ================================
        """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 