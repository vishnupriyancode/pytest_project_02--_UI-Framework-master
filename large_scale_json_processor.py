import os
import json
import logging
import time
import asyncio
import aiohttp
import pandas as pd
import glob
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import traceback
import math
from tenacity import retry, stop_after_attempt, wait_exponential
import sys

# Add parent directory to system path (if needed)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
JSON_FILES_DIR = r"C:\Cursor_Projects\pytest_project_02 -_UI Framework\Edit1_jsons"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
MAX_CONCURRENT_REQUESTS = 5  # Adjust based on system capabilities
API_ENDPOINT = "http://localhost:5000/process"  # Update with actual endpoint
TIMEOUT_SECONDS = 120  # Timeout for API requests
CHUNK_SIZE = 50000  # Number of records to process in chunks for large files
MAX_RETRIES = 3  # Maximum number of retries for failed requests
RETRY_DELAY = 2  # Base delay between retries (seconds)

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logging
log_file = os.path.join(LOG_DIR, f"json_processor_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JSONProcessor:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        self.json_files_dir = JSON_FILES_DIR  # Allow this to be overridden

    async def process_json_files(self):
        """Process all JSON files in the specified directory asynchronously"""
        self.start_time = time.time()
        logger.info(f"Starting JSON processing from directory: {self.json_files_dir}")
        
        # Get list of JSON files
        json_files = glob.glob(os.path.join(self.json_files_dir, "*.json"))
        if not json_files:
            logger.warning(f"No JSON files found in {self.json_files_dir}")
            return []
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        # Create a semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        # Process files concurrently with semaphore
        tasks = [
            self.process_file(file_path, semaphore)
            for file_path in json_files
        ]
        
        # Wait for all tasks to complete
        self.results = await asyncio.gather(*tasks)
        
        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time
        
        # Filter out None results (failed processing)
        self.results = [r for r in self.results if r is not None]
        
        logger.info(f"Completed processing {len(self.results)} files in {elapsed_time:.2f} seconds")
        return self.results

    async def process_file(self, file_path, semaphore):
        """Process a single JSON file and send API request"""
        filename = os.path.basename(file_path)
        
        try:
            logger.info(f"Reading file: {filename}")
            
            # Read JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check if the file is large and needs chunking
            is_large_file = self._is_large_json(data)
            
            if is_large_file:
                logger.info(f"Large JSON detected in {filename}, processing in chunks")
                return await self._process_large_json(filename, data, semaphore)
            else:
                logger.info(f"Processing regular JSON file: {filename}")
                return await self._process_regular_json(filename, data, semaphore)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in {filename}: {str(e)}")
            return {
                'filename': filename,
                'status': 'error',
                'error_type': 'json_decode',
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'filename': filename,
                'status': 'error',
                'error_type': 'processing',
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _is_large_json(self, data):
        """Determine if a JSON is large and needs special handling"""
        # Estimate size by serializing a small sample
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
            # If data is in a 'data' field and it's a list
            return len(data['data']) > CHUNK_SIZE
        elif isinstance(data, list):
            # If the root element is a list
            return len(data) > CHUNK_SIZE
            
        # Get a rough size estimate by converting to string
        try:
            sample = str(data)[:1000]  # Take a small sample to estimate size
            if len(sample) > 900:  # If the sample is large, likely a big JSON
                return True
        except:
            pass
            
        return False  # Default to regular processing

    async def _process_regular_json(self, filename, data, semaphore):
        """Process a regular-sized JSON file"""
        async with semaphore:
            try:
                # Retry mechanism for API calls
                response_data = await self._send_api_request(data)
                
                # Save response to file
                response_file = os.path.join(OUTPUT_DIR, f"response_{filename}")
                with open(response_file, 'w') as f:
                    json.dump(response_data, f, indent=2)
                
                logger.info(f"Processed {filename} successfully")
                
                return {
                    'filename': filename,
                    'status': 'success',
                    'response_size': len(json.dumps(response_data)),
                    'response_file': response_file,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error in API request for {filename}: {str(e)}")
                return {
                    'filename': filename,
                    'status': 'error',
                    'error_type': 'api_request',
                    'error_message': str(e),
                    'timestamp': datetime.now().isoformat()
                }

    async def _process_large_json(self, filename, data, semaphore):
        """Process a large JSON file by chunking it"""
        logger.info(f"Breaking down large JSON {filename} into chunks")
        
        # Determine chunking strategy based on data structure
        chunks = []
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
            # If data is in a 'data' field which is a list
            items = data['data']
            template = {k: v for k, v in data.items() if k != 'data'}
            
            # Calculate number of chunks
            num_chunks = math.ceil(len(items) / CHUNK_SIZE)
            logger.info(f"Splitting {len(items)} items into {num_chunks} chunks")
            
            # Create chunks
            for i in range(0, len(items), CHUNK_SIZE):
                chunk_data = template.copy()
                chunk_data['data'] = items[i:i + CHUNK_SIZE]
                chunk_data['chunk_info'] = {
                    'original_file': filename,
                    'chunk_index': i // CHUNK_SIZE + 1,
                    'total_chunks': num_chunks,
                    'items_in_chunk': len(chunk_data['data'])
                }
                chunks.append(chunk_data)
                
        elif isinstance(data, list):
            # If the root element is a list
            items = data
            num_chunks = math.ceil(len(items) / CHUNK_SIZE)
            logger.info(f"Splitting {len(items)} items into {num_chunks} chunks")
            
            for i in range(0, len(items), CHUNK_SIZE):
                chunk_data = items[i:i + CHUNK_SIZE]
                # Add metadata as first item
                chunks.append({
                    'data': chunk_data,
                    'chunk_info': {
                        'original_file': filename,
                        'chunk_index': i // CHUNK_SIZE + 1,
                        'total_chunks': num_chunks,
                        'items_in_chunk': len(chunk_data)
                    }
                })
        else:
            # For other structures, just use the size-based chunking
            chunks = [{
                'data': data,
                'chunk_info': {
                    'original_file': filename,
                    'chunk_index': 1,
                    'total_chunks': 1,
                    'approximate_size': 'large'
                }
            }]
        
        # Process each chunk
        chunk_results = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)} for {filename}")
            
            async with semaphore:
                try:
                    # Send API request for this chunk
                    response_data = await self._send_api_request(chunk)
                    
                    # Save chunk response
                    chunk_file = os.path.join(OUTPUT_DIR, f"response_{filename}_chunk{i+1}of{len(chunks)}.json")
                    with open(chunk_file, 'w') as f:
                        json.dump(response_data, f, indent=2)
                    
                    chunk_results.append({
                        'chunk_index': i+1,
                        'status': 'success',
                        'response_file': chunk_file
                    })
                    
                    logger.info(f"Successfully processed chunk {i+1}/{len(chunks)} for {filename}")
                    
                except Exception as e:
                    logger.error(f"Error processing chunk {i+1}/{len(chunks)} for {filename}: {str(e)}")
                    chunk_results.append({
                        'chunk_index': i+1,
                        'status': 'error',
                        'error_message': str(e)
                    })
        
        # Summarize chunk processing results
        successful_chunks = sum(1 for r in chunk_results if r['status'] == 'success')
        
        # If all chunks were successful, merge results if appropriate
        if successful_chunks == len(chunks) and len(chunks) > 1:
            logger.info(f"All {len(chunks)} chunks processed successfully for {filename}")
            
            # Attempt to merge chunk responses into a single file if feasible
            try:
                self._merge_chunk_responses(filename, chunk_results)
            except Exception as e:
                logger.warning(f"Could not merge chunk responses for {filename}: {str(e)}")
        
        return {
            'filename': filename,
            'status': 'chunked',
            'total_chunks': len(chunks),
            'successful_chunks': successful_chunks,
            'failed_chunks': len(chunks) - successful_chunks,
            'chunk_results': chunk_results,
            'timestamp': datetime.now().isoformat()
        }

    def _merge_chunk_responses(self, filename, chunk_results):
        """Attempt to merge chunked responses into a single file"""
        logger.info(f"Attempting to merge chunk responses for {filename}")
        
        # Collect all chunk responses
        merged_data = {}
        merged_items = []
        
        for chunk in chunk_results:
            if chunk['status'] == 'success':
                with open(chunk['response_file'], 'r') as f:
                    chunk_data = json.load(f)
                
                # Extract items from the response
                if isinstance(chunk_data, dict) and 'processed_data' in chunk_data:
                    # Extract from API response structure
                    proc_data = chunk_data['processed_data']
                    
                    # Initialize merged data structure if this is the first chunk
                    if not merged_data:
                        merged_data = {k: v for k, v in proc_data.items() 
                                      if k != 'data' and k != 'chunk_info'}
                    
                    # Extract and append data items
                    if 'data' in proc_data and isinstance(proc_data['data'], list):
                        merged_items.extend(proc_data['data'])
                
                elif isinstance(chunk_data, list):
                    # If response is a list, simply extend
                    merged_items.extend(chunk_data)
        
        # Create merged file if we have items
        if merged_items:
            if merged_data:
                # For dict structure with 'data' field
                merged_data['data'] = merged_items
                merged_data['merged_info'] = {
                    'original_file': filename,
                    'chunk_count': len(chunk_results),
                    'total_items': len(merged_items)
                }
                
                # Save merged response
                merged_file = os.path.join(OUTPUT_DIR, f"merged_response_{filename}")
                with open(merged_file, 'w') as f:
                    json.dump(merged_data, f, indent=2)
                
                logger.info(f"Successfully merged {len(chunk_results)} chunks for {filename} with {len(merged_items)} items")
            else:
                # For list structure
                merged_file = os.path.join(OUTPUT_DIR, f"merged_response_{filename}")
                with open(merged_file, 'w') as f:
                    json.dump(merged_items, f, indent=2)
                
                logger.info(f"Successfully merged {len(chunk_results)} chunks for {filename} with {len(merged_items)} items")

    @retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=RETRY_DELAY))
    async def _send_api_request(self, data):
        """Send API request with retry logic"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    API_ENDPOINT, 
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API request failed with status {response.status}: {error_text}")
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                    
                    # Parse JSON response
                    return await response.json()
                    
            except aiohttp.ClientError as e:
                logger.error(f"Network error in API request: {str(e)}")
                raise
            except asyncio.TimeoutError:
                logger.error(f"API request timed out after {TIMEOUT_SECONDS} seconds")
                raise Exception(f"API request timed out after {TIMEOUT_SECONDS} seconds")
            except Exception as e:
                logger.error(f"Unexpected error in API request: {str(e)}")
                raise

    def save_results_to_excel(self):
        """Save processing results to Excel"""
        if not self.results:
            logger.warning("No results to save to Excel")
            return None
        
        try:
            # Create summary data
            summary_data = []
            
            for result in self.results:
                row = {
                    'Filename': result.get('filename', ''),
                    'Status': result.get('status', ''),
                    'Timestamp': result.get('timestamp', ''),
                    'Processing Time (s)': round(self.end_time - self.start_time, 2) if self.end_time and self.start_time else None
                }
                
                # Add fields based on status
                if result.get('status') == 'success':
                    row.update({
                        'Response Size': result.get('response_size', ''),
                        'Response File': result.get('response_file', '')
                    })
                elif result.get('status') == 'chunked':
                    row.update({
                        'Total Chunks': result.get('total_chunks', 0),
                        'Successful Chunks': result.get('successful_chunks', 0),
                        'Failed Chunks': result.get('failed_chunks', 0)
                    })
                elif result.get('status') == 'error':
                    row.update({
                        'Error Type': result.get('error_type', ''),
                        'Error Message': result.get('error_message', '')
                    })
                
                summary_data.append(row)
            
            # Create DataFrame and save to Excel
            df = pd.DataFrame(summary_data)
            excel_path = os.path.join(OUTPUT_DIR, f"processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Summary', index=False)
                
                # If we have chunked results, add a sheet with detailed chunk info
                chunked_results = [r for r in self.results if r.get('status') == 'chunked']
                if chunked_results:
                    chunk_details = []
                    for result in chunked_results:
                        for chunk in result.get('chunk_results', []):
                            chunk_details.append({
                                'Filename': result.get('filename', ''),
                                'Chunk Index': chunk.get('chunk_index', ''),
                                'Status': chunk.get('status', ''),
                                'Response File': chunk.get('response_file', '') if chunk.get('status') == 'success' else '',
                                'Error Message': chunk.get('error_message', '') if chunk.get('status') == 'error' else ''
                            })
                    
                    if chunk_details:
                        pd.DataFrame(chunk_details).to_excel(writer, sheet_name='Chunk Details', index=False)
            
            logger.info(f"Results saved to Excel: {excel_path}")
            return excel_path
            
        except Exception as e:
            logger.error(f"Error saving results to Excel: {str(e)}")
            return None

    def save_to_database(self, db_type='sqlite', connection_string=None):
        """Save results to database"""
        try:
            # Import the database storage module
            from db_storage import get_db_connection
            
            # Connect to database
            db = get_db_connection(db_type=db_type, connection_string=connection_string)
            
            # Save results
            db_result = db.save_processing_results(self.results)
            
            if db_result.get('status') == 'success':
                logger.info(f"Successfully saved {db_result.get('records_saved', 0)} records to database")
                return db_result
            else:
                logger.error(f"Failed to save to database: {db_result.get('error', 'Unknown error')}")
                return db_result
                
        except ImportError:
            logger.error("Database module not found. Run 'pip install -r requirements.txt' to install dependencies.")
            return {'status': 'error', 'error': 'Database module not found'}
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def process_folder(self, folder_path, edit_id="Edit 1"):
        """Process all JSON files in a specific folder"""
        logger.info(f"Processing all JSON files in folder: {folder_path}")
        
        # Check if folder exists
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return {
                'status': 'error',
                'message': f'Folder not found: {folder_path}'
            }
        
        # Start timing
        self.start_time = time.time()
        
        # Build the request data
        request_data = {
            'folder_path': folder_path,
            'edit_id': edit_id
        }
        
        try:
            # Create a semaphore for API requests
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
            
            # Send a single request to process all files in the folder
            async with semaphore:
                try:
                    # Send the API request
                    response_data = await self._send_api_request(request_data)
                    
                    # Save response to file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    response_file = os.path.join(OUTPUT_DIR, f"folder_response_{timestamp}.json")
                    with open(response_file, 'w') as f:
                        json.dump(response_data, f, indent=2)
                    
                    logger.info(f"Processed folder {folder_path} successfully")
                    
                    # Get statistics
                    total_files = response_data.get('total_files', 0)
                    successful = response_data.get('successful', 0)
                    failed = response_data.get('failed', 0)
                    
                    # Create a result for Excel report
                    result = {
                        'folder_path': folder_path,
                        'status': 'success',
                        'total_files': total_files,
                        'successful_files': successful,
                        'failed_files': failed,
                        'edit_id': edit_id,
                        'response_file': response_file,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    self.results = [result]
                    self.end_time = time.time()
                    
                    return response_data
                    
                except Exception as e:
                    logger.error(f"Error in API request for folder {folder_path}: {str(e)}")
                    self.results = [{
                        'folder_path': folder_path,
                        'status': 'error',
                        'error_type': 'api_request',
                        'error_message': str(e),
                        'timestamp': datetime.now().isoformat()
                    }]
                    self.end_time = time.time()
                    
                    return {
                        'status': 'error',
                        'message': f'Failed to process folder {folder_path}',
                        'error': str(e)
                    }
        
        except Exception as e:
            logger.error(f"Error processing folder {folder_path}: {str(e)}")
            logger.error(traceback.format_exc())
            
            self.end_time = time.time()
            return {
                'status': 'error',
                'message': f'Failed to process folder {folder_path}',
                'error': str(e)
            }

async def process_edit1_jsons():
    """Process all JSON files in the Edit1_jsons directory"""
    # Create an instance of JSONProcessor
    processor = JSONProcessor()
    
    # Override the default directory
    processor.json_files_dir = JSON_FILES_DIR
    
    print(f"Processing JSON files from: {JSON_FILES_DIR}")
    print(f"Results will be saved to: {OUTPUT_DIR}")
    print(f"Logs will be saved to: {LOG_DIR}")
    
    # Process the files
    results = await processor.process_json_files()
    
    # Save results to Excel
    excel_path = processor.save_results_to_excel()
    
    if excel_path:
        print(f"Results saved to Excel: {excel_path}")
    
    return results

if __name__ == "__main__":
    # Ensure the output and log directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Run the async function
    asyncio.run(process_edit1_jsons()) 