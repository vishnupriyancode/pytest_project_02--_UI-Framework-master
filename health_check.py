import requests
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_api_server():
    """Check if the API server is running and responding."""
    try:
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            logger.info("✅ API server is running and healthy")
            return True
        else:
            logger.error("❌ API server returned non-200 status code")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ API server is not running")
        return False

def check_directories():
    """Check if all required directories exist."""
    required_dirs = ['logs', 'output', 'Edit1_jsons']
    all_exist = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            logger.info(f"✅ Directory '{dir_name}' exists")
        else:
            logger.error(f"❌ Directory '{dir_name}' is missing")
            all_exist = False
    
    return all_exist

def check_env_file():
    """Check if .env file exists and has required variables."""
    if not Path('.env').exists():
        logger.error("❌ .env file is missing")
        return False
    
    required_vars = ['PG_HOST', 'PG_PORT', 'PG_DBNAME', 'PG_USER', 'PG_PASSWORD']
    with open('.env', 'r') as f:
        env_content = f.read()
    
    missing_vars = [var for var in required_vars if var not in env_content]
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ .env file is properly configured")
    return True

def check_dependencies():
    """Check if all required Python packages are installed."""
    try:
        import pandas
        import numpy
        import flask
        import sqlalchemy
        logger.info("✅ All required Python packages are installed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing required package: {str(e)}")
        return False

def main():
    """Run all health checks."""
    logger.info("Starting health check...")
    
    checks = {
        "API Server": check_api_server(),
        "Directories": check_directories(),
        "Environment File": check_env_file(),
        "Dependencies": check_dependencies()
    }
    
    # Print summary
    logger.info("\nHealth Check Summary:")
    for check, status in checks.items():
        status_symbol = "✅" if status else "❌"
        logger.info(f"{status_symbol} {check}")
    
    # Exit with error if any check failed
    if not all(checks.values()):
        sys.exit(1)

if __name__ == "__main__":
    main() 