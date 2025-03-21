import json
import os
import logging
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    filename='logs/json_reader.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JsonReader:
    """
    A class for reading and processing JSON files from a specified directory.
    """
    
    def __init__(self, directory_path: str = "json_files"):
        """
        Initialize the JsonReader with a directory path.
        
        Args:
            directory_path: Path to the directory containing JSON files.
        """
        self.directory_path = directory_path
        logger.info(f"JsonReader initialized with directory: {directory_path}")
    
    def get_json_files(self) -> List[str]:
        """
        Get a list of all JSON files in the specified directory.
        
        Returns:
            List of JSON file paths.
        """
        try:
            if not os.path.exists(self.directory_path):
                logger.error(f"Directory not found: {self.directory_path}")
                raise FileNotFoundError(f"Directory not found: {self.directory_path}")
            
            json_files = [
                os.path.join(self.directory_path, file)
                for file in os.listdir(self.directory_path)
                if file.endswith('.json')
            ]
            
            logger.info(f"Found {len(json_files)} JSON files")
            return json_files
        
        except Exception as e:
            logger.error(f"Error getting JSON files: {str(e)}")
            raise
    
    def read_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read and parse a JSON file.
        
        Args:
            file_path: Path to the JSON file.
            
        Returns:
            Dictionary containing the JSON data.
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            logger.info(f"Successfully read JSON file: {file_path}")
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in file {file_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {str(e)}")
            raise
    
    def create_request_payload(self, file_path: str, operation: str = "process_data") -> Dict[str, Any]:
        """
        Create a request payload for the API based on a JSON file.
        
        Args:
            file_path: Path to the JSON file.
            operation: The operation to perform on the data.
            
        Returns:
            Dictionary containing the request payload.
        """
        try:
            # Read the JSON file
            data = self.read_json_file(file_path)
            
            # Create the payload
            payload = {
                "file_path": file_path,
                "operation": operation,
                "data": data
            }
            
            logger.info(f"Created request payload for file: {file_path}")
            return payload
        
        except Exception as e:
            logger.error(f"Error creating request payload: {str(e)}")
            raise

# For direct execution testing
if __name__ == "__main__":
    reader = JsonReader()
    try:
        json_files = reader.get_json_files()
        for file in json_files:
            payload = reader.create_request_payload(file)
            print(f"Created payload for {file}: {payload}")
    except Exception as e:
        print(f"Error: {str(e)}")