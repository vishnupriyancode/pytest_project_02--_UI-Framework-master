import requests
import json
import logging
import time
import os
import sys
from typing import Dict, Any

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the database integrator
from db_integration import ApiServiceIntegrator
from api_service import ApiService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DbIntegrationTest:
    """
    Class to test the database integration with the API service.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        """
        Initialize the test.
        
        Args:
            base_url: Base URL of the API service.
        """
        self.base_url = base_url
        logger.info(f"Test initialized with base URL: {base_url}")
    
    def test_process_json(self):
        """
        Test the process-json endpoint with database integration.
        """
        try:
            # Create a test payload
            payload = {
                "file_path": "test_file.json",
                "operation": "process_data",
                "data": {
                    "test": "data",
                    "properties": {
                        "name": "Test Property"
                    }
                }
            }
            
            # Make a request to the process-json endpoint
            response = requests.post(
                f"{self.base_url}/process-json",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                edit_id = response_data.get("edit_id")
                
                logger.info(f"Processed JSON successfully with edit_id: {edit_id}")
                logger.info(f"Response: {response_data}")
                
                return edit_id
            else:
                logger.error(f"Failed to process JSON: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error testing process-json: {str(e)}")
            return None
    
    def test_get_response(self, edit_id: int):
        """
        Test the get-response endpoint.
        
        Args:
            edit_id: The edit_id to retrieve.
        """
        try:
            # Make a request to the get-response endpoint
            response = requests.get(f"{self.base_url}/get-response?edit_id={edit_id}")
            
            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                
                logger.info(f"Retrieved response for edit_id {edit_id}")
                logger.info(f"Response: {response_data}")
                
                return response_data
            else:
                logger.error(f"Failed to retrieve response: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error testing get-response: {str(e)}")
            return None
    
    def test_get_all_responses(self):
        """
        Test the get-all-responses endpoint.
        """
        try:
            # Make a request to the get-all-responses endpoint
            response = requests.get(f"{self.base_url}/get-all-responses")
            
            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                
                logger.info(f"Retrieved all responses")
                logger.info(f"Response: {response_data}")
                
                return response_data
            else:
                logger.error(f"Failed to retrieve all responses: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error testing get-all-responses: {str(e)}")
            return None
    
    def run_all_tests(self):
        """
        Run all tests.
        """
        try:
            # Test the process-json endpoint
            edit_id = self.test_process_json()
            
            if edit_id:
                # Wait a moment for the database to be updated
                time.sleep(1)
                
                # Test the get-response endpoint
                self.test_get_response(edit_id)
                
                # Test the get-all-responses endpoint
                self.test_get_all_responses()
                
                logger.info("All tests completed successfully")
                return True
            else:
                logger.error("Tests failed")
                return False
        
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            return False

def run_api_with_integration():
    """Run the API service with database integration."""
    try:
        # Integrate the database middleware with the API service
        ApiServiceIntegrator.integrate()
        
        # Create and run the API service
        api_service = ApiService()
        
        print("Starting API service with database integration...")
        print("Press Ctrl+C to stop the service.")
        
        # Run the API service (this will block until stopped)
        api_service.run()
        
    except KeyboardInterrupt:
        print("\nStopping API service...")
    
    except Exception as e:
        logger.error(f"Error running API with integration: {str(e)}")
        print(f"Error: {str(e)}")

# For direct execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the database integration")
    parser.add_argument(
        "--run_api", 
        action="store_true",
        help="Run the API service with database integration"
    )
    parser.add_argument(
        "--run_tests", 
        action="store_true",
        help="Run the integration tests against a running API service"
    )
    
    args = parser.parse_args()
    
    if args.run_api:
        run_api_with_integration()
    elif args.run_tests:
        # Run the integration tests
        tester = DbIntegrationTest()
        tester.run_all_tests()
    else:
        print("Please specify either --run_api or --run_tests")
        print("Example:")
        print("  python test_db_integration.py --run_api")
        print("  python test_db_integration.py --run_tests") 