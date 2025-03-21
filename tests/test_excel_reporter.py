import os
import pytest
import pandas as pd
from src.excel_reporter import ExcelReporter

def test_excel_reporter_initialization(temp_output_file):
    """Test ExcelReporter initialization."""
    reporter = ExcelReporter(output_file=temp_output_file)
    assert reporter.output_file == temp_output_file
    assert reporter.data is not None
    assert all(key in reporter.data for key in ["Timestamp", "Input JSON", "API Response", "Expected Result", "Status"])

def test_add_response(excel_reporter):
    """Test adding a response to the Excel reporter."""
    input_json = "C:\\json_files\\test.json"
    api_response = {
        "status": "success",
        "message": "Edit is working properly",
        "data": {"example": "data"}
    }
    expected_result = "Success"
    
    # Add a response
    excel_reporter.add_response(input_json, api_response, expected_result)
    
    # Check that the data was added correctly
    assert len(excel_reporter.data["Input JSON"]) == 1
    assert excel_reporter.data["Input JSON"][0] == input_json
    assert excel_reporter.data["Expected Result"][0] == expected_result
    assert excel_reporter.data["Status"][0] == "Success"

def test_add_multiple_responses(excel_reporter):
    """Test adding multiple responses to the Excel reporter."""
    # Add first response
    input_json1 = "C:\\json_files\\test1.json"
    api_response1 = {
        "status": "success",
        "message": "Edit is working properly",
        "data": {"example": "data1"}
    }
    excel_reporter.add_response(input_json1, api_response1)
    
    # Add second response
    input_json2 = "C:\\json_files\\test2.json"
    api_response2 = {
        "status": "error",
        "message": "Something went wrong",
        "data": {"example": "data2"}
    }
    excel_reporter.add_response(input_json2, api_response2)
    
    # Check that both responses were added
    assert len(excel_reporter.data["Input JSON"]) == 2
    assert excel_reporter.data["Input JSON"][0] == input_json1
    assert excel_reporter.data["Input JSON"][1] == input_json2
    assert excel_reporter.data["Status"][0] == "Success"
    assert excel_reporter.data["Status"][1] == "Failure"

def test_save_to_excel(excel_reporter):
    """Test saving data to an Excel file."""
    # Add a response
    input_json = "C:\\json_files\\test.json"
    api_response = {
        "status": "success",
        "message": "Edit is working properly",
        "data": {"example": "data"}
    }
    excel_reporter.add_response(input_json, api_response)
    
    # Save to Excel
    output_file = excel_reporter.save_to_excel()
    
    # Check that the file exists
    assert os.path.exists(output_file)
    
    # Read the Excel file
    df = pd.read_excel(output_file)
    
    # Check the data
    assert len(df) == 1
    assert df["Input JSON"][0] == input_json
    assert df["Expected Result"][0] == "Success"

def test_append_to_excel(excel_reporter):
    """Test appending data to an existing Excel file."""
    # Add and save the first response
    input_json1 = "C:\\json_files\\test1.json"
    api_response1 = {
        "status": "success",
        "message": "Edit is working properly",
        "data": {"example": "data1"}
    }
    excel_reporter.add_response(input_json1, api_response1)
    excel_reporter.save_to_excel()
    
    # Clear the current data
    excel_reporter.data = {
        "Timestamp": [],
        "Input JSON": [],
        "API Response": [],
        "Expected Result": [],
        "Status": []
    }
    
    # Add a second response
    input_json2 = "C:\\json_files\\test2.json"
    api_response2 = {
        "status": "success",
        "message": "Edit is working properly",
        "data": {"example": "data2"}
    }
    excel_reporter.add_response(input_json2, api_response2)
    
    # Append to Excel
    output_file = excel_reporter.append_to_excel()
    
    # Read the Excel file
    df = pd.read_excel(output_file)
    
    # Check the data
    assert len(df) == 2
    assert df["Input JSON"][0] == input_json1
    assert df["Input JSON"][1] == input_json2

def test_directory_creation(temp_output_file):
    """Test that the directory is created if it doesn't exist."""
    # Create a path with a non-existent directory
    dir_path = os.path.join(os.path.dirname(temp_output_file), "nonexistent")
    file_path = os.path.join(dir_path, "test.xlsx")
    
    # Create a reporter with this path
    reporter = ExcelReporter(output_file=file_path)
    
    # Add a response
    input_json = "C:\\json_files\\test.json"
    api_response = {
        "status": "success",
        "message": "Edit is working properly",
        "data": {"example": "data"}
    }
    reporter.add_response(input_json, api_response)
    
    # Save to Excel
    output_file = reporter.save_to_excel()
    
    # Check that the directory and file exist
    assert os.path.exists(dir_path)
    assert os.path.exists(output_file)