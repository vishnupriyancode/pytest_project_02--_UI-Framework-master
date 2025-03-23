#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path
import logging
from config import setup_logging, API_PORT, FRONTEND_PORT

# Setup logging
loggers = setup_logging()
logger = logging.getLogger('api')

def is_windows():
    return platform.system().lower() == 'windows'

def run_command(command, wait=True):
    """Run a command and return its output"""
    try:
        if is_windows():
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if wait:
            stdout, stderr = process.communicate()
            return process.returncode == 0, stdout.decode(), stderr.decode()
        return True, None, None
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False, None, str(e)

def start_api_server():
    """Start the API server"""
    logger.info("Starting API server...")
    success, stdout, stderr = run_command(f"python api_server.py --port {API_PORT}")
    if not success:
        logger.error(f"Error starting API server: {stderr}")
        return False
    logger.info(f"API server started successfully on port {API_PORT}")
    return True

def start_frontend():
    """Start the frontend development server"""
    logger.info("Starting frontend development server...")
    success, stdout, stderr = run_command(f"npm start -- --port {FRONTEND_PORT}")
    if not success:
        logger.error(f"Error starting frontend: {stderr}")
        return False
    logger.info(f"Frontend server started successfully on port {FRONTEND_PORT}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Start the application')
    parser.add_argument('--api-only', action='store_true', help='Start only the API server')
    parser.add_argument('--frontend-only', action='store_true', help='Start only the frontend')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    try:
        if args.api_only:
            return start_api_server()
        elif args.frontend_only:
            return start_frontend()
        else:
            # Start both servers
            api_success = start_api_server()
            frontend_success = start_frontend()
            return api_success and frontend_success
    except KeyboardInterrupt:
        logger.info("Shutting down servers...")
        return True
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 