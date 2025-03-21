import os
import sys
import logging
import json
import time
from typing import List, Dict, Any, Optional
import threading

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the modules
from json_reader import JsonReader
from api_service import ApiService
from api_client import ApiClient
from excel_reporter import ExcelReporter

# Configure logging
logging.basicConfig(
    filename='logs/workflow.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

class JsonProcessingWorkflow:
    """
    A workflow for processing JSON files and sending them to an API.
    """
    
    def __init__(self, 
                json_dir: str = "C:\\json_files\\", 
                output_excel: str = "results/api_responses.xlsx"):
        """
        Initialize the workflow.
        
        Args:
            json_dir: Path to the directory containing JSON files.
            output_excel: Path to the Excel output file.
        """
        self.json_dir = json_dir
        self.output_excel = output_excel
        
        # Create instances of the required components
        self.json_reader = JsonReader(directory_path=json_dir)
        self.api_client = ApiClient()
        self.excel_reporter = ExcelReporter(output_file=output_excel)
        
        # Create the API service, but don't start it yet
        self.api_service = ApiService()
        self.api_thread = None
        
        logger.info(f"Workflow initialized with JSON directory: {json_dir}")
    
    def start_api_service(self):
        """Start the API service in a separate thread."""
        try:
            self.api_thread = threading.Thread(target=self.api_service.run)
            self.api_thread.daemon = True
            self.api_thread.start()
            
            # Wait for the API to start up
            time.sleep(2)
            
            logger.info("API service started in a separate thread")
        
        except Exception as e:
            logger.error(f"Error starting API service: {str(e)}")
            raise
    
    def process_json_files(self):
        """
        Process all JSON files in the specified directory.
        """
        try:
            # Get all JSON files
            json_files = self.json_reader.get_json_files()
            
            if not json_files:
                logger.warning(f"No JSON files found in {self.json_dir}")
                return
            
            logger.info(f"Found {len(json_files)} JSON files to process")
            
            # Process each file
            for file_path in json_files:
                self.process_single_file(file_path)
            
            # Save the results to Excel
            output_file = self.excel_reporter.save_to_excel()
            logger.info(f"All results saved to Excel file: {output_file}")
            
            return output_file
        
        except Exception as e:
            logger.error(f"Error in workflow: {str(e)}")
            raise
    
    def process_single_file(self, file_path: str):
        """
        Process a single JSON file.
        
        Args:
            file_path: Path to the JSON file.
        """
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Create request payload
            payload = self.json_reader.create_request_payload(file_path)
            
            # Make API request
            response = self.api_client.process_json(payload)
            
            # Add to Excel reporter
            self.excel_reporter.add_response(
                input_json=file_path,
                api_response=response,
                expected_result="Success"
            )
            
            logger.info(f"Successfully processed file: {file_path}")
            return response
        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            
            # Add error to Excel reporter
            self.excel_reporter.add_response(
                input_json=file_path,
                api_response={"status": "error", "message": str(e)},
                expected_result="Success"
            )
            
            # Re-raise the exception
            raise

def run_workflow():
    """Run the complete workflow."""
    try:
        # Create the workflow
        workflow = JsonProcessingWorkflow()
        
        # Start the API service
        workflow.start_api_service()
        
        # Process all JSON files
        output_file = workflow.process_json_files()
        
        print(f"Workflow completed successfully. Results saved to: {output_file}")
        
        return output_file
    
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        print(f"Error: {str(e)}")
        return None

# For direct execution
if __name__ == "__main__":
    run_workflow()