"""
Test script to upload a sample JSON file to the API server.
"""

import requests
import os
import sys

def upload_file(file_path, api_url="http://localhost:5000/upload-json"):
    """Upload a file to the API server."""
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    try:
        # Open the file
        with open(file_path, 'rb') as f:
            # Create a multipart form with the file
            files = {'file': (os.path.basename(file_path), f, 'application/json')}
            
            # Send the request
            print(f"Uploading file {file_path} to {api_url}...")
            response = requests.post(api_url, files=files)
            
            # Check the response
            if response.status_code == 200:
                print("Upload successful!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"Upload failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False

if __name__ == "__main__":
    # Use the provided file path or default to sample.json
    file_path = sys.argv[1] if len(sys.argv) > 1 else "sample.json"
    upload_file(file_path) 