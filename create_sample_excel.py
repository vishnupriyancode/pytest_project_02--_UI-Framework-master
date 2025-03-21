"""
Create a sample Excel file for testing the download functionality.
"""

import pandas as pd
import os
from datetime import datetime

def create_sample_excel():
    """Create a sample Excel file with test data."""
    # Create the results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    # Sample data
    data = {
        "Timestamp": [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ],
        "Input JSON": [
            "C:\\json_files\\example1.json",
            "C:\\json_files\\example2.json",
            "C:\\json_files\\example3.json"
        ],
        "API Response": [
            '{"status": "success", "message": "Edit is working properly", "data": {"example": "data1"}}',
            '{"status": "error", "message": "Invalid data", "data": {"example": "data2"}}',
            '{"status": "success", "message": "Edit is working properly", "data": {"example": "data3"}}'
        ],
        "Expected Result": [
            "Success",
            "Success",
            "Success"
        ],
        "Status": [
            "Success",
            "Failed",
            "Success"
        ]
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel
    excel_path = os.path.join('results', 'api_responses.xlsx')
    df.to_excel(excel_path, index=False)
    
    print(f"Created sample Excel file at: {excel_path}")
    
    # Create individual reports
    for i in range(1, 4):
        # Filter for the specific ID
        filtered_df = df[df['Input JSON'].str.contains(f"example{i}.json")]
        
        # Save to the output path
        individual_path = os.path.join('results', f'report_{i}.xlsx')
        filtered_df.to_excel(individual_path, index=False)
        
        print(f"Created individual report for ID {i} at: {individual_path}")

if __name__ == "__main__":
    create_sample_excel() 