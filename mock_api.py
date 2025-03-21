from flask import Flask, request, jsonify
import time
import random
import logging
import os
from datetime import datetime
import json
from flask_cors import CORS

# Configure app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes and origins

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"mock_api_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def index():
    """Root endpoint for health check"""
    return jsonify({
        'status': 'success',
        'message': 'Mock API server is running',
        'version': '1.0.0'
    })

@app.route('/process-folder', methods=['POST'])
def process_folder():
    """Endpoint to process all JSON files in a folder"""
    try:
        # Get the request data
        data = request.json
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        # Check if folder path is provided
        folder_path = data.get('folder_path')
        edit_id = data.get('edit_id', 'Edit 1')  # Default to Edit 1 if not specified
        
        if not folder_path:
            logger.error("No folder path provided")
            return jsonify({
                'status': 'error',
                'message': 'No folder path provided'
            }), 400
        
        logger.info(f"Processing all JSON files in folder: {folder_path}")
        
        # Check if folder exists
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return jsonify({
                'status': 'error',
                'message': f'Folder not found: {folder_path}'
            }), 404
        
        # Get all JSON files in the folder
        json_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                     if f.lower().endswith('.json')]
        
        if not json_files:
            logger.warning(f"No JSON files found in folder: {folder_path}")
            return jsonify({
                'status': 'warning',
                'message': f'No JSON files found in folder: {folder_path}'
            })
        
        logger.info(f"Found {len(json_files)} JSON files in folder")
        
        # Process each JSON file
        results = []
        for file_path in json_files:
            try:
                # Read the JSON file
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                
                # Process the data
                processed_data = process_data(file_data)
                
                # Add to results
                results.append({
                    'file_name': os.path.basename(file_path),
                    'status': 'success',
                    'data': processed_data
                })
                
                logger.info(f"Successfully processed file: {os.path.basename(file_path)}")
                
            except Exception as e:
                logger.error(f"Error processing file {os.path.basename(file_path)}: {str(e)}")
                results.append({
                    'file_name': os.path.basename(file_path),
                    'status': 'error',
                    'error': str(e)
                })
        
        # Return consolidated response
        successful = sum(1 for r in results if r['status'] == 'success')
        
        return jsonify({
            'status': 'success',
            'message': f'Processed {len(results)} files from folder',
            'folder_path': folder_path,
            'edit_id': edit_id,
            'total_files': len(results),
            'successful': successful,
            'failed': len(results) - successful,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing folder: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error processing folder',
            'error': str(e)
        }), 500

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_json():
    """Main endpoint for processing JSON data"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # Get the request data
        data = request.json
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        # Check if this is a folder processing request
        if 'folder_path' in data:
            return process_folder()
            
        # Log received data size
        data_size = len(str(data))
        logger.info(f"Received request with data size: {data_size} bytes")
        
        # Check if this is a chunk
        if isinstance(data, dict) and 'chunk_info' in data:
            logger.info(f"Processing chunk {data['chunk_info'].get('chunk_index', 'unknown')}/{data['chunk_info'].get('total_chunks', 'unknown')}")
            # Add artificial delay for large chunks to simulate processing time
            time.sleep(random.uniform(0.5, 2.0))
        
        # Apply processing transformation
        processed_data = process_data(data)
        
        # Return the processed data
        return jsonify({
            'status': 'success',
            'message': 'Data processed successfully',
            'processed_data': processed_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error processing request',
            'error': str(e)
        }), 500

@app.route('/process-edit', methods=['POST', 'OPTIONS'])
def process_edit():
    """Specific endpoint for processing Edit1_jsons folder"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # Get the request data
        data = request.json
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        # Default edit_id if not provided
        edit_id = data.get('edit_id', 'Edit 1')
        
        # Get the Edit1_jsons folder path (either from request or default)
        folder_path = data.get('folder_path')
        if not folder_path:
            # Try to find the default Edit1_jsons folder
            script_dir = os.path.dirname(os.path.abspath(__file__))
            folder_path = os.path.join(script_dir, "Edit1_jsons")
            if not os.path.exists(folder_path):
                logger.error(f"Edit1_jsons folder not found at {folder_path}")
                return jsonify({
                    'status': 'error',
                    'message': 'Edit1_jsons folder not found and no alternative folder_path provided'
                }), 404
        
        logger.info(f"Processing Edit1_jsons with edit_id: {edit_id} from folder: {folder_path}")
        
        # Get all JSON files in the folder
        json_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                     if f.lower().endswith('.json')]
        
        if not json_files:
            logger.warning(f"No JSON files found in folder: {folder_path}")
            return jsonify({
                'status': 'warning',
                'message': f'No JSON files found in folder: {folder_path}'
            })
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        # Process each JSON file
        results = []
        for file_path in json_files:
            try:
                # Read the JSON file
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                
                # Process the data
                processed_data = process_data(file_data)
                
                # Add to results
                results.append({
                    'file_name': os.path.basename(file_path),
                    'status': 'success',
                    'data': processed_data
                })
                
                logger.info(f"Successfully processed file: {os.path.basename(file_path)}")
                
            except Exception as e:
                logger.error(f"Error processing file {os.path.basename(file_path)}: {str(e)}")
                results.append({
                    'file_name': os.path.basename(file_path),
                    'status': 'error',
                    'error': str(e)
                })
        
        # Return consolidated response
        successful = sum(1 for r in results if r['status'] == 'success')
        
        return jsonify({
            'status': 'success',
            'message': f'Processed {len(results)} files with Edit 1',
            'folder_path': folder_path,
            'edit_id': edit_id,
            'total_files': len(results),
            'successful': successful,
            'failed': len(results) - successful,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing Edit1_jsons: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error processing Edit1_jsons folder',
            'error': str(e)
        }), 500

@app.route('/test-connection', methods=['GET', 'OPTIONS'])
def test_connection():
    """Test endpoint to verify API connectivity"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
        
    return jsonify({
        'status': 'success',
        'message': 'API connection successful',
        'timestamp': datetime.now().isoformat()
    })

def process_data(data):
    """Apply a transformation to the data"""
    # If this is already a chunk, process it
    if isinstance(data, dict) and 'chunk_info' in data:
        # Keep the chunk info
        result = data.copy()
        
        # Process the data based on structure
        if 'data' in result and isinstance(result['data'], list):
            # Process each item in the list
            for item in result['data']:
                if isinstance(item, dict):
                    item['processed'] = True
                    item['processed_at'] = datetime.now().isoformat()
        
        # Add processing metadata
        result['processed'] = True
        result['processed_at'] = datetime.now().isoformat()
        return result
    
    # Handle other data structures
    if isinstance(data, dict):
        # Make a copy to avoid modifying the original
        result = data.copy()
        
        # Add processing metadata
        result['processed'] = True
        result['processed_at'] = datetime.now().isoformat()
        
        # Process nested dictionaries
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = process_data(value)
            elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
                # Process list of dictionaries
                result[key] = [process_data(item) for item in value]
        
        return result
    
    elif isinstance(data, list):
        # Process each item in the list
        return [process_data(item) if isinstance(item, dict) else item for item in data]
    
    else:
        # Return primitive types as is
        return data

if __name__ == '__main__':
    port = 5000
    logger.info(f"Starting mock API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 