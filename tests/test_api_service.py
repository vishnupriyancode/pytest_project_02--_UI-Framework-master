import json
import pytest
from flask import Flask
from flask.testing import FlaskClient
from src.api_service import ApiService

@pytest.fixture
def api_service():
    """Create an API service instance for testing."""
    return ApiService(host="127.0.0.1", port=5000)

@pytest.fixture
def test_client(api_service):
    """Create a Flask test client for the API service."""
    api_service.app.config['TESTING'] = True
    with api_service.app.test_client() as client:
        yield client

def test_api_service_initialization():
    """Test ApiService initialization."""
    service = ApiService(host="127.0.0.1", port=8080)
    assert service.host == "127.0.0.1"
    assert service.port == 8080
    assert service.app is not None

def test_edit_data(api_service):
    """Test the Edit 1 feature."""
    # Test with an empty dict
    data = {}
    edited_data = api_service.edit_data(data)
    assert edited_data["edited"] is True
    assert edited_data["edit_version"] == "Edit 1"
    
    # Test with properties
    data = {
        "id": 1,
        "name": "Test Data",
        "properties": {
            "value": 42,
            "active": True
        }
    }
    
    edited_data = api_service.edit_data(data)
    assert edited_data["edited"] is True
    assert edited_data["edit_version"] == "Edit 1"
    assert edited_data["properties"]["processed"] is True
    assert edited_data["properties"]["value"] == 42
    
    # Make sure original data is not modified
    assert "edited" not in data
    assert "processed" not in data.get("properties", {})

def test_process_json_endpoint(test_client):
    """Test the /process-json endpoint."""
    # Create test data
    data = {
        "file_path": "C:\\json_files\\test.json",
        "operation": "process_data",
        "data": {
            "id": 1,
            "name": "Test Data",
            "properties": {
                "value": 42,
                "active": True
            }
        }
    }
    
    # Make a POST request to the endpoint
    response = test_client.post(
        '/process-json',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    # Check that the response is OK
    assert response.status_code == 200
    
    # Parse the response data
    response_data = json.loads(response.data)
    
    # Check the response data
    assert response_data["status"] == "success"
    assert response_data["message"] == "Edit is working properly"
    assert response_data["file_path"] == "C:\\json_files\\test.json"
    assert response_data["operation"] == "process_data"
    assert "processed_data" in response_data
    assert response_data["processed_data"]["edited"] is True
    assert response_data["processed_data"]["edit_version"] == "Edit 1"

def test_process_json_endpoint_missing_file_path(test_client):
    """Test the /process-json endpoint with missing file_path."""
    # Create test data with missing file_path
    data = {
        "operation": "process_data",
        "data": {
            "id": 1,
            "name": "Test Data"
        }
    }
    
    # Make a POST request to the endpoint
    response = test_client.post(
        '/process-json',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    # Check that the response is Bad Request
    assert response.status_code == 400
    
    # Parse the response data
    response_data = json.loads(response.data)
    
    # Check the response data
    assert response_data["status"] == "error"
    assert "No file_path provided" in response_data["message"]

def test_process_json_endpoint_no_data(test_client):
    """Test the /process-json endpoint with no data."""
    # Make a POST request to the endpoint with no data
    response = test_client.post('/process-json')
    
    # Check that the response is Bad Request
    assert response.status_code == 400
    
    # Parse the response data
    response_data = json.loads(response.data)
    
    # Check the response data
    assert response_data["status"] == "error"
    assert "Content-Type must be application/json" in response_data["message"]