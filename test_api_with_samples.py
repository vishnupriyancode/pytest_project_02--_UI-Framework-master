import os
import json
import requests
import pandas as pd
from datetime import datetime

# Configuration
INPUT_FILES = [
    "json1_simple.json",
    "json2_nested.json", 
    "json3_arrays.json",
    "json4_complex.json",
    "json5_edge_cases.json"
]
PROCESSED_DIR = "processed_json"
API_URL = "http://localhost:5000/process"  # Flask API endpoint
RESULTS_DIR = "api_results"

# Ensure directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def test_api_with_files():
    """Test the API with both original and processed JSON files"""
    results = []
    
    # First check if the API is running
    try:
        requests.get(API_URL.replace('/process', ''))
        print("✓ API is accessible\n")
    except requests.exceptions.ConnectionError:
        print("✗ API is not running! Please start the Flask API (python app.py) first.\n")
        return []
    
    print(f"Testing API with {len(INPUT_FILES)} JSON files...")
    
    # Test original files
    for filename in INPUT_FILES:
        print(f"\nTesting with original file: {filename}")
        
        try:
            # Read the original file
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Send POST request to API
            response = requests.post(API_URL, json=data)
            
            # Process response
            if response.status_code == 200:
                response_data = response.json()
                print(f"  ✓ API response: {response.status_code} - Success")
                
                # Check if the response has expected fields
                processed_data = response_data.get('processed_data', {})
                validation_fields = []
                
                if processed_data.get('processed') is True:
                    validation_fields.append('processed flag')
                if processed_data.get('processed_at'):
                    validation_fields.append('timestamp')
                if processed_data.get('validation_status'):
                    validation_fields.append('validation status')
                if processed_data.get('validation_id'):
                    validation_fields.append('validation ID')
                
                print(f"  ✓ Validation fields added: {', '.join(validation_fields)}")
                
                # Save the API response for comparison
                response_path = os.path.join(RESULTS_DIR, f"api_response_{filename}")
                with open(response_path, 'w') as f:
                    json.dump(response_data, f, indent=2)
                
                # Store result
                results.append({
                    'filename': filename,
                    'file_type': 'original',
                    'status_code': response.status_code,
                    'success': True,
                    'validation_fields': validation_fields,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                print(f"  ✗ API response: {response.status_code} - Failed")
                print(f"  Error: {response.text}")
                
                results.append({
                    'filename': filename,
                    'file_type': 'original',
                    'status_code': response.status_code,
                    'success': False,
                    'error': response.text,
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"  ✗ Error testing {filename}: {str(e)}")
            
            results.append({
                'filename': filename,
                'file_type': 'original',
                'status_code': None,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    # Now test processed files
    print("\nTesting with pre-processed files...")
    
    for filename in INPUT_FILES:
        processed_filename = f"processed_{filename}"
        processed_path = os.path.join(PROCESSED_DIR, processed_filename)
        
        # Skip if processed file doesn't exist
        if not os.path.exists(processed_path):
            print(f"\n  ✗ Processed file not found: {processed_path}")
            print(f"  Run validate_edit1.py first to generate processed files")
            continue
        
        print(f"\nTesting with pre-processed file: {processed_filename}")
        
        try:
            # Read the processed file
            with open(processed_path, 'r') as f:
                data = json.load(f)
            
            # Send POST request to API
            response = requests.post(API_URL, json=data)
            
            # Process response
            if response.status_code == 200:
                response_data = response.json()
                print(f"  ✓ API response: {response.status_code} - Success")
                
                # Check if the response maintained the validation fields
                processed_data = response_data.get('processed_data', {})
                maintained_fields = []
                
                if processed_data.get('validation_id') == data.get('validation_id'):
                    maintained_fields.append('validation ID')
                if processed_data.get('validation_status') == data.get('validation_status'):
                    maintained_fields.append('validation status')
                
                print(f"  ✓ Maintained fields: {', '.join(maintained_fields)}")
                
                # Save the API response for comparison
                response_path = os.path.join(RESULTS_DIR, f"api_response_{processed_filename}")
                with open(response_path, 'w') as f:
                    json.dump(response_data, f, indent=2)
                
                # Store result
                results.append({
                    'filename': processed_filename,
                    'file_type': 'processed',
                    'status_code': response.status_code,
                    'success': True,
                    'maintained_fields': maintained_fields,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                print(f"  ✗ API response: {response.status_code} - Failed")
                print(f"  Error: {response.text}")
                
                results.append({
                    'filename': processed_filename,
                    'file_type': 'processed',
                    'status_code': response.status_code,
                    'success': False,
                    'error': response.text,
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"  ✗ Error testing {processed_filename}: {str(e)}")
            
            results.append({
                'filename': processed_filename,
                'file_type': 'processed',
                'status_code': None,
                'success': False,
                'error': str(e),
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
            'File Type': result.get('file_type', ''),
            'Status Code': result.get('status_code', ''),
            'Success': result.get('success', False),
            'Timestamp': result.get('timestamp', ''),
        }
        
        # Add details based on success and file type
        if result.get('success'):
            if result.get('file_type') == 'original':
                row['Validation Fields'] = ', '.join(result.get('validation_fields', []))
            else:
                row['Maintained Fields'] = ', '.join(result.get('maintained_fields', []))
        else:
            row['Error'] = result.get('error', '')
        
        excel_data.append(row)
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(excel_data)
    excel_path = os.path.join(RESULTS_DIR, f"api_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    df.to_excel(excel_path, index=False)
    
    print(f"\nTest results saved to: {excel_path}")
    return excel_path

def generate_summary(results):
    """Generate a summary of test results"""
    print("\n" + "="*60)
    print(" API TESTING SUMMARY ".center(60, "="))
    print("="*60)
    
    if not results:
        print("\nNo test results available.")
        return
    
    # Separate by file type
    original_results = [r for r in results if r.get('file_type') == 'original']
    processed_results = [r for r in results if r.get('file_type') == 'processed']
    
    # Count successes and failures
    original_success = sum(1 for r in original_results if r.get('success', False))
    original_failure = len(original_results) - original_success
    
    processed_success = sum(1 for r in processed_results if r.get('success', False))
    processed_failure = len(processed_results) - processed_success
    
    # Print summary
    print("\nOriginal Files:")
    print(f"  Total: {len(original_results)}")
    print(f"  ✓ Successful: {original_success}")
    print(f"  ✗ Failed: {original_failure}")
    
    print("\nPre-processed Files:")
    print(f"  Total: {len(processed_results)}")
    print(f"  ✓ Successful: {processed_success}")
    print(f"  ✗ Failed: {processed_failure}")
    
    print("\nOverall:")
    print(f"  Total Tests: {len(results)}")
    print(f"  ✓ Total Successful: {original_success + processed_success}")
    print(f"  ✗ Total Failed: {original_failure + processed_failure}")
    
    # Save summary to JSON
    summary_path = os.path.join(RESULTS_DIR, "api_test_summary.json")
    with open(summary_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'original_files': {
                'total': len(original_results),
                'successful': original_success,
                'failed': original_failure
            },
            'processed_files': {
                'total': len(processed_results),
                'successful': processed_success,
                'failed': processed_failure
            },
            'overall': {
                'total': len(results),
                'successful': original_success + processed_success,
                'failed': original_failure + processed_failure
            }
        }, f, indent=2)
    
    print(f"\nSummary saved to: {summary_path}")

if __name__ == "__main__":
    print("Testing the Flask API with sample JSON files...")
    print(f"API Endpoint: {API_URL}\n")
    
    # Run tests
    results = test_api_with_files()
    
    if results:
        # Save results to Excel
        excel_path = save_results_to_excel(results)
        
        # Generate summary
        generate_summary(results)
    else:
        print("\nNo test results were generated.") 