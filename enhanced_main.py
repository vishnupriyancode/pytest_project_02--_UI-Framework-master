import os
import sys
import logging
import importlib
import argparse
import dotenv

# Add the source directory to the path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.append(src_dir)

# Import the database integration module
from src.db_integration import ApiServiceIntegrator
from src.db_manager import DatabaseManager

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/enhanced_main.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

def main(db_type="sqlite"):
    """
    Enhanced main entry point that includes database functionality.
    
    Args:
        db_type: Database type to use ("sqlite" or "postgres")
    """
    try:
        logger.info(f"Starting enhanced JSON processing workflow with {db_type} database integration")
        
        # Load environment variables
        dotenv.load_dotenv()
        
        # Set database type
        os.environ["DB_TYPE"] = db_type
        
        # Apply the database integration before importing the main module
        ApiServiceIntegrator.integrate()
        logger.info("Database integration applied successfully")
        
        # Import the original main module
        import main as original_main
        
        # Call the original main function
        exit_code = original_main.main()
        
        logger.info(f"Enhanced workflow completed with exit code: {exit_code}")
        return exit_code
    
    except Exception as e:
        logger.error(f"Unhandled exception in enhanced main: {str(e)}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the enhanced application with database integration")
    parser.add_argument(
        "--db_type", 
        choices=["sqlite", "postgres"], 
        default="sqlite",
        help="Database type to use"
    )
    
    args = parser.parse_args()
    sys.exit(main(db_type=args.db_type)) 