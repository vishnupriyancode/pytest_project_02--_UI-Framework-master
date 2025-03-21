from flask import Flask, request, jsonify, send_file
import logging
import os
from typing import Dict, Any, Optional, Tuple
import json
import copy
from flask_cors import CORS
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(
    filename='logs/api_service.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ApiService:
    """
    API service for processing JSON data and handling HTTP requests.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        """
        Initialize the API service.
        
        Args:
            host: Host address for the API server.
            port: Port number for the API server.
        """
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        
        # Enable CORS with more permissive settings
        CORS(
            self.app, 
            resources={r"/*": {
                "origins": "*",
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
            }},
            supports_credentials=True
        )
        
        # Handle OPTIONS requests for all routes
        self.app.before_request(self.handle_options_request)
        
        self.setup_routes()
        logger.info(f"ApiService initialized with host={host}, port={port}")
    
    def handle_options_request(self):
        """Handle OPTIONS requests for CORS preflight."""
        if request.method == "OPTIONS":
            response = self.app.make_default_options_response()
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
            return response
        return None
    
    def setup_routes(self):
        """Set up the API routes."""
        self.app.route('/process-json', methods=['POST'])(self.process_json)
        self.app.route('/health-check', methods=['GET'])(self.health_check)
        self.app.route('/download-excel/<id>', methods=['GET'])(self.download_excel)
        self.app.route('/processed-jsons', methods=['GET'])(self.get_processed_jsons)
        self.app.route('/download-excel/all', methods=['GET'])(self.download_all_excel)
        self.app.route('/upload-json', methods=['POST'])(self.upload_json)
        self.app.route('/process-multiple-jsons', methods=['POST', 'OPTIONS'])(self.process_multiple_jsons)
        
        # New route for processing edits from local JSON files
        self.app.route('/process-edit', methods=['POST'])(self.process_edit)
        logger.info("API routes configured")
    
    def health_check(self):
        """
        Health check endpoint.
        
        Returns:
            JSON response with health status.
        """
        try:
            return jsonify({
                "status": "healthy",
                "message": "API server is running properly",
                "server": "Flask API Service",
                "version": "1.0.0"
            }), 200
        except Exception as e:
            logger.error(f"Error in health check: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Health check failed: {str(e)}"
            }), 500
    
    def download_excel(self, id):
        """
        Download Excel report for a specific processed JSON.
        
        Args:
            id: ID of the processed JSON.
            
        Returns:
            Excel file as attachment.
        """
        try:
            logger.info(f"Received request to download Excel report for ID: {id}")
            
            # Check if the ID is valid
            if not id:
                logger.error("No ID provided for Excel download")
                return jsonify({
                    "status": "error",
                    "message": "No ID provided"
                }), 400
            
            # Path to the Excel file
            if id == 'all':
                excel_path = os.path.join('results', 'api_responses.xlsx')
            else:
                excel_path = os.path.join('results', f'report_{id}.xlsx')
            
            # Get absolute path
            abs_excel_path = os.path.abspath(excel_path)
            
            # Check if the file exists
            if not os.path.exists(abs_excel_path):
                # If specific file doesn't exist, try to create it from the main Excel file
                try:
                    self.generate_individual_report(id, abs_excel_path)
                except Exception as e:
                    logger.error(f"Failed to generate report for ID {id}: {str(e)}")
                    return jsonify({
                        "status": "error",
                        "message": f"Report not found and could not be generated: {str(e)}"
                    }), 404
            
            # Send the file
            logger.info(f"Sending Excel file: {abs_excel_path}")
            return send_file(
                abs_excel_path,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"report_{id}.xlsx"
            )
            
        except Exception as e:
            logger.error(f"Error downloading Excel report: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error downloading report: {str(e)}"
            }), 500
    
    def generate_individual_report(self, id, output_path):
        """
        Generate an individual report for a specific ID.
        
        Args:
            id: ID of the processed JSON.
            output_path: Path to save the Excel file.
        """
        # Main Excel file path
        main_excel_path = os.path.join('results', 'api_responses.xlsx')
        
        # Check if the main file exists
        if not os.path.exists(main_excel_path):
            raise FileNotFoundError(f"Main Excel file not found: {main_excel_path}")
        
        # Read the main Excel file
        df = pd.read_excel(main_excel_path)
        
        # Filter for the specific ID
        filtered_df = df[df['Input JSON'].str.contains(f"example{id}.json")]
        
        # Check if any rows were found
        if filtered_df.empty:
            raise ValueError(f"No data found for ID: {id}")
        
        # Save to the output path
        filtered_df.to_excel(output_path, index=False)
        logger.info(f"Generated individual report for ID {id} at {output_path}")
    
    def download_all_excel(self):
        """
        Download Excel report for all processed JSONs.
        
        Returns:
            Excel file as attachment.
        """
        return self.download_excel('all')
    
    def get_processed_jsons(self):
        """
        Get list of processed JSON files.
        
        Returns:
            JSON response with list of processed JSON files.
        """
        try:
            # Path to the results directory
            results_dir = 'results'
            
            # Check if the directory exists
            if not os.path.exists(results_dir):
                logger.warning(f"Results directory not found: {results_dir}")
                return jsonify([]), 200
            
            # Get the main Excel file
            excel_path = os.path.join(results_dir, 'api_responses.xlsx')
            
            # Check if the file exists
            if not os.path.exists(excel_path):
                logger.warning(f"Excel file not found: {excel_path}")
                return jsonify([]), 200
            
            # Read the Excel file
            df = pd.read_excel(excel_path)
            
            # Extract the processed JSONs
            processed_jsons = []
            for index, row in df.iterrows():
                # Extract the filename from the path
                file_path = row['Input JSON']
                file_name = os.path.basename(file_path)
                
                # Extract the ID from the filename
                id = file_name.replace('example', '').replace('.json', '')
                
                # Create a record
                record = {
                    'id': id,
                    'file_name': file_name,
                    'timestamp': row['Timestamp'],
                    'status': row['Status']
                }
                
                processed_jsons.append(record)
            
            logger.info(f"Returning {len(processed_jsons)} processed JSON records")
            return jsonify(processed_jsons), 200
            
        except Exception as e:
            logger.error(f"Error getting processed JSONs: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error getting processed JSONs: {str(e)}"
            }), 500
    
    def process_json(self):
        """
        Process a JSON request.
        
        Returns:
            JSON response with status and message.
        """
        try:
            # Check if the request has the correct content type
            if not request.is_json:
                logger.error("Request Content-Type is not application/json")
                return jsonify({
                    "status": "error",
                    "message": "Content-Type must be application/json"
                }), 400
                
            # Get the JSON data from the request
            data = request.get_json()
            if not data:
                logger.error("No JSON data received in request")
                return jsonify({
                    "status": "error",
                    "message": "No JSON data received"
                }), 400
            
            logger.info(f"Received JSON request: {data}")
            
            # Extract the file path and operation
            file_path = data.get('file_path')
            operation = data.get('operation', 'process_data')
            json_data = data.get('data', {})
            
            if not file_path:
                logger.error("No file_path provided in request")
                return jsonify({
                    "status": "error",
                    "message": "No file_path provided"
                }), 400
            
            # Process the data with Edit 1 feature
            processed_data = self.edit_data(json_data)
            
            # Return successful response
            response = {
                "message": "Edit is working properly",
                "status": "success",
                "processed_data": processed_data,
                "file_path": file_path,
                "operation": operation
            }
            
            logger.info(f"Processed request successfully: {response}")
            return jsonify(response), 200
        
        except Exception as e:
            logger.error(f"Error processing JSON request: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }), 500
    
    def edit_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit 1 feature: Modify the JSON data.
        
        Args:
            data: The JSON data to modify.
            
        Returns:
            Modified JSON data.
        """
        try:
            # Make a deep copy of the data to avoid modifying the original
            edited_data = copy.deepcopy(data)
            
            # Add an "edited" flag
            edited_data["edited"] = True
            edited_data["edit_version"] = "Edit 1"
            
            # If there's a "properties" field, modify it
            if "properties" in edited_data:
                edited_data["properties"]["processed"] = True
            
            logger.info("Applied Edit 1 to data")
            return edited_data
        
        except Exception as e:
            logger.error(f"Error in edit_data: {str(e)}")
            raise
    
    def upload_json(self):
        """
        Handle JSON file upload.
        
        Returns:
            JSON response with status and file details.
        """
        try:
            logger.info("Received file upload request")
            
            # Check if the request has a file
            if 'file' not in request.files:
                logger.error("No file part in the request")
                return jsonify({
                    "status": "error",
                    "message": "No file part in the request"
                }), 400
            
            file = request.files['file']
            
            # Check if the file is selected
            if file.filename == '':
                logger.error("No file selected")
                return jsonify({
                    "status": "error",
                    "message": "No file selected"
                }), 400
            
            # Check if the file is a JSON file
            if not file.filename.endswith('.json'):
                logger.error("Uploaded file is not a JSON file")
                return jsonify({
                    "status": "error",
                    "message": "Uploaded file must be a JSON file"
                }), 400
            
            # Create the json_files directory if it doesn't exist
            upload_dir = os.path.abspath(os.path.join(os.getcwd(), 'json_files'))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_dir, file.filename)
            file.save(file_path)
            logger.info(f"File saved successfully at {file_path}")
            
            # Validate JSON format
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                # Remove the invalid file
                os.remove(file_path)
                logger.error(f"Invalid JSON format: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": f"Invalid JSON format: {str(e)}"
                }), 400
            
            # Process the file
            response = {
                "status": "success",
                "message": "File uploaded and processed successfully",
                "file_path": file_path,
                "file_name": file.filename
            }
            
            logger.info(f"File upload successful: {file.filename}")
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Error handling file upload: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error processing file: {str(e)}"
            }), 500
    
    def process_multiple_jsons(self):
        """
        Process multiple JSON files uploaded in bulk.
        
        Returns:
            JSON response with status and processing results.
        """
        try:
            if request.method == 'OPTIONS':
                # Return an empty response for OPTIONS requests (CORS preflight)
                response = jsonify({})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
                return response, 200
                
            logger.info("Received bulk file upload request")
            logger.info(f"Request headers: {dict(request.headers)}")
            logger.info(f"Request files keys: {list(request.files.keys())}")
            
            # Check if the request has files
            if 'jsonFiles' not in request.files:
                logger.error(f"No jsonFiles part in the request. Available keys: {list(request.files.keys())}")
                return jsonify({
                    "status": "error",
                    "message": "No files found in the request"
                }), 400
            
            # Get all files with the name 'jsonFiles'
            files = request.files.getlist('jsonFiles')
            
            if not files or len(files) == 0:
                logger.error("No files were selected")
                return jsonify({
                    "status": "error",
                    "message": "No files were selected"
                }), 400
            
            logger.info(f"Processing {len(files)} files")
            
            # Create the json_files directory if it doesn't exist
            upload_dir = os.path.abspath(os.path.join(os.getcwd(), 'json_files'))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Process each file
            processed_files = []
            failed_files = []
            
            for file in files:
                try:
                    # Skip if no filename
                    if file.filename == '':
                        continue
                    
                    # Log file information
                    logger.info(f"Processing file: {file.filename}, Content-Type: {file.content_type}")
                    
                    # Check if it's a JSON file
                    if not file.filename.endswith('.json'):
                        failed_files.append({
                            "filename": file.filename,
                            "reason": "Not a JSON file"
                        })
                        continue
                    
                    # Save the file
                    file_path = os.path.join(upload_dir, file.filename)
                    file.save(file_path)
                    logger.info(f"Saved file to: {file_path}")
                    
                    # Validate JSON format
                    try:
                        with open(file_path, 'r') as f:
                            json_data = json.load(f)
                            
                            # Process the JSON data (apply the edit function)
                            processed_data = self.edit_data(json_data)
                            
                            # Save the processed data back to the file
                            with open(file_path, 'w') as f_write:
                                json.dump(processed_data, f_write, indent=2)
                            
                            processed_files.append({
                                "filename": file.filename,
                                "path": file_path,
                                "status": "success"
                            })
                            logger.info(f"Successfully processed file: {file.filename}")
                            
                    except json.JSONDecodeError as e:
                        # Remove the invalid file
                        os.remove(file_path)
                        error_message = f"Invalid JSON format: {str(e)}"
                        logger.error(f"Error with file {file.filename}: {error_message}")
                        failed_files.append({
                            "filename": file.filename,
                            "reason": error_message
                        })
                        
                except Exception as e:
                    error_message = f"Processing error: {str(e)}"
                    logger.error(f"Error processing file {file.filename}: {error_message}")
                    failed_files.append({
                        "filename": file.filename,
                        "reason": error_message
                    })
            
            # Prepare response
            response = {
                "status": "success",
                "message": f"Processed {len(processed_files)} files successfully, {len(failed_files)} failed",
                "processedCount": len(processed_files),
                "failedCount": len(failed_files),
                "processed": processed_files,
                "failed": failed_files
            }
            
            logger.info(f"Bulk processing completed: {len(processed_files)} successful, {len(failed_files)} failed")
            return jsonify(response), 200
            
        except Exception as e:
            error_message = f"Error handling bulk file upload: {str(e)}"
            logger.error(error_message)
            logger.exception(e)
            return jsonify({
                "status": "error",
                "message": error_message
            }), 500
    
    def process_edit(self):
        """
        Process a JSON edit request. This endpoint accepts JSON with a file_path parameter
        pointing to a local JSON file, processes it, and saves the response to Excel.
        
        It can also accept multiple file paths via the file_paths parameter.
        
        Returns:
            JSON response with edit status.
        """
        try:
            logger.info("Processing edit request")
            
            # Get request data
            data = request.json
            
            if not data:
                logger.error("No JSON data in request")
                return jsonify({
                    "status": "error",
                    "message": "No JSON data provided"
                }), 400
            
            # Get the file path(s) from the request
            file_path = data.get('file_path')
            file_paths = data.get('file_paths', [])
            edit_id = data.get('edit_id', 'Edit 1')  # Default to Edit 1 if not provided
            
            # Validate input
            if not file_path and not file_paths:
                logger.error("No file_path or file_paths provided in request")
                return jsonify({
                    "status": "error",
                    "message": "Either file_path or file_paths parameter is required"
                }), 400
            
            # Process either single file or multiple files
            if file_path:
                # Single file case
                logger.info(f"Processing single file from path: {file_path}")
                
                # Validate that the file exists
                if not os.path.isfile(file_path):
                    logger.error(f"File not found: {file_path}")
                    return jsonify({
                        "status": "error",
                        "message": f"File not found at path: {file_path}"
                    }), 404
                
                # Load and parse the JSON file
                try:
                    with open(file_path, 'r') as file:
                        json_data = json.load(file)
                        
                    logger.info(f"Successfully loaded JSON from {file_path}")
                    
                    # Process single file
                    processed_data = {
                        "input": json_data,
                        "edit_id": edit_id,
                        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "Success",
                        "file_path": file_path
                    }
                    
                    # Save to Excel
                    self._save_edit_to_excel(processed_data)
                    
                    return jsonify({
                        "status": "success",
                        "message": "Edit is working properly",
                        "edit_id": edit_id,
                        "processed": True
                    }), 200
                    
                except Exception as e:
                    logger.error(f"Error parsing JSON file: {str(e)}")
                    return jsonify({
                        "status": "error",
                        "message": f"Error parsing JSON file: {str(e)}"
                    }), 400
                
            else:
                # Multiple files case
                logger.info(f"Processing multiple files: {file_paths}")
                
                if not isinstance(file_paths, list) or len(file_paths) == 0:
                    logger.error("Invalid file_paths parameter: must be a non-empty list")
                    return jsonify({
                        "status": "error",
                        "message": "file_paths must be a non-empty list of file paths"
                    }), 400
                
                results = []
                success_count = 0
                error_count = 0
                
                for index, path in enumerate(file_paths):
                    try:
                        # Validate that the file exists
                        if not os.path.isfile(path):
                            logger.warning(f"File not found: {path}")
                            results.append({
                                "file_path": path,
                                "status": "error",
                                "message": f"File not found at path: {path}"
                            })
                            error_count += 1
                            continue
                        
                        # Load and parse the JSON file
                        with open(path, 'r') as file:
                            json_data = json.load(file)
                        
                        logger.info(f"Successfully loaded JSON from {path}")
                        
                        # Process file
                        file_edit_id = f"{edit_id}_{index + 1}" if len(file_paths) > 1 else edit_id
                        processed_data = {
                            "input": json_data,
                            "edit_id": file_edit_id,
                            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "status": "Success",
                            "file_path": path
                        }
                        
                        # Save to Excel
                        self._save_edit_to_excel(processed_data)
                        
                        # Add to results
                        results.append({
                            "file_path": path,
                            "status": "success",
                            "edit_id": file_edit_id
                        })
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing file {path}: {str(e)}")
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
            logger.error(f"Error processing edit: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error processing edit: {str(e)}"
            }), 500
            
    def _save_edit_to_excel(self, processed_data):
        """
        Save the processed edit data to Excel.
        
        Args:
            processed_data: Data to save to Excel.
        """
        try:
            # Path to the Excel file
            excel_path = os.path.join('results', 'api_responses.xlsx')
            
            # Create results directory if it doesn't exist
            os.makedirs(os.path.dirname(excel_path), exist_ok=True)
            
            # Check if Excel file exists, create it if not
            if os.path.exists(excel_path):
                # Read existing Excel file
                try:
                    df = pd.read_excel(excel_path, sheet_name="Processed JSON")
                except ValueError:
                    # If "Processed JSON" sheet doesn't exist, create a new DataFrame
                    df = pd.DataFrame(columns=["edit_id", "timestamp", "status", "json_input", "response"])
            else:
                # Create a new DataFrame if the file doesn't exist
                df = pd.DataFrame(columns=["edit_id", "timestamp", "status", "json_input", "response"])
            
            # Convert the input and response to JSON strings
            json_input = json.dumps(processed_data["input"], indent=2)
            response = json.dumps({"message": "Edit is working properly"}, indent=2)
            
            # Create a new row for the DataFrame
            new_row = {
                "edit_id": processed_data["edit_id"],
                "timestamp": processed_data["timestamp"],
                "status": processed_data["status"],
                "json_input": json_input,
                "response": response
            }
            
            # Append the new row to the DataFrame
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Write the DataFrame to Excel
            with pd.ExcelWriter(excel_path, engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, sheet_name="Processed JSON", index=False)
                
            logger.info(f"Successfully saved edit data to Excel: {excel_path}")
        
        except Exception as e:
            logger.error(f"Error saving edit data to Excel: {str(e)}")
            raise
    
    def run(self):
        """Run the API server."""
        try:
            logger.info(f"Starting API server on {self.host}:{self.port}")
            self.app.run(host=self.host, port=self.port)
        except Exception as e:
            logger.error(f"Error running API server: {str(e)}")
            raise

# For direct execution testing
if __name__ == "__main__":
    api_service = ApiService()
    api_service.run()