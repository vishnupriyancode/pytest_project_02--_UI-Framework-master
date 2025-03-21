import os
import pytest
from unittest.mock import MagicMock, patch
from src.workflow import JsonProcessingWorkflow

@pytest.fixture
def mock_components():
    """Create mock components for the workflow."""
    json_reader_mock = MagicMock()
    api_client_mock = MagicMock()
    excel_reporter_mock = MagicMock()
    api_service_mock = MagicMock()
    
    return {
        "json_reader": json_reader_mock,
        "api_client": api_client_mock,
        "excel_reporter": excel_reporter_mock,
        "api_service": api_service_mock
    }

@pytest.fixture
def workflow_with_mocks(mock_components, temp_json_dir, temp_output_file):
    """Create a workflow with mock components."""
    workflow = JsonProcessingWorkflow(
        json_dir=temp_json_dir,
        output_excel=temp_output_file
    )
    
    # Replace the components with mocks
    workflow.json_reader = mock_components["json_reader"]
    workflow.api_client = mock_components["api_client"]
    workflow.excel_reporter = mock_components["excel_reporter"]
    workflow.api_service = mock_components["api_service"]
    
    # Mock the process_single_file method
    workflow.process_single_file = MagicMock()
    
    return workflow

def test_workflow_initialization(temp_json_dir, temp_output_file):
    """Test workflow initialization."""
    workflow = JsonProcessingWorkflow(
        json_dir=temp_json_dir,
        output_excel=temp_output_file
    )
    
    assert workflow.json_dir == temp_json_dir
    assert workflow.output_excel == temp_output_file
    assert workflow.json_reader is not None
    assert workflow.api_client is not None
    assert workflow.excel_reporter is not None
    assert workflow.api_service is not None

def test_start_api_service(workflow_with_mocks, mock_components):
    """Test starting the API service."""
    with patch('time.sleep'):  # Mock sleep to speed up the test
        workflow_with_mocks.start_api_service()
        
        # Check that the API service was started
        mock_components["api_service"].run.assert_called_once()

def test_process_single_file_success(workflow_with_mocks, mock_components, sample_json_files):
    """Test processing a single file with success."""
    # Restore the original method for this test
    workflow_with_mocks.process_single_file = JsonProcessingWorkflow.process_single_file.__get__(workflow_with_mocks, JsonProcessingWorkflow)
    
    # Set up mocks
    file_path = sample_json_files[0]
    payload = {"file_path": file_path, "operation": "process_data", "data": {"id": 1}}
    response = {"status": "success", "message": "Edit is working properly"}
    
    mock_components["json_reader"].create_request_payload.return_value = payload
    mock_components["api_client"].process_json.return_value = response
    
    # Process the file
    result = workflow_with_mocks.process_single_file(file_path)
    
    # Check that the correct methods were called
    mock_components["json_reader"].create_request_payload.assert_called_once_with(file_path)
    mock_components["api_client"].process_json.assert_called_once_with(payload)
    mock_components["excel_reporter"].add_response.assert_called_once_with(
        input_json=file_path,
        api_response=response,
        expected_result="Success"
    )
    
    # Check the result
    assert result == response

def test_process_single_file_error(workflow_with_mocks, mock_components, sample_json_files):
    """Test processing a single file with an error."""
    # Restore the original method for this test
    workflow_with_mocks.process_single_file = JsonProcessingWorkflow.process_single_file.__get__(workflow_with_mocks, JsonProcessingWorkflow)
    
    # Set up mocks
    file_path = sample_json_files[0]
    error_message = "Test error"
    
    mock_components["json_reader"].create_request_payload.side_effect = Exception(error_message)
    
    # Process the file (should raise an exception)
    with pytest.raises(Exception) as exc_info:
        workflow_with_mocks.process_single_file(file_path)
    
    # Check that the error was added to the Excel reporter
    mock_components["excel_reporter"].add_response.assert_called_once_with(
        input_json=file_path,
        api_response={"status": "error", "message": error_message},
        expected_result="Success"
    )
    
    # Check the exception
    assert error_message in str(exc_info.value)

def test_process_json_files_success(workflow_with_mocks, mock_components, sample_json_files):
    """Test processing all JSON files with success."""
    # Set up mocks
    mock_components["json_reader"].get_json_files.return_value = sample_json_files
    mock_components["excel_reporter"].save_to_excel.return_value = "output.xlsx"
    
    # Process all files
    result = workflow_with_mocks.process_json_files()
    
    # Check that the correct methods were called
    mock_components["json_reader"].get_json_files.assert_called_once()
    assert workflow_with_mocks.process_single_file.call_count == len(sample_json_files)
    mock_components["excel_reporter"].save_to_excel.assert_called_once()
    
    # Check the result
    assert result == "output.xlsx"

def test_process_json_files_no_files(workflow_with_mocks, mock_components):
    """Test processing when no JSON files are found."""
    # Set up mocks
    mock_components["json_reader"].get_json_files.return_value = []
    
    # Process all files
    result = workflow_with_mocks.process_json_files()
    
    # Check that the correct methods were called
    mock_components["json_reader"].get_json_files.assert_called_once()
    workflow_with_mocks.process_single_file.assert_not_called()
    mock_components["excel_reporter"].save_to_excel.assert_not_called()
    
    # Check the result
    assert result is None

@patch('src.workflow.JsonProcessingWorkflow')
def test_run_workflow_success(mock_workflow_class):
    """Test running the workflow with success."""
    # Set up mocks
    mock_workflow = MagicMock()
    mock_workflow_class.return_value = mock_workflow
    mock_workflow.process_json_files.return_value = "output.xlsx"
    
    # Import the run_workflow function
    from src.workflow import run_workflow
    
    # Run the workflow
    result = run_workflow()
    
    # Check that the correct methods were called
    mock_workflow_class.assert_called_once()
    mock_workflow.start_api_service.assert_called_once()
    mock_workflow.process_json_files.assert_called_once()
    
    # Check the result
    assert result == "output.xlsx"

@patch('src.workflow.JsonProcessingWorkflow')
def test_run_workflow_error(mock_workflow_class):
    """Test running the workflow with an error."""
    # Set up mocks
    mock_workflow = MagicMock()
    mock_workflow_class.return_value = mock_workflow
    mock_workflow.process_json_files.side_effect = Exception("Test error")
    
    # Import the run_workflow function
    from src.workflow import run_workflow
    
    # Run the workflow
    result = run_workflow()
    
    # Check that the correct methods were called
    mock_workflow_class.assert_called_once()
    mock_workflow.start_api_service.assert_called_once()
    mock_workflow.process_json_files.assert_called_once()
    
    # Check the result
    assert result is None