import logging
import json
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, Blueprint
import os

# Import the database manager
from db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    filename='logs/api_middleware.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ApiMiddleware:
    """
    Middleware for extending API functionality without modifying the core API service.
    Adds database storage and query capabilities for API responses.
    """
    
    def __init__(self, app: Flask = None):
        """
        Initialize the API middleware.
        
        Args:
            app: Flask application to attach the middleware to.
        """
        self.blueprint = Blueprint('api_middleware', __name__)
        
        # Initialize database manager with type from environment
        db_type = os.getenv("DB_TYPE", "sqlite")
        logger.info(f"Using database type: {db_type}")
        self.db_manager = DatabaseManager(db_type=db_type)
        
        # Set up routes
        self.setup_routes()
        
        # Register blueprint with app if provided
        if app:
            self.register(app)
        
        logger.info("ApiMiddleware initialized")
    
    def setup_routes(self):
        """Set up the middleware routes."""
        self.blueprint.route('/get-response', methods=['GET'])(self.get_response)
        self.blueprint.route('/get-all-responses', methods=['GET'])(self.get_all_responses)
        logger.info("Middleware routes configured")
    
    def register(self, app: Flask):
        """
        Register the middleware with a Flask application.
        
        Args:
            app: The Flask application to register with.
        """
        app.register_blueprint(self.blueprint)
        
        # Register after_request handler to capture and store API responses
        app.after_request(self.process_response)
        
        logger.info("Middleware registered with Flask application")
    
    def process_response(self, response):
        """
        Process API responses after they are generated.
        Store responses from the /process-json endpoint in the database.
        
        Args:
            response: The Flask response object.
            
        Returns:
            The modified response.
        """
        try:
            # Check if this is a response from the process-json endpoint
            if request.path == '/process-json' and request.method == 'POST':
                # Get the response data
                response_data = json.loads(response.get_data(as_text=True))
                
                # Store the response in the database
                input_json = request.json.get('file_path', 'unknown')
                edit_id = self.db_manager.store_response(
                    input_json=input_json,
                    api_response=response_data,
                    expected_result="Success"
                )
                
                # Add the edit_id to the response
                response_data['edit_id'] = edit_id
                
                # Update the response with the modified data
                response.set_data(json.dumps(response_data))
                
                logger.info(f"Stored API response with edit_id {edit_id}")
        
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            # Don't modify the response in case of error
        
        return response
    
    def get_response(self):
        """
        Endpoint to retrieve a stored API response by its edit_id.
        
        Returns:
            JSON response with the stored data.
        """
        try:
            # Get the edit_id from the query parameters
            edit_id = request.args.get('edit_id')
            
            if not edit_id:
                logger.error("No edit_id provided in request")
                return jsonify({
                    "status": "error",
                    "message": "No edit_id provided"
                }), 400
            
            # Retrieve the response from the database
            response = self.db_manager.get_response_by_edit_id(int(edit_id))
            
            if response:
                logger.info(f"Retrieved response for edit_id {edit_id}")
                return jsonify(response), 200
            else:
                logger.warning(f"No response found for edit_id {edit_id}")
                return jsonify({
                    "status": "error",
                    "message": f"No response found for edit_id {edit_id}"
                }), 404
        
        except Exception as e:
            logger.error(f"Error retrieving response: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error retrieving response: {str(e)}"
            }), 500
    
    def get_all_responses(self):
        """
        Endpoint to retrieve all stored API responses.
        
        Returns:
            JSON response with all stored data.
        """
        try:
            # Retrieve all responses from the database
            responses = self.db_manager.get_all_responses()
            
            logger.info(f"Retrieved {len(responses)} responses")
            return jsonify({
                "status": "success",
                "count": len(responses),
                "responses": responses
            }), 200
        
        except Exception as e:
            logger.error(f"Error retrieving all responses: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error retrieving all responses: {str(e)}"
            }), 500

# For direct execution testing
if __name__ == "__main__":
    # Create a Flask app for testing
    app = Flask(__name__)
    
    # Create and register the middleware
    middleware = ApiMiddleware(app)
    
    # Run the app
    app.run(host="127.0.0.1", port=5001) 