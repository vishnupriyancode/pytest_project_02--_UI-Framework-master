from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import logging
import traceback
from datetime import datetime

# Import our modules
from json_processor import setup_logging, read_json_files, apply_edit_one
from excel_handler import save_to_excel
from config import API_PORT, API_HOST

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow requests from all origins with all methods and headers
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "*"],
         "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"],
         "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With", "Cache-Control"],
         "expose_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True,
         "max_age": 3600  # Cache preflight response for 1 hour
     }},
     send_wildcard=True)

# Additional CORS headers as a fallback
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,X-Requested-With,Cache-Control')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS,PUT,DELETE,PATCH')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Health check endpoint
@app.route('/test-connection', methods=['GET', 'OPTIONS'])
def test_connection():
    """Health check endpoint"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
        
    return jsonify({
        'status': 'success',
        'message': 'API connection successful',
        'timestamp': datetime.now().isoformat()
    })

# Process Edit endpoint
@app.route('/process-edit', methods=['POST', 'OPTIONS'])
def process_edit():
    """Process Edit1_jsons folder"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        return response, 204
    
    try:
        # Get request data
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.json
        print(f"Received data: {data}")
        
        # Get folder path and edit_id
        folder_path = data.get('folder_path')
        edit_id = data.get('edit_id', 'Edit 1')
        
        if not folder_path:
            return jsonify({
                'status': 'error',
                'message': 'Folder path is required'
            }), 400
        
        # Normalize path (handle Windows backslashes)
        folder_path = os.path.normpath(folder_path)
        
        # Check if folder exists
        if not os.path.exists(folder_path):
            return jsonify({
                'status': 'error',
                'message': f'Folder not found: {folder_path}'
            }), 404
        
        # Get JSON files in the folder
        json_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.json')]
        
        if not json_files:
            return jsonify({
                'status': 'warning',
                'message': f'No JSON files found in folder: {folder_path}'
            })
        
        # Process each JSON file
        results = []
        for filename in json_files:
            try:
                file_path = os.path.join(folder_path, filename)
                
                # Read JSON file
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                
                # Process data (add your actual processing logic here)
                processed_data = {
                    **file_data,
                    'processed': True,
                    'processed_at': datetime.now().isoformat(),
                    'edit_id': edit_id
                }
                
                # Add to results
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'data': processed_data
                })
                
            except Exception as e:
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Return results
        return jsonify({
            'status': 'success',
            'message': f'Processed {len(json_files)} files',
            'folder_path': folder_path,
            'edit_id': edit_id,
            'results': results
        })
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

# Process Custom Folder endpoint
@app.route('/process-folder', methods=['POST', 'OPTIONS'])
def process_folder():
    """Process a custom folder"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        return response, 204
    
    try:
        # Get request data
        if not request.is_json:
            logger.error("Request must be JSON")
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.json
        logger.info(f"Received data for folder processing: {data}")
        
        # Get folder path and edit_id
        folder_path = data.get('folder_path')
        edit_id = data.get('edit_id', 'Custom Edit')
        
        if not folder_path:
            logger.error("Folder path is required")
            return jsonify({
                'status': 'error',
                'message': 'Folder path is required'
            }), 400
        
        # Try multiple path formats
        original_path = folder_path
        
        # Normalize path (handle Windows backslashes)
        try:
            # First attempt with the original path
            folder_path = os.path.normpath(original_path)
            
            # Check if folder exists
            if not os.path.exists(folder_path):
                logger.warning(f"Folder not found with original path: {folder_path}")
                
                # Try replacing double backslashes with single
                if '\\\\' in original_path:
                    folder_path = os.path.normpath(original_path.replace('\\\\', '\\'))
                    logger.info(f"Trying with simplified backslashes: {folder_path}")
                    
                    if not os.path.exists(folder_path):
                        # Try with forward slashes instead
                        folder_path = original_path.replace('\\', '/').replace('//', '/')
                        folder_path = os.path.normpath(folder_path)
                        logger.info(f"Trying with forward slashes: {folder_path}")
                        
                        if not os.path.exists(folder_path):
                            logger.error(f"Folder not found after trying multiple path formats: {original_path}")
                            return jsonify({
                                'status': 'error',
                                'message': f'Folder not found after trying multiple path formats: {original_path}',
                                'attempted_paths': [original_path, folder_path]
                            }), 404
        except Exception as e:
            logger.error(f"Path normalization error: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Path normalization error: {str(e)}'
            }), 400
        
        # Get JSON files in the folder
        try:
            json_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.json')]
            logger.info(f"Found {len(json_files)} JSON files in {folder_path}")
        except PermissionError:
            logger.error(f"Permission denied accessing folder: {folder_path}")
            return jsonify({
                'status': 'error',
                'message': f'Permission denied accessing folder: {folder_path}'
            }), 403
        except Exception as e:
            logger.error(f"Error listing directory {folder_path}: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Error listing directory: {str(e)}'
            }), 500
        
        if not json_files:
            logger.warning(f"No JSON files found in folder: {folder_path}")
            return jsonify({
                'status': 'warning',
                'message': f'No JSON files found in folder: {folder_path}'
            })
        
        # Process each JSON file (simplified for this example)
        processed_count = len(json_files)
        
        # Return results
        return jsonify({
            'status': 'success',
            'message': f'Processed {processed_count} files',
            'folder_path': folder_path,
            'edit_id': edit_id,
            'files_processed': json_files
        })
        
    except Exception as e:
        print(f"Error processing folder request: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/process', methods=['POST'])
def process_json():
    """API endpoint to process incoming JSON data"""
    timestamp = datetime.now().isoformat()
    
    try:
        # Get JSON data from request
        request_data = request.get_json()
        
        if not request_data:
            logger.error("No JSON data received")
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        # Extract filename if provided, otherwise use timestamp
        filename = request_data.get('filename', f"request_{timestamp}")
        
        logger.info(f"Processing request for {filename}")
        
        # Apply the Edit 1 transformation
        processed_data = apply_edit_one(request_data)
        
        # Prepare response
        response_data = {
            'status': 'success',
            'message': 'JSON processed successfully',
            'processed_data': processed_data,
            'timestamp': timestamp
        }
        
        # Store response for Excel export
        api_responses.append({
            'filename': filename,
            'status': 'success',
            'timestamp': timestamp,
            'response_data': processed_data,
            'matches_expected': True  # This would be determined by your validation logic
        })
        
        return jsonify(response_data)
    
    except Exception as e:
        error_message = str(e)
        stack_trace = traceback.format_exc()
        logger.error(f"Error processing request: {error_message}\n{stack_trace}")
        
        # Store error response
        api_responses.append({
            'filename': request.get_json().get('filename', f"error_{timestamp}") if request.get_json() else f"error_{timestamp}",
            'status': 'error',
            'timestamp': timestamp,
            'error': error_message,
            'matches_expected': False
        })
        
        return jsonify({
            'status': 'error',
            'message': 'Failed to process JSON',
            'error': error_message
        }), 500

@app.route('/export-excel', methods=['GET'])
def export_excel():
    """Export all processed responses to Excel"""
    try:
        if not api_responses:
            return jsonify({
                'status': 'warning',
                'message': 'No responses to export'
            })
        
        excel_path = save_to_excel(api_responses)
        
        return jsonify({
            'status': 'success',
            'message': 'Responses exported to Excel',
            'excel_file': excel_path
        })
    
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error exporting to Excel: {error_message}")
        
        return jsonify({
            'status': 'error',
            'message': 'Failed to export to Excel',
            'error': error_message
        }), 500

@app.route('/process-all', methods=['GET'])
def process_all_files():
    """Process all JSON files in the specified directory"""
    try:
        # Read all JSON files
        json_files = read_json_files()
        
        if not json_files:
            return jsonify({
                'status': 'warning',
                'message': 'No JSON files found to process'
            })
        
        # Process each file
        results = []
        for json_file in json_files:
            try:
                filename = json_file['filename']
                data = json_file['data']
                
                # Apply transformation
                processed_data = apply_edit_one(data)
                
                # Store response
                timestamp = datetime.now().isoformat()
                api_responses.append({
                    'filename': filename,
                    'status': 'success',
                    'timestamp': timestamp,
                    'response_data': processed_data,
                    'matches_expected': True
                })
                
                results.append({
                    'filename': filename,
                    'status': 'success'
                })
                
                logger.info(f"Processed file: {filename}")
            
            except Exception as e:
                error_message = str(e)
                logger.error(f"Error processing file {json_file['filename']}: {error_message}")
                
                results.append({
                    'filename': json_file['filename'],
                    'status': 'error',
                    'error': error_message
                })
        
        # Export results to Excel
        excel_path = save_to_excel(api_responses)
        
        return jsonify({
            'status': 'success',
            'message': f'Processed {len(json_files)} JSON files',
            'results': results,
            'excel_file': excel_path
        })
    
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error in batch processing: {error_message}")
        
        return jsonify({
            'status': 'error',
            'message': 'Failed to process files',
            'error': error_message
        }), 500

if __name__ == '__main__':
    logger.info("Starting JSON Processing API")
    app.run(host=API_HOST, port=API_PORT, debug=True) 