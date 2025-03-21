import pandas as pd
import json
import logging
from config import EXCEL_OUTPUT

logger = logging.getLogger(__name__)

def save_to_excel(responses):
    """
    Save API responses to Excel file
    
    Args:
        responses: List of dictionaries containing response data
    """
    try:
        # Prepare data for Excel
        excel_data = []
        
        for response in responses:
            # Extract basic info
            row = {
                'Filename': response.get('filename', 'Unknown'),
                'Status': response.get('status', 'Unknown'),
                'Timestamp': response.get('timestamp', 'Unknown'),
            }
            
            # Handle response data - flattening complex JSON objects
            response_data = response.get('response_data', {})
            if isinstance(response_data, dict):
                # Flatten first level of response data
                for key, value in response_data.items():
                    if isinstance(value, (dict, list)):
                        row[key] = json.dumps(value)  # Serialize complex objects
                    else:
                        row[key] = value
            
            # Add expected result comparison
            row['Matches_Expected'] = response.get('matches_expected', False)
            
            excel_data.append(row)
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(excel_data)
        df.to_excel(EXCEL_OUTPUT, index=False)
        
        logger.info(f"Saved responses to Excel file: {EXCEL_OUTPUT}")
        return EXCEL_OUTPUT
    
    except Exception as e:
        logger.error(f"Error saving to Excel: {str(e)}")
        raise 