"""
Check if the API server is running and start it if needed.
"""

import os
import sys
import time
import logging
import subprocess
import requests
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_port_in_use(port):
    """Check if a port is in use using a simple socket connection."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

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
        # Check if port 5000 is already in use
        if is_port_in_use(5000):
            logger.warning("Port 5000 is already in use")
            logger.warning("Please close any applications using port 5000 and try again")
            return False
        
        # Start the API server
        logger.info("Starting API server...")
        
        # Use the direct API service approach
        cmd = [
            sys.executable, 
            "-c", 
            "from src.api_service import ApiService; api = ApiService(); api.run()"
        ]
        
        # Start the process
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE  # Open in new window on Windows
            )
        except AttributeError:
            # For non-Windows systems
            process = subprocess.Popen(
                cmd,
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
        logger.info("API server is not running. Starting it...")
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