"""
Test script to upload multiple JSON files in bulk to the API server.
"""

import requests
import os
import sys
import json

def create_sample_files(num_files=3):
    """Create sample JSON files for testing."""
    # Create the test_files directory if it doesn't exist
    os.makedirs('test_files', exist_ok=True)
    
    files_created = []
    
    for i in range(1, num_files + 1):
        filename = f"test_file_{i}.json"
        file_path = os.path.join('test_files', filename)
        
        # Create sample data
        data = {
            "id": f"test{i}",
            "name": f"Test JSON {i}",
            "description": f"This is test file {i} for bulk upload testing",
            "timestamp": f"2025-03-08T14:{i}0:00Z",
            "data": {
                "key1": f"value{i}",
                "key2": f"value{i}2",
                "numericValue": i * 100,
                "booleanValue": i % 2 == 0
            }
        }
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        files_created.append(file_path)
        print(f"Created file: {file_path}")
    
    return files_created

def upload_files(file_paths, api_url="http://localhost:5000/process-multiple-jsons"):
    """Upload multiple files to the API server."""
    
    # Check if files exist
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return False
    
    try:
        # Open each file and add to the files dictionary
        files_dict = {}
        for i, file_path in enumerate(file_paths):
            files_dict[f'jsonFiles'] = (
                os.path.basename(file_path),
                open(file_path, 'rb'),
                'application/json'
            )
        
        # Send the request
        print(f"Uploading {len(file_paths)} files to {api_url}...")
        
        # Since we need to keep files open for the duration of the upload,
        # we'll use a different approach
        file_tuples = []
        open_files = []
        
        for file_path in file_paths:
            f = open(file_path, 'rb')
            open_files.append(f)
            file_tuples.append(('jsonFiles', (os.path.basename(file_path), f, 'application/json')))
        
        try:
            response = requests.post(api_url, files=file_tuples)
            
            # Check the response
            if response.status_code == 200:
                print("Upload successful!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"Upload failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
        finally:
            # Close all opened files
            for f in open_files:
                f.close()
            
    except Exception as e:
        print(f"Error uploading files: {e}")
        return False

if __name__ == "__main__":
    # Create sample files if they don't exist yet
    if not os.path.exists('test_files') or len(os.listdir('test_files')) == 0:
        file_paths = create_sample_files(3)
    else:
        # Use existing files
        file_paths = [os.path.join('test_files', f) for f in os.listdir('test_files') if f.endswith('.json')]
    
    # Upload the files
    upload_files(file_paths) 