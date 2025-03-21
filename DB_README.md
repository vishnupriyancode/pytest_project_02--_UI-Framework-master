# Database Integration Module

This module enhances the existing API application by adding database functionality without modifying the original codebase. It implements a database-backed storage system for API responses, assigns unique `edit_id` values to each response, and provides query mechanisms to retrieve responses.

## Features

1. **SQLite Database Integration**
   - Stores all API responses in a SQLite database
   - Automatically assigns a unique `edit_id` to each response
   - Preserves compatibility with the existing application

2. **New API Endpoints**
   - `/get-response?edit_id=123` - Retrieve a specific response by its `edit_id`
   - `/get-all-responses` - Retrieve all stored responses

3. **No Modifications to Existing Code**
   - Implements runtime patching using Python's module system
   - Preserves all existing functionality while adding new features

## Components

- **`src/db_manager.py`** - Core database operations (create, read, etc.)
- **`src/api_middleware.py`** - Flask middleware for database integration with the API
- **`src/db_integration.py`** - Runtime integration with the existing API service
- **`src/test_db_integration.py`** - Testing script for the database integration
- **`enhanced_main.py`** - Enhanced entry point that includes database functionality

## Database Schema

```sql
CREATE TABLE api_responses (
    edit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    input_json TEXT,
    api_response TEXT,
    expected_result TEXT
)
```

## How to Use

### Running the Enhanced Application

To run the application with database integration:

```bash
python enhanced_main.py
```

This will start the application with all the original functionality plus the database features.

### Testing the Database Features

To test the database integration:

1. Start the API service with database integration:
   ```bash
   python src/test_db_integration.py --run_api
   ```

2. In a separate terminal, run the integration tests:
   ```bash
   python src/test_db_integration.py --run_tests
   ```

### Using the API Endpoints

#### 1. Process JSON (Original Endpoint with Added `edit_id`)

```
POST http://localhost:5000/process-json
Content-Type: application/json

{
  "file_path": "example.json",
  "operation": "process_data",
  "data": {
    "example": "data",
    "properties": {
      "name": "Test Property"
    }
  }
}
```

Response:
```json
{
  "message": "Edit is working properly",
  "status": "success",
  "processed_data": {
    "example": "data",
    "properties": {
      "name": "Test Property",
      "processed": true
    },
    "edited": true,
    "edit_version": "Edit 1"
  },
  "file_path": "example.json",
  "operation": "process_data",
  "edit_id": 123
}
```

#### 2. Get Response by `edit_id`

```
GET http://localhost:5000/get-response?edit_id=123
```

Response:
```json
{
  "edit_id": 123,
  "timestamp": "2023-03-07 12:30:45",
  "input_json": "example.json",
  "api_response": {
    "message": "Edit is working properly",
    "status": "success",
    "processed_data": {
      "example": "data",
      "properties": {
        "name": "Test Property",
        "processed": true
      },
      "edited": true,
      "edit_version": "Edit 1"
    },
    "file_path": "example.json",
    "operation": "process_data"
  },
  "expected_result": "Success"
}
```

#### 3. Get All Responses

```
GET http://localhost:5000/get-all-responses
```

Response:
```json
{
  "status": "success",
  "count": 2,
  "responses": [
    {
      "edit_id": 124,
      "timestamp": "2023-03-07 12:35:12",
      "input_json": "example2.json",
      "api_response": { "..." },
      "expected_result": "Success"
    },
    {
      "edit_id": 123,
      "timestamp": "2023-03-07 12:30:45",
      "input_json": "example.json",
      "api_response": { "..." },
      "expected_result": "Success"
    }
  ]
}
```

## Implementation Details

### How It Works Without Modifying the Original Code

This module uses several Python techniques to add functionality without changing the existing code:

1. **Runtime Method Patching** - The `ApiServiceIntegrator` replaces the `run` method of the `ApiService` class at runtime.

2. **Flask Middleware** - The `ApiMiddleware` class adds new endpoints and intercepts/modifies responses from existing endpoints.

3. **SQLite Database** - Provides lightweight, file-based storage that requires no additional server setup.

### Database File Location

The SQLite database is stored at:
```
results/api_responses.db
```

You can access this file directly using any SQLite client if needed. 