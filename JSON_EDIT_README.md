# JSON Edit Processing Feature

This document provides instructions on how to use the JSON edit processing feature that allows loading JSON files from your local drive, processing them, and saving the results to Excel.

## Features

- Load JSON files from your local drive (C: or any accessible path)
- Process single or multiple JSON files in one request
- Postman-like interface for advanced API testing
- Process JSON edits with a sample Edit ID (Edit 1) for validation
- View processing results directly in the UI
- Automatically save responses to Excel in the "Processed JSON" tab
- API endpoint for integration with Postman or other tools

## Using the UI

### Simple Mode

1. Navigate to the "Run JSONs" tab in the application
2. At the top of the page, you'll see the "Process JSON Edit from Local File" section
3. Enter the full path to your JSON file (e.g., `C:\path\to\your\file.json`)
4. Optionally, change the Edit ID (default is "Edit 1")
5. Click "Process Edit"
6. The result will be displayed below the form
7. The response is automatically saved to the Excel file in the "Processed JSON" tab

### Advanced Mode (Postman-like Interface)

1. Click the "Advanced Mode" button to switch to the Postman-like interface
2. Configure your request:
   - Set the HTTP method (default is POST)
   - Enter the request URL (default is `http://localhost:5000/process-edit`)
   - Add multiple file paths in the "JSON File Paths" section
   - View or modify the request body in the "Body" tab
   - Add or modify headers in the "Headers" tab
3. Click "Send" to process the request
4. View the response in the "Response" tab
5. The results will also be displayed below the form
6. All responses are saved to the Excel file in the "Processed JSON" tab

## Processing Multiple Files

You can process multiple JSON files at once using either:

1. The Advanced Mode UI:
   - Click "Advanced Mode"
   - Add multiple file paths using the "Add File" button
   - Each file will be processed individually and results combined

2. The API directly:
   - Use the `file_paths` parameter instead of `file_path` in your request
   - Provide an array of file paths to process
   - Each file will get a unique Edit ID based on the provided base ID

## Using the API with Postman

### Single File Processing

1. Import the provided `postman_collection_example.json` into Postman
2. Open the "Process Edit from Single JSON File" request
3. Update the request body with your file path:
   ```json
   {
     "file_path": "C:\\path\\to\\your\\sample.json",
     "edit_id": "Edit 1"
   }
   ```
4. Send the request to `http://localhost:5000/process-edit`
5. You should receive a response like:
   ```json
   {
     "status": "success",
     "message": "Edit is working properly",
     "edit_id": "Edit 1",
     "processed": true
   }
   ```

### Multiple Files Processing

1. Open the "Process Edit from Multiple JSON Files" request
2. Update the request body with multiple file paths:
   ```json
   {
     "file_paths": [
       "C:\\path\\to\\your\\sample1.json",
       "C:\\path\\to\\your\\sample2.json",
       "C:\\path\\to\\your\\sample3.json"
     ],
     "edit_id": "Bulk_Edit"
   }
   ```
3. Send the request to `http://localhost:5000/process-edit`
4. You will receive a response with results for each file:
   ```json
   {
     "status": "success",
     "message": "Edit processing completed",
     "summary": {
       "total": 3,
       "success": 3,
       "error": 0
     },
     "edit_id": "Bulk_Edit",
     "results": [
       {
         "file_path": "C:\\path\\to\\your\\sample1.json",
         "status": "success",
         "edit_id": "Bulk_Edit_1"
       },
       {
         "file_path": "C:\\path\\to\\your\\sample2.json",
         "status": "success",
         "edit_id": "Bulk_Edit_2"
       },
       {
         "file_path": "C:\\path\\to\\your\\sample3.json",
         "status": "success",
         "edit_id": "Bulk_Edit_3"
       }
     ],
     "processed": true
   }
   ```

## Sample JSON File

A sample JSON file (`sample_edit.json`) is provided for testing. You can use this file to test the functionality:

```json
{
  "edit_data": {
    "id": "sample_edit_1",
    "name": "Sample Edit",
    "description": "This is a sample JSON file for testing the edit functionality",
    "timestamp": "2023-07-15T10:30:00Z",
    "properties": {
      "type": "test",
      "priority": "high",
      "status": "pending"
    },
    "fields": [
      {
        "name": "field1",
        "value": "value1",
        "type": "string"
      },
      {
        "name": "field2",
        "value": 42,
        "type": "number"
      },
      {
        "name": "field3",
        "value": true,
        "type": "boolean"
      }
    ],
    "metadata": {
      "created_by": "user123",
      "version": "1.0.0",
      "tags": ["test", "sample", "edit"]
    }
  }
}
```

## Excel Output

The processed JSON responses are saved to:
- File: `results/api_responses.xlsx`
- Sheet: "Processed JSON"

The Excel file contains the following columns:
- edit_id: The ID of the edit (e.g., "Edit 1")
- timestamp: When the edit was processed
- status: The status of the processing (Success/Failed)
- json_input: The original JSON input
- response: The API response

## Troubleshooting

If you encounter any issues:

1. **File Not Found**: Ensure the file path is correct and accessible
2. **Invalid JSON**: Check that your JSON file is properly formatted
3. **API Connection**: Verify that the API server is running on port 5000
4. **Excel Access**: Make sure the Excel file is not open in another program when saving
5. **Multiple Files**: When processing multiple files, ensure all paths are valid and accessible

For any other issues, check the console logs for detailed error messages. 