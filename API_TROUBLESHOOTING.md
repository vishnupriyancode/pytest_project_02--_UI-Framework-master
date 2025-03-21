# API Server Troubleshooting Guide

## Starting the Server

1. Run the `start_api_server.bat` file by double-clicking it.
2. Alternatively, open a command prompt and run:
   ```
   python src/run_api.py
   ```
3. Keep the terminal window open while using the API.
4. You should see messages like "Starting API server on http://localhost:5000" and "Running on http://0.0.0.0:5000".

## Common Issues and Solutions

### "NetworkError when attempting to fetch resource"

**Causes:**
- The API server is not running
- The API server is running on a different port
- A firewall is blocking the connection

**Solutions:**
1. Make sure the server is running (check the terminal window)
2. Verify the server started successfully without errors
3. Try using 127.0.0.1 instead of localhost in your browser
4. Check if any firewall is blocking port 5000

### "File not found at path"

**Causes:**
- The file path provided doesn't exist
- The path uses incorrect format

**Solutions:**
1. Double-check the file path is correct
2. Use double backslashes in paths (e.g., `C:\\path\\to\\file.json`)
3. Try using forward slashes instead (e.g., `C:/path/to/file.json`)
4. Make sure the file has read permissions

### "Invalid JSON format in file"

**Cause:** The file exists but doesn't contain valid JSON

**Solution:** Check your JSON file for syntax errors using a JSON validator

## Testing the API Server

To verify the API server is running correctly:

1. Open a browser and navigate to: http://localhost:5000/health-check
2. You should see a response like:
   ```json
   {
     "status": "healthy",
     "message": "API server is running properly",
     "server": "Flask API Service",
     "version": "1.0.0"
   }
   ```

## Checking Logs

If issues persist, check the logs:
1. Open the `api_server.log` file in your project directory
2. Look for any ERROR or WARNING messages that might indicate the problem

## Dependency Issues

If you encounter errors related to missing dependencies:

```bash
pip install -r requirements.txt
```

This will install all the required packages for the API server to run.