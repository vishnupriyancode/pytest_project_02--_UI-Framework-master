from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import pandas as pd
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Ensure the results directory exists
os.makedirs('results', exist_ok=True)

@app.route('/health-check', methods=['GET'])
def health_check():
    """Simple endpoint to check if the API is running"""
    return jsonify({
        "status": "healthy",
        "message": "API server is running properly",
        "server": "Flask API Service",
        "version": "1.0.0"
    })

@app.route('/process-edit', methods=['POST'])
def process_edit():
    """
    Process a JSON edit request with file path(s)
    
    Accepts:
    - single file_path
    - multiple file_paths in an array
    """
    try:
        logger.info("Received process-edit request")
        data = request.json
        
        if not data:
            logger.error("No JSON data in request")
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        # Get file path(s) from the request
        file_path = data.get('file_path')
        file_paths = data.get('file_paths', [])
        edit_id = data.get('edit_id', 'Edit 1')
        
        # Validate input
        if not file_path and not file_paths:
            logger.error("No file_path or file_paths provided")
            return jsonify({
                "status": "error",
                "message": "Either file_path or file_paths parameter is required"
            }), 400
        
        # Process single file
        if file_path:
            logger.info(f"Processing single file: {file_path}")
            
            # Check if file exists
            if not os.path.isfile(file_path):
                logger.error(f"File not found: {file_path}")
                return jsonify({
                    "status": "error",
                    "message": f"File not found at path: {file_path}"
                }), 404
            
            # Load and parse JSON file
            try:
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                
                # Process the file (for demo just return success)
                processed_data = {
                    "input": json_data,
                    "edit_id": edit_id,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Success",
                    "file_path": file_path
                }
                
                # Save to Excel
                save_to_excel(processed_data)
                
                return jsonify({
                    "status": "success",
                    "message": "Edit is working properly",
                    "edit_id": edit_id,
                    "processed": True
                }), 200
                
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON file: {file_path}")
                return jsonify({
                    "status": "error",
                    "message": f"Invalid JSON format in file: {file_path}"
                }), 400
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": f"Error processing file: {str(e)}"
                }), 500
        
        # Process multiple files
        else:
            logger.info(f"Processing multiple files: {file_paths}")
            
            if not isinstance(file_paths, list) or len(file_paths) == 0:
                logger.error("Invalid file_paths parameter")
                return jsonify({
                    "status": "error",
                    "message": "file_paths must be a non-empty list"
                }), 400
            
            results = []
            success_count = 0
            error_count = 0
            
            for index, path in enumerate(file_paths):
                try:
                    # Check if file exists
                    if not os.path.isfile(path):
                        logger.warning(f"File not found: {path}")
                        results.append({
                            "file_path": path,
                            "status": "error",
                            "message": f"File not found at path: {path}"
                        })
                        error_count += 1
                        continue
                    
                    # Load and parse JSON file
                    with open(path, 'r') as f:
                        json_data = json.load(f)
                    
                    # Process file (demo just returns success)
                    file_edit_id = f"{edit_id}_{index + 1}" if len(file_paths) > 1 else edit_id
                    processed_data = {
                        "input": json_data,
                        "edit_id": file_edit_id,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "Success",
                        "file_path": path
                    }
                    
                    # Save to Excel
                    save_to_excel(processed_data)
                    
                    results.append({
                        "file_path": path,
                        "status": "success",
                        "edit_id": file_edit_id
                    })
                    success_count += 1
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON file: {path}")
                    results.append({
                        "file_path": path,
                        "status": "error",
                        "message": f"Invalid JSON format in file: {path}"
                    })
                    error_count += 1
                except Exception as e:
                    logger.error(f"Error processing file: {str(e)}")
                    results.append({
                        "file_path": path,
                        "status": "error",
                        "message": str(e)
                    })
                    error_count += 1
            
            return jsonify({
                "status": "success" if error_count == 0 else "partial",
                "message": "Edit processing completed",
                "summary": {
                    "total": len(file_paths),
                    "success": success_count,
                    "error": error_count
                },
                "edit_id": edit_id,
                "results": results,
                "processed": True
            }), 200
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

def save_to_excel(processed_data):
    """Save processed data to Excel file"""
    excel_path = os.path.join('results', 'api_responses.xlsx')
    
    try:
        # Check if Excel file exists
        if os.path.exists(excel_path):
            # Read existing Excel
            try:
                df = pd.read_excel(excel_path, sheet_name="Processed JSON")
            except:
                # If sheet doesn't exist, create new DataFrame
                df = pd.DataFrame(columns=["edit_id", "timestamp", "status", "json_input", "response"])
        else:
            # Create new DataFrame
            df = pd.DataFrame(columns=["edit_id", "timestamp", "status", "json_input", "response"])
        
        # Convert data to JSON strings
        json_input = json.dumps(processed_data["input"], indent=2)
        response = json.dumps({"message": "Edit is working properly"}, indent=2)
        
        # Create new row
        new_row = {
            "edit_id": processed_data["edit_id"],
            "timestamp": processed_data["timestamp"],
            "status": processed_data["status"],
            "json_input": json_input,
            "response": response
        }
        
        # Append new row to DataFrame
        df_new_row = pd.DataFrame([new_row])
        df = pd.concat([df, df_new_row], ignore_index=True)
        
        # Write to Excel
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, sheet_name="Processed JSON", index=False)
        
        logger.info(f"Saved data to Excel: {excel_path}")
        
    except Exception as e:
        logger.error(f"Error saving to Excel: {str(e)}")
        raise

if __name__ == '__main__':
    logger.info("Starting API server on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True) 