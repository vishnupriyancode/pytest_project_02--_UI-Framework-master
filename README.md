# JSON Processing API Solution

This solution provides a robust framework for processing JSON files, handling API requests, and storing responses.

## Project Structure

```
.
├── api_server.py          # Main API server
├── app.py                 # Main application
├── config/               # Configuration files
│   ├── __init__.py      # Package initialization
│   ├── settings.py      # Application settings
│   └── logging_config.py # Logging configuration
├── scripts/              # Start scripts and utilities
│   ├── start.py         # Main start script (Python)
│   ├── start.bat        # Windows start script
│   └── start.sh         # Unix start script
├── docs/                 # Documentation
│   └── examples/        # Example files and samples
├── tests/               # Test files
├── src/                 # Source code
├── static/              # Static files
├── logs/                # Application logs
├── uploads/             # Upload directory
└── output/              # Output directory
```

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

## Configuration

The project uses a centralized configuration system in the `config` directory:

- `settings.py`: Contains all application settings
- `logging_config.py`: Configures logging for different components

Key configuration options:
- API and Frontend ports
- File processing settings
- Logging levels and formats
- Security settings
- Database configuration

## Setup Instructions

### Prerequisites

- Python 3.8 or newer
- pip (Python package manager)
- Node.js and npm (for frontend)
- Postman (optional, for testing)

### Installation

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. Configure the application:
   - Copy `.env.example` to `.env`
   - Update settings in `config/settings.py` if needed
   - Ensure your `Edit1_jsons` folder exists or update `SOURCE_DIR` in settings

### Running the Solution

The project includes a unified start script with improved logging and configuration:

1. **On Windows**:
   ```bash
   scripts\start.bat
   ```

2. **On Unix-like systems**:
   ```bash
   ./scripts/start.sh
   ```

3. **Using Python directly**:
   ```bash
   python scripts/start.py
   ```

The start script supports the following options:
- `--api-only`: Start only the API server
- `--frontend-only`: Start only the frontend
- `--debug`: Enable debug mode for detailed logging
- No arguments: Start both servers

Example:
```bash
# Start with debug logging
python scripts/start.py --debug

# Start only the API server
python scripts/start.py --api-only

# Start only the frontend
python scripts/start.py --frontend-only

# Start both (default)
python scripts/start.py
```

## Logging

The application uses a comprehensive logging system:
- Logs are stored in the `logs` directory
- Rotating file handler (10MB max size, 5 backup files)
- Separate loggers for API, processor, and frontend
- Console and file output
- Configurable log levels

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

- **API Timeout**: Adjust `REQUEST_TIMEOUT` in `config/settings.py`
- **CORS Issues**: Check `CORS_ORIGINS` in `config/settings.py`
- **File Not Found**: Verify paths in `config/settings.py`
- **Logging Issues**: Check `logs` directory and `config/logging_config.py`

## Output Files

- `responses.xlsx`: Contains responses recorded by the API
- `processing_results.xlsx`: Contains results of the batch processing script

# Project Name

This project is containerized using Docker. Follow the instructions below to run the project.

## Prerequisites

- Docker installed on your machine
- Docker Compose installed on your machine

## Running the Project

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Build the Docker image:
   ```bash
   docker-compose build
   ```

3. Start the Docker container:
   ```bash
   docker-compose up
   ```

4. Open your browser and navigate to `http://localhost:3000` to view the project.

## Stopping the Project

To stop the running container, press `Ctrl+C` in the terminal where the container is running, or run:
```bash
docker-compose down
```

## Additional Information

- The project runs on port 3000.
- Any changes made to the project files will be reflected in the container due to the volume mapping in docker-compose.yml. 