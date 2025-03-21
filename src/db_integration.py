import logging
import importlib
import sys
from typing import Any

# Configure logging
logging.basicConfig(
    filename='logs/db_integration.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ApiServiceIntegrator:
    """
    Class to integrate the database middleware with the existing API service
    without modifying the original code.
    """
    
    @staticmethod
    def integrate():
        """
        Integrate the database middleware with the API service at runtime.
        """
        try:
            # Import the API service module
            api_service_module = importlib.import_module('api_service')
            
            # Import the API middleware module
            from api_middleware import ApiMiddleware
            
            # Store the original run method
            original_run = api_service_module.ApiService.run
            
            # Define a new run method that integrates the middleware
            def enhanced_run(self):
                """Enhanced run method that adds middleware integration."""
                try:
                    logger.info("Starting enhanced API service with database integration")
                    
                    # Register the middleware with the Flask app
                    middleware = ApiMiddleware(self.app)
                    
                    # Call the original run method
                    return original_run(self)
                
                except Exception as e:
                    logger.error(f"Error in enhanced run method: {str(e)}")
                    raise
            
            # Replace the original run method with our enhanced version
            api_service_module.ApiService.run = enhanced_run
            
            logger.info("Successfully integrated database middleware with API service")
            
        except Exception as e:
            logger.error(f"Error integrating middleware: {str(e)}")
            raise

# For direct execution
if __name__ == "__main__":
    # Integrate the middleware with the API service
    ApiServiceIntegrator.integrate()
    print("Database integration complete. API service now includes database functionality.") 