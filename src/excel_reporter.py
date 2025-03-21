import pandas as pd
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    filename='logs/excel_reporter.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExcelReporter:
    """
    A class for saving API responses to an Excel spreadsheet.
    """
    
    def __init__(self, output_file: str = "results/api_responses.xlsx"):
        """
        Initialize the ExcelReporter with an output file path.
        
        Args:
            output_file: Path to the Excel output file.
        """
        self.output_file = output_file
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Initialize data structure
        self.data = {
            "Timestamp": [],
            "Input JSON": [],
            "API Response": [],
            "Expected Result": [],
            "Status": []
        }
        
        logger.info(f"ExcelReporter initialized with output file: {output_file}")
    
    def add_response(self, 
                    input_json: str, 
                    api_response: Dict[str, Any], 
                    expected_result: str = "Success"):
        """
        Add an API response to the Excel data.
        
        Args:
            input_json: The path to the input JSON file.
            api_response: The API response dictionary.
            expected_result: The expected result of the API call.
        """
        try:
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add data to the structure
            self.data["Timestamp"].append(timestamp)
            self.data["Input JSON"].append(input_json)
            self.data["API Response"].append(json.dumps(api_response))
            self.data["Expected Result"].append(expected_result)
            
            # Check if the API response matches the expected result
            status = "Success" if api_response.get("status") == "success" else "Failure"
            self.data["Status"].append(status)
            
            logger.info(f"Added response for {input_json} with status {status}")
        
        except Exception as e:
            logger.error(f"Error adding response: {str(e)}")
            raise
    
    def save_to_excel(self):
        """
        Save the collected data to an Excel spreadsheet.
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(self.data)
            
            # Save to Excel
            df.to_excel(self.output_file, index=False)
            
            logger.info(f"Saved data to Excel file: {self.output_file}")
            return self.output_file
        
        except Exception as e:
            logger.error(f"Error saving to Excel: {str(e)}")
            raise
    
    def append_to_excel(self):
        """
        Append the collected data to an existing Excel spreadsheet,
        or create a new one if it doesn't exist.
        """
        try:
            # Check if file exists
            if os.path.exists(self.output_file):
                # Read existing data
                existing_df = pd.read_excel(self.output_file)
                
                # Convert current data to DataFrame
                new_df = pd.DataFrame(self.data)
                
                # Combine data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                
                # Save to Excel
                combined_df.to_excel(self.output_file, index=False)
                
                logger.info(f"Appended data to existing Excel file: {self.output_file}")
            else:
                # If file doesn't exist, just save new data
                self.save_to_excel()
            
            return self.output_file
        
        except Exception as e:
            logger.error(f"Error appending to Excel: {str(e)}")
            raise

# For direct execution testing
if __name__ == "__main__":
    reporter = ExcelReporter()
    
    # Add a sample response
    reporter.add_response(
        input_json="C:\\json_files\\example.json",
        api_response={
            "status": "success",
            "message": "Edit is working properly",
            "data": {"example": "data"}
        },
        expected_result="Success"
    )
    
    # Save to Excel
    output_file = reporter.save_to_excel()
    print(f"Saved to Excel file: {output_file}") 