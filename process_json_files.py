import os
import requests
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import logging
import time
from tqdm import tqdm  # For progress bar
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('json_processing.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
SOURCE_DIR = r"C:\Cursor_Projects\pytest_project_02 -_UI Framework\Edit1_jsons"
API_ENDPOINT = "http://localhost:5000/process-edit"
MAX_WORKERS = 5  # Adjust based on your system capabilities
REQUEST_TIMEOUT = 60  # Seconds
RETRY_COUNT = 3
RETRY_DELAY = 2  # Seconds

def check_api_connection():
    """Check if the API server is running and accessible"""
    try:
        response = requests.get("http://localhost:5000/test-connection", timeout=5)
        if response.status_code == 200:
            logger.info("API server is running and accessible")
            return True
        else:
            logger.error(f"API server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to API server: {str(e)}")
        return False

def process_file(file_path):
    """Process a single JSON file through the API with retry logic"""
    # Normalize path to ensure proper format
    file_path = os.path.normpath(file_path)
    
    for attempt in range(RETRY_COUNT):
        try:
            # Prepare request payload
            payload = {
                "file_path": file_path,
                "edit_id": "Edit 1"
            }
            
            # Send request to API
            response = requests.post(
                API_ENDPOINT, 
                json=payload, 
                timeout=REQUEST_TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            
            # Check response
            if response.status_code == 200:
                logger.info(f"Successfully processed: {file_path}")
                return {"file": file_path, "status": "success", "response": response.json()}
            else:
                logger.warning(f"Failed to process: {file_path} - Status: {response.status_code} - Response: {response.text}")
                
                if attempt < RETRY_COUNT - 1:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds... (Attempt {attempt+1}/{RETRY_COUNT})")
                    time.sleep(RETRY_DELAY)
                else:
                    return {
                        "file": file_path, 
                        "status": "error", 
                        "status_code": response.status_code,
                        "message": response.text
                    }
        
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout processing {file_path}")
            if attempt < RETRY_COUNT - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds... (Attempt {attempt+1}/{RETRY_COUNT})")
                time.sleep(RETRY_DELAY)
            else:
                return {"file": file_path, "status": "error", "message": "API request timed out"}
        
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            if attempt < RETRY_COUNT - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds... (Attempt {attempt+1}/{RETRY_COUNT})")
                time.sleep(RETRY_DELAY)
            else:
                return {"file": file_path, "status": "error", "message": str(e)}
    
    # This should not be reached, but just in case
    return {"file": file_path, "status": "error", "message": "Maximum retry attempts exceeded"}

def main():
    """Run all tests"""
    print("\n📝 JSON Processing Utility\n")
    
    # First check if API is running
    if not check_api_connection():
        print("❌ API server is not running or not accessible. Please start the API server first.")
        print("   Run: python api_server.py")
        return
    
    # Check if source directory exists
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Source directory does not exist: {SOURCE_DIR}")
        return
    
    # Find all JSON files in the directory
    json_files = []
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith('.json'):
                json_files.append(os.path.join(root, file))
    
    if not json_files:
        print(f"❌ No JSON files found in {SOURCE_DIR}")
        return
    
    print(f"✅ Found {len(json_files)} JSON files to process")
    
    # Process files in parallel with progress bar
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_file = {executor.submit(process_file, file_path): file_path for file_path in json_files}
        
        # Process results as they complete with progress bar
        for future in tqdm(
            future_to_file, 
            total=len(future_to_file), 
            desc="Processing files", 
            unit="file"
        ):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                file_path = future_to_file[future]
                logger.error(f"Unexpected error processing {file_path}: {str(e)}")
                results.append({
                    "file": file_path,
                    "status": "error",
                    "message": f"Executor error: {str(e)}"
                })
    
    # Compile results
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = len(results) - success_count
    
    print(f"\n✅ Processing complete:")
    print(f"  - Total files: {len(results)}")
    print(f"  - Successful: {success_count}")
    print(f"  - Failed: {error_count}")
    
    # Save results to Excel
    try:
        df = pd.DataFrame([
            {
                'file_path': r["file"],
                'status': r["status"],
                'message': r.get("message", "Success"),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            } 
            for r in results
        ])
        
        excel_file = "processing_results.xlsx"
        df.to_excel(excel_file, index=False)
        print(f"\n✅ Results saved to {excel_file}")
    except Exception as e:
        logger.error(f"Error saving results to Excel: {str(e)}")
        print(f"\n❌ Failed to save results to Excel: {str(e)}")
    
    # Provide next steps
    if error_count > 0:
        print("\n⚠️ Some files failed to process. Check the Excel report for details.")
        print("   You can retry failed files or check the log for more information.")
    
    print("\n📝 Processing completed.")

if __name__ == "__main__":
    main() 