import os
import json
import logging
from config import JSON_FILES_DIR

logger = logging.getLogger(__name__)

def setup_logging():
    """Configure logging based on settings in config.py"""
    from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL
    logging.basicConfig(
        filename=LOG_FILE,
        level=LOG_LEVEL,
        format=LOG_FORMAT
    )
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(LOG_LEVEL)
    console.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger('').addHandler(console)

def read_json_files():
    """Read all JSON files from the specified directory"""
    json_data = []
    try:
        for filename in os.listdir(JSON_FILES_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(JSON_FILES_DIR, filename)
                logger.info(f"Processing file: {file_path}")
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        json_data.append({
                            'filename': filename,
                            'data': data
                        })
                    logger.info(f"Successfully processed: {filename}")
                except Exception as e:
                    logger.error(f"Error processing {filename}: {str(e)}")
    except Exception as e:
        logger.error(f"Error accessing directory {JSON_FILES_DIR}: {str(e)}")
    
    return json_data

def apply_edit_one(json_data):
    """
    Apply the "Edit 1" transformation to JSON data
    This is a placeholder - replace with your actual transformation logic
    """
    if not json_data:
        return json_data
        
    # Example transformation: add a timestamp and processing flag
    from datetime import datetime
    
    transformed_data = json_data.copy()
    transformed_data['processed'] = True
    transformed_data['processed_at'] = datetime.now().isoformat()
    
    # If the JSON contains a 'data' field that's a list, process each item
    if 'data' in transformed_data and isinstance(transformed_data['data'], list):
        for item in transformed_data['data']:
            if isinstance(item, dict):
                item['modified'] = True
    
    logger.info("Applied 'Edit 1' transformation to JSON data")
    return transformed_data

def generate_postman_request_bodies():
    """Generate request bodies for Postman from the JSON files"""
    json_files = read_json_files()
    postman_requests = []
    
    for json_file in json_files:
        # Apply transformation before generating request body
        transformed_data = apply_edit_one(json_file['data'])
        
        request = {
            'url': 'http://localhost:5000/process',  # Adjust based on your API
            'method': 'POST',
            'header': [
                {
                    'key': 'Content-Type',
                    'value': 'application/json'
                }
            ],
            'body': {
                'mode': 'raw',
                'raw': json.dumps(transformed_data, indent=2)
            },
            'description': f"Request generated from {json_file['filename']}"
        }
        
        postman_requests.append({
            'filename': json_file['filename'],
            'request': request
        })
    
    logger.info(f"Generated {len(postman_requests)} Postman request bodies")
    return postman_requests 