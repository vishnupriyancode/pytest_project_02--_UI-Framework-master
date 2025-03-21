import os
import json
import pytest
from src.json_reader import JsonReader

def test_json_reader_initialization(temp_json_dir):
    """Test JsonReader initialization."""
    reader = JsonReader(directory_path=temp_json_dir)
    assert reader.directory_path == temp_json_dir

def test_get_json_files(json_reader, sample_json_files):
    """Test getting JSON files from the directory."""
    json_files = json_reader.get_json_files()
    assert len(json_files) == 2
    assert all(os.path.exists(file) for file in json_files)
    assert all(file.endswith('.json') for file in json_files)

def test_read_json_file(json_reader, sample_json_files):
    """Test reading a JSON file."""
    file_path = sample_json_files[0]
    data = json_reader.read_json_file(file_path)
    
    assert data is not None
    assert isinstance(data, dict)
    assert data["id"] == 1
    assert data["name"] == "Test Data 1"
    assert "properties" in data
    assert data["properties"]["value"] == 42

def test_read_json_file_not_found(json_reader):
    """Test reading a non-existent JSON file."""
    with pytest.raises(FileNotFoundError):
        json_reader.read_json_file("nonexistent.json")

def test_create_request_payload(json_reader, sample_json_files):
    """Test creating a request payload."""
    file_path = sample_json_files[0]
    payload = json_reader.create_request_payload(file_path)
    
    assert payload is not None
    assert isinstance(payload, dict)
    assert payload["file_path"] == file_path
    assert payload["operation"] == "process_data"
    assert "data" in payload
    assert payload["data"]["id"] == 1
    assert payload["data"]["name"] == "Test Data 1"

def test_create_request_payload_custom_operation(json_reader, sample_json_files):
    """Test creating a request payload with a custom operation."""
    file_path = sample_json_files[0]
    operation = "custom_operation"
    payload = json_reader.create_request_payload(file_path, operation)
    
    assert payload is not None
    assert payload["operation"] == operation

def test_directory_not_found():
    """Test handling of a non-existent directory."""
    reader = JsonReader(directory_path="/nonexistent/directory/")
    with pytest.raises(FileNotFoundError):
        reader.get_json_files()