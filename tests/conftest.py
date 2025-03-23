"""
Pytest configuration file with shared fixtures and settings.
"""
import os
import sys
import pytest
import tempfile
import json
import shutil
from pathlib import Path
import logging
from config import setup_logging

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the modules
from src.json_reader import JsonReader
from src.api_service import ApiService
from src.api_client import ApiClient
from src.excel_reporter import ExcelReporter
from src.workflow import JsonProcessingWorkflow

# Add src directory to Python path
src_path = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_path))

# Setup logging for tests
loggers = setup_logging()
logger = logging.getLogger('tests')

@pytest.fixture
def temp_json_dir():
    """Create a temporary directory for JSON files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after the test
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_json_files(temp_json_dir):
    """Create sample JSON files for testing."""
    # Create sample JSON file 1
    sample_data1 = {
        "id": 1,
        "name": "Test Data 1",
        "description": "This is a test JSON file",
        "properties": {
            "value": 42,
            "active": True,
            "tags": ["test", "sample", "json"]
        }
    }
    
    file_path1 = os.path.join(temp_json_dir, "test1.json")
    with open(file_path1, 'w') as f:
        json.dump(sample_data1, f)
    
    # Create sample JSON file 2
    sample_data2 = {
        "id": 2,
        "name": "Test Data 2",
        "description": "This is another test JSON file",
        "properties": {
            "value": 100,
            "active": False,
            "tags": ["json", "test", "example"]
        }
    }
    
    file_path2 = os.path.join(temp_json_dir, "test2.json")
    with open(file_path2, 'w') as f:
        json.dump(sample_data2, f)
    
    return [file_path1, file_path2]

@pytest.fixture
def temp_output_file():
    """Create a temporary file for Excel output."""
    fd, path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    yield path
    # Clean up after the test
    os.unlink(path)

@pytest.fixture
def json_reader(temp_json_dir):
    """Create a JsonReader instance for testing."""
    return JsonReader(directory_path=temp_json_dir)

@pytest.fixture
def excel_reporter(temp_output_file):
    """Create an ExcelReporter instance for testing."""
    return ExcelReporter(output_file=temp_output_file)

@pytest.fixture
def api_client():
    """Create an ApiClient instance for testing."""
    return ApiClient()

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture to provide the test data directory path."""
    return Path(__file__).parent / 'test_data'

@pytest.fixture(scope="session")
def sample_json_file(test_data_dir):
    """Fixture to provide a sample JSON file for testing."""
    return test_data_dir / 'sample.json'

@pytest.fixture(scope="session")
def mock_api_response():
    """Fixture to provide a mock API response."""
    return {
        "status": "success",
        "data": {"message": "Test response"}
    }

@pytest.fixture(scope="function")
def temp_upload_dir(tmp_path):
    """Fixture to provide a temporary upload directory."""
    upload_dir = tmp_path / 'uploads'
    upload_dir.mkdir()
    return upload_dir

@pytest.fixture(scope="function")
def temp_output_dir(tmp_path):
    """Fixture to provide a temporary output directory."""
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    return output_dir