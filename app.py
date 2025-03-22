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

# Configure CORS
CORS(app)

# Health check endpoint
@app.route('/health-check', methods=['GET', 'OPTIONS'])
def health_check():
    """Simple endpoint to check if the API is running"""
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

# Process all JSONs endpoint
@app.route('/process-all-jsons', methods=['GET', 'OPTIONS'])
def process_all_jsons():
    """Process all JSON files"""
    if request.method == 'OPTIONS':
        return '', 204
    try:
        # Your processing logic here
        return jsonify({
            "status": "success",
            "message": "Processing complete"
        })
    except Exception as e:
        logger.error(f"Error processing JSONs: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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

# Route to upload BRD document
@app.route('/upload-brd', methods=['GET', 'POST'])
def upload_brd():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file and file.filename.endswith('.doc'):
            # Save the file to a temporary location
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            # Here you would call the AI processing function
            # For now, just return a success message
            return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200
    # Serve a simple HTML form for file upload
    return '''
    <!doctype html>
    <title>Upload BRD Document</title>
    <h1>Upload BRD Document</h1>
    <form method="post" action="/upload-brd" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''

if __name__ == '__main__':
    logger.info("Starting JSON Processing API")
    app.run(host='0.0.0.0', port=5000, debug=True) 