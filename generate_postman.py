import os
import json
import uuid
import datetime

def generate_postman_collection(json_files, output_path):
    """Generate a Postman collection for testing the JSON processing API"""
    # Create collection structure
    collection = {
        "info": {
            "_postman_id": str(uuid.uuid4()),
            "name": "JSON Edit Processing Collection",
            "description": "Automatically generated collection for JSON editing",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }
    
    # Add connection test request
    connection_test = {
        "name": "Test API Connection",
        "request": {
            "method": "GET",
            "header": [],
            "url": {
                "raw": "http://localhost:5000/test-connection",
                "protocol": "http",
                "host": ["localhost"],
                "port": "5000",
                "path": ["test-connection"]
            },
            "description": "Tests if the API server is running and accessible"
        }
    }
    collection["item"].append(connection_test)
    
    # Add request for each JSON file
    file_requests = []
    for file_path in json_files:
        item = {
            "name": f"Process {os.path.basename(file_path)}",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "file_path": file_path,
                        "edit_id": "Edit 1"
                    }, indent=2)
                },
                "url": {
                    "raw": "http://localhost:5000/process-edit",
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "5000",
                    "path": ["process-edit"]
                },
                "description": f"Process the JSON file at {file_path}"
            }
        }
        file_requests.append(item)
    
    # Add a folder process request
    if json_files:
        # Get the directory of the first JSON file
        sample_dir = os.path.dirname(json_files[0])
        folder_request = {
            "name": "Process Entire Folder",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "folder_path": sample_dir,
                        "edit_id": "Folder Edit"
                    }, indent=2)
                },
                "url": {
                    "raw": "http://localhost:5000/process-folder",
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "5000",
                    "path": ["process-folder"]
                },
                "description": f"Process all JSON files in the folder: {sample_dir}"
            }
        }
        file_requests.append(folder_request)
    
    # Create a folder for all file processing requests
    files_folder = {
        "name": "Process Individual Files",
        "item": file_requests
    }
    collection["item"].append(files_folder)
    
    # Write collection to file
    with open(output_path, 'w') as f:
        json.dump(collection, f, indent=2)
    
    print(f"✅ Postman collection generated at: {output_path}")
    print(f"   Contains {len(json_files)} individual file requests and 1 folder processing request")

def main():
    """Generate a Postman collection for all JSON files in the specified directory"""
    print("\n📝 Postman Collection Generator\n")
    
    # Get source directory from environment or use default
    source_dir = os.environ.get('JSON_SOURCE_DIR', r"C:\Cursor_Projects\pytest_project_02 -_UI Framework\Edit1_jsons")
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"❌ Source directory does not exist: {source_dir}")
        return
    
    # Find all JSON files in the directory
    json_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.json'):
                json_files.append(os.path.join(root, file))
    
    if not json_files:
        print(f"❌ No JSON files found in {source_dir}")
        return
    
    print(f"✅ Found {len(json_files)} JSON files")
    
    # Generate timestamp for the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate the collection
    output_file = f"JSON_Edit_Collection_{timestamp}.postman_collection.json"
    generate_postman_collection(json_files, output_file)
    
    print("\n📝 Collection generation completed.")

if __name__ == "__main__":
    main() 