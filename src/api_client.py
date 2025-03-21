import requests
import json
import logging
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    filename='logs/api_client.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ApiClient:
    """
    A client for making requests to the API.
    """
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server.
        """
        self.base_url = base_url
        logger.info(f"ApiClient initialized with base URL: {base_url}")
    
    def process_json(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the process-json endpoint.
        
        Args:
            payload: The JSON payload to send.
            
        Returns:
            The API response.
        """
        try:
            url = f"{self.base_url}/process-json"
            logger.info(f"Making POST request to {url} with payload: {payload}")
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            
            # Check for successful response
            response.raise_for_status()
            
            # Parse the JSON response
            json_response = response.json()
            logger.info(f"Received response: {json_response}")
            
            return json_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making API request: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing API response: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in API client: {str(e)}")
            raise
    
    def save_response_to_file(self, response: Dict[str, Any], output_file: str):
        """
        Save an API response to a file.
        
        Args:
            response: The API response.
            output_file: Path to the output file.
        """
        try:
            with open(output_file, 'w') as file:
                json.dump(response, file, indent=4)
            
            logger.info(f"Saved API response to file: {output_file}")
        
        except Exception as e:
            logger.error(f"Error saving API response to file: {str(e)}")
            raise

# For direct execution testing
if __name__ == "__main__":
    client = ApiClient()
    
    # Create a sample payload
    payload = {
        "file_path": "C:\\json_files\\example.json",
        "operation": "process_data",
        "data": {
            "id": 1,
            "name": "Example Data",
            "description": "This is a sample JSON file for testing"
        }
    }
    
    try:
        # Make a request
        response = client.process_json(payload)
        print(f"API Response: {response}")
        
        # Save the response to a file
        client.save_response_to_file(response, "results/sample_response.json")
    
    except Exception as e:
        print(f"Error: {str(e)}") 