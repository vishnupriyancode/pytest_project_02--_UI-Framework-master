import os
import json
import requests
import glob
import pandas as pd
from datetime import datetime

# Configuration
JSON_FILES_DIR = r"C:\json_files"
PROCESSED_DIR = os.path.join(JSON_FILES_DIR, "processed")
API_URL = "http://localhost:5000/process"  # Flask API endpoint
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

# Ensure directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def test_api_with_json_files():
    """Test the API with all processed JSON files"""
    # Find all processed JSON files
    json_files = glob.glob(os.path.join(PROCESSED_DIR, "*.json"))
    
    if not json_files:
        print(f"No processed JSON files found in {PROCESSED_DIR}")
        print(f"Run apply_edit1.py first to generate processed files.")
        return
    
    results = []
    
    for file_path in json_files:
        filename = os.path.basename(file_path)
        print(f"Testing API with: {filename}")
        
        try:
            # Read the JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Send POST request to API
            response = requests.post(API_URL, json=data)
            
            # Check response
            if response.status_code == 200:
                response_data = response.json()
                print(f"  ✓ API response: {response.status_code} - Success")
                
                # Store result
                results.append({
                    'filename': filename,
                    'status_code': response.status_code,
                    'success': True,
                    'response': response_data,
                    'validation_status': data.get('validation_status', 'UNKNOWN'),
                    'timestamp': datetime.now().isoformat()
                })
            else:
                print(f"  ✗ API response: {response.status_code} - Failed")
                results.append({
                    'filename': filename,
                    'status_code': response.status_code,
                    'success': False,
                    'error': response.text,
                    'validation_status': data.get('validation_status', 'UNKNOWN'),
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"  ✗ Error testing {filename}: {str(e)}")
            results.append({
                'filename': filename,
                'status_code': None,
                'success': False,
                'error': str(e),
                'validation_status': 'ERROR',
                'timestamp': datetime.now().isoformat()
            })
    
    return results

def save_results_to_excel(results):
    """Save test results to Excel file"""
    if not results:
        print("No results to save.")
        return
    
    # Prepare data for Excel
    excel_data = []
    
    for result in results:
        row = {
            'Filename': result.get('filename', ''),
            'Status Code': result.get('status_code', ''),
            'Success': result.get('success', False),
            'Validation Status': result.get('validation_status', ''),
            'Timestamp': result.get('timestamp', ''),
        }
        
        # Add response details if successful
        if result.get('success'):
            response = result.get('response', {})
            row['API Status'] = response.get('status', '')
            row['API Message'] = response.get('message', '')
            
            # Add some processed data details if available
            processed_data = response.get('processed_data', {})
            if processed_data:
                row['Has Processed Data'] = True
                row['Processed At'] = processed_data.get('processed_at', '')
        else:
            row['Error'] = result.get('error', '')
        
        excel_data.append(row)
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(excel_data)
    excel_path = os.path.join(RESULTS_DIR, f"api_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    df.to_excel(excel_path, index=False)
    
    print(f"\nSaved test results to: {excel_path}")
    return excel_path

if __name__ == "__main__":
    print("Testing the API with processed JSON files...")
    print(f"API Endpoint: {API_URL}")
    
    # Check if Flask API is running
    try:
        requests.get(API_URL.replace('/process', ''))
        print("API is accessible.\n")
    except requests.exceptions.ConnectionError:
        print("WARNING: API doesn't appear to be running. Start the Flask app first (python app.py).\n")
    
    # Test the API
    results = test_api_with_json_files()
    
    if results:
        # Calculate statistics
        total = len(results)
        successful = sum(1 for r in results if r.get('success', False))
        failed = total - successful
        
        print(f"\nTest Summary:")
        print(f"  Total Files Tested: {total}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        
        # Save results to Excel
        excel_path = save_results_to_excel(results)
    else:
        print("\nNo test results were generated.") 