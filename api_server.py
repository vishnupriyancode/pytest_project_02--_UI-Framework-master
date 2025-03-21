from flask import Flask, request, jsonify
import os
import json
import pandas as pd
from flask_cors import CORS
import logging
from datetime import datetime
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "*"],
         "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
         "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With"],
         "supports_credentials": True,
         "max_age": 3600  # Cache preflight response for 1 hour
     }},
     send_wildcard=True)

# Add CORS headers to all responses for extra protection
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS,PUT,DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Configure Flask for larger requests
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max size
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/test-connection', methods=['GET', 'OPTIONS'])
def test_connection():
    """Simple endpoint to test API connection"""
    if request.method == 'OPTIONS':
        return '', 204
        
    return jsonify({
        'status': 'success',
        'message': 'API connection successful',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/process-edit', methods=['POST', 'OPTIONS'])
def process_edit():
    """Process a JSON file and record the response"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # Log request
        logger.info(f"Received process-edit request")
        
        # Extract data from request
        data = request.json
        logger.info(f"Request data: {data}")
        
        file_path = data.get('file_path')
        edit_id = data.get('edit_id')
        
        # Validate input
        if not file_path:
            logger.warning("Missing file_path parameter")
            return jsonify({"error": "Missing file_path parameter"}), 400
            
        if not edit_id:
            logger.warning("Missing edit_id parameter")
            return jsonify({"error": "Missing edit_id parameter"}), 400
        
        # Normalize path
        file_path = os.path.normpath(file_path)
        
        # Check if file exists
        if not os.path.isfile(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({"error": f"File not found: {file_path}"}), 404
        
        # Read the JSON file
        try:
            with open(file_path, 'r') as f:
                json_content = json.load(f)
            logger.info(f"Successfully loaded JSON from {file_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {str(e)}")
            return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return jsonify({"error": f"Error reading file: {str(e)}"}), 500
        
        # Process the JSON content (customize this for your specific requirements)
        # This is a simplified example - replace with your actual processing logic
        processed_result = {
            "original": json_content,
            "processed_at": datetime.now().isoformat(),
            "char_count": len(json.dumps(json_content)),
            "edit_id": edit_id
        }
        
        # Append to Excel
        excel_path = 'responses.xlsx'
        try:
            if os.path.exists(excel_path):
                df = pd.read_excel(excel_path)
            else:
                df = pd.DataFrame(columns=['file_path', 'edit_id', 'status', 'timestamp'])
                
            new_row = pd.DataFrame([{
                'file_path': file_path,
                'edit_id': edit_id,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(excel_path, index=False)
            logger.info(f"Response recorded in Excel: {excel_path}")
        except Exception as e:
            logger.error(f"Error saving to Excel: {str(e)}")
            # Continue processing even if Excel save fails
        
        # Prepare response
        result = {
            "status": "success",
            "processed_file": file_path,
            "edit_id": edit_id,
            "content_summary": f"Processed {len(json.dumps(json_content))} characters",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Processing completed successfully for {file_path}")
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/process-folder', methods=['POST', 'OPTIONS'])
def process_folder():
    """Process all JSON files in a folder"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        return response, 204
        
    try:
        # Extract data from request
        data = request.json
        logger.info(f"Received folder processing request: {data}")
        
        folder_path = data.get('folder_path')
        edit_id = data.get('edit_id', 'Folder Edit')
        
        # Validate input
        if not folder_path:
            logger.error("Missing folder_path parameter")
            return jsonify({"error": "Missing folder_path parameter"}), 400
        
        # Handle different path formats (both forward and backslashes)
        # First normalize any forward slashes to system format
        folder_path = folder_path.replace('/', os.sep)
        # Then normalize the path
        folder_path = os.path.normpath(folder_path)
        
        logger.info(f"Normalized folder path: {folder_path}")
        
        # Check if folder exists
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            
            # Try to adapt the path if it's the Edit1_jsons folder with different formats
            if "Edit1_jsons" in folder_path:
                logger.info("Folder path contains Edit1_jsons, trying alternative paths")
                # Try some common variations
                alternatives = [
                    r"C:\Cursor_Projects\pytest_project_02 -_UI Framework\Edit1_jsons",
                    r"C:\Cursor_Projects\pytest_project_02_-_UI_Framework\Edit1_jsons",
                    r"C:\Cursor_Projects\pytest_project_02-_UI_Framework\Edit1_jsons"
                ]
                
                for alt_path in alternatives:
                    if os.path.exists(alt_path):
                        logger.info(f"Found alternative path: {alt_path}")
                        folder_path = alt_path
                        break
                else:
                    # No alternatives found
                    return jsonify({
                        "status": "error",
                        "message": f"Folder not found: {folder_path}"
                    }), 404
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Folder not found: {folder_path}"
                }), 404
        
        # Find all JSON files
        json_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.json'):
                    json_files.append(os.path.join(root, file))
        
        if not json_files:
            return jsonify({
                "status": "warning",
                "message": f"No JSON files found in {folder_path}"
            })
        
        # Process each file (simplified - in a production environment, consider using threading)
        results = []
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    json_content = json.load(f)
                
                results.append({
                    "file": file_path,
                    "status": "success",
                    "char_count": len(json.dumps(json_content))
                })
            except Exception as e:
                results.append({
                    "file": file_path,
                    "status": "error",
                    "message": str(e)
                })
        
        # Compile response
        response = {
            "status": "success",
            "folder_path": folder_path,
            "edit_id": edit_id,
            "total_files": len(json_files),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error processing folder: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/process-edit1', methods=['GET', 'POST', 'OPTIONS'])
def process_edit1():
    """Process Edit1_jsons folder directly"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # Define the specific folder path
        folder_path = r"C:\Cursor_Projects\pytest_project_02 -_UI Framework\Edit1_jsons"
        edit_id = "Edit 1"
        
        logger.info(f"Processing Edit1_jsons folder: {folder_path}")
        
        # Check if folder exists
        if not os.path.exists(folder_path):
            logger.error(f"Edit1_jsons folder not found: {folder_path}")
            return jsonify({
                "status": "error",
                "message": f"Edit1_jsons folder not found: {folder_path}"
            }), 404
        
        # Find all JSON files
        json_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.json'):
                    json_files.append(os.path.join(root, file))
        
        if not json_files:
            logger.warning(f"No JSON files found in Edit1_jsons folder: {folder_path}")
            return jsonify({
                "status": "warning",
                "message": f"No JSON files found in Edit1_jsons folder"
            })
        
        # Process each file
        results = []
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    json_content = json.load(f)
                
                # Process the JSON content (simplified example)
                processed_result = {
                    "file_name": os.path.basename(file_path),
                    "processed_at": datetime.now().isoformat(),
                    "char_count": len(json.dumps(json_content)),
                    "edit_id": edit_id
                }
                
                # Append to Excel
                excel_path = 'responses.xlsx'
                try:
                    if os.path.exists(excel_path):
                        df = pd.read_excel(excel_path)
                    else:
                        df = pd.DataFrame(columns=['file_path', 'edit_id', 'status', 'timestamp'])
                        
                    new_row = pd.DataFrame([{
                        'file_path': file_path,
                        'edit_id': edit_id,
                        'status': 'success',
                        'timestamp': datetime.now().isoformat()
                    }])
                    
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_excel(excel_path, index=False)
                except Exception as e:
                    logger.error(f"Error saving to Excel: {str(e)}")
                
                results.append({
                    "file": file_path,
                    "status": "success",
                    "char_count": len(json.dumps(json_content))
                })
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
                results.append({
                    "file": file_path,
                    "status": "error",
                    "message": str(e)
                })
        
        # Compile response
        response = {
            "status": "success",
            "folder_path": folder_path,
            "edit_id": edit_id,
            "total_files": len(json_files),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }
        
        logger.info(f"Successfully processed Edit1_jsons folder with {len(json_files)} files")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error processing Edit1_jsons folder: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/process-folder', methods=['OPTIONS'])
def process_folder_preflight():
    response = jsonify({'status': 'success'})
    return response, 204

if __name__ == '__main__':
    logger.info("Starting JSON Processing API on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)

# Example usage of the API
response = requests.post(
    'http://localhost:8080/process-folder',
    json={
        'folder_path': "C:/Cursor_Projects/pytest_project_02 -_UI Framework/Edit1_jsons",
        'edit_id': "Edit 1"
    },
    headers={'Content-Type': 'application/json'}
)

print(response.status_code)
print(response.json()) 