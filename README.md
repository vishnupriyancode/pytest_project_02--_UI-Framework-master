# JSON Processing API Solution

This solution provides a robust framework for processing JSON files, handling API requests, and storing responses.

## Components

1. **Flask API Server** (`api_server.py`)
   - Provides endpoints for processing JSON files and folders
   - Handles CORS and error responses
   - Logs requests and responses

2. **JSON File Processor** (`process_json_files.py`)
   - Scans directory for JSON files
   - Processes files in parallel using multithreading
   - Handles retries and error logging

3. **Postman Collection Generator** (`generate_postman.py`)
   - Creates a ready-to-use Postman collection
   - Includes requests for testing all endpoints
   - Auto-generates requests for each JSON file

## Setup Instructions

### Prerequisites

- Python 3.8 or newer
- pip (Python package manager)
- Postman (optional, for testing)

### Installation

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure your `Edit1_jsons` folder exists at:
   ```
   C:\Cursor_Projects\pytest_project_02 -_UI Framework\Edit1_jsons
   ```
   Or update the `SOURCE_DIR` constant in `process_json_files.py` to point to your JSON files.

### Running the Solution

1. **Start the API Server**:
   ```bash
   python api_server.py
   ```
   The server will start at http://localhost:5000

2. **Process JSON Files**:
   ```bash
   python process_json_files.py
   ```
   This will process all JSON files and generate an Excel report

3. **Generate Postman Collection**:
   ```bash
   python generate_postman.py
   ```
   Import the generated file into Postman to test the API manually

## API Endpoints

- `GET /test-connection` - Test if API is available
- `POST /process-edit` - Process a single JSON file
- `POST /process-folder` - Process all JSON files in a folder

## Request Format Examples

### Processing a Single File

```json
{
  "file_path": "C:\\Cursor_Projects\\pytest_project_02 -_UI Framework\\Edit1_jsons\\file.json",
  "edit_id": "Edit 1"
}
```

### Processing a Folder

```json
{
  "folder_path": "C:\\Cursor_Projects\\pytest_project_02 -_UI Framework\\Edit1_jsons",
  "edit_id": "Folder Edit"
}
```

## Troubleshooting

- **API Timeout**: Increase `REQUEST_TIMEOUT` in `process_json_files.py`
- **CORS Issues**: Verify that the API server is allowing requests from your origin
- **File Not Found**: Check that the paths are correct and accessible

## Logging

- API Server logs: `api_server.log`
- JSON Processing logs: `json_processing.log`

## Output Files

- `responses.xlsx`: Contains responses recorded by the API
- `processing_results.xlsx`: Contains results of the batch processing script 