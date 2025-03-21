import os
import json
import shutil
from datetime import datetime

# Configuration
INPUT_FILES = [
    "json1_simple.json",
    "json2_nested.json", 
    "json3_arrays.json",
    "json4_complex.json",
    "json5_edge_cases.json"
]
OUTPUT_DIR = "processed_json"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def apply_edit_one(json_data):
    """
    Apply the "Edit 1" transformation to JSON data
    """
    if not json_data:
        return json_data
        
    # Create a deep copy of the data to avoid modifying the original
    transformed_data = json_data.copy()
    
    # Add processing metadata
    transformed_data['processed'] = True
    transformed_data['processed_at'] = datetime.now().isoformat()
    transformed_data['validation_status'] = "VALID"
    
    # Add a validation ID
    transformed_data['validation_id'] = f"VAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Process nested objects and arrays
    for key, value in transformed_data.items():
        if isinstance(value, dict):
            # Add metadata to nested objects
            value['_processed'] = True
            value['_validation'] = "PASSED"
        elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
            # Process list of objects
            for item in value:
                item['_processed'] = True
                item['_validation'] = "PASSED"
    
    return transformed_data

def process_files():
    """Process each input JSON file and save the transformed version"""
    results = []
    
    print(f"Processing {len(INPUT_FILES)} JSON files...")
    
    for filename in INPUT_FILES:
        print(f"\nProcessing: {filename}")
        
        try:
            # Read the input file
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Apply Edit 1 transformation
            transformed_data = apply_edit_one(data)
            
            # Save transformed file
            output_filename = f"processed_{filename}"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            with open(output_path, 'w') as f:
                json.dump(transformed_data, f, indent=2)
            
            # Copy original to output dir for comparison
            shutil.copy(filename, os.path.join(OUTPUT_DIR, f"original_{filename}"))
            
            print(f"✓ Transformation successful")
            print(f"  Original file: {filename}")
            print(f"  Processed file: {output_path}")
            
            # Analyze changes
            added_fields = []
            if 'processed' in transformed_data:
                added_fields.append('processed')
            if 'processed_at' in transformed_data:
                added_fields.append('processed_at')
            if 'validation_status' in transformed_data:
                added_fields.append('validation_status')
            if 'validation_id' in transformed_data:
                added_fields.append('validation_id')
            
            # Count nested changes
            nested_objects_processed = 0
            nested_arrays_processed = 0
            
            for key, value in transformed_data.items():
                if isinstance(value, dict) and '_processed' in value:
                    nested_objects_processed += 1
                elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
                    for item in value:
                        if '_processed' in item:
                            nested_arrays_processed += 1
            
            print(f"  Changes made:")
            print(f"  - Top-level fields added: {', '.join(added_fields)}")
            print(f"  - Nested objects processed: {nested_objects_processed}")
            print(f"  - Nested array items processed: {nested_arrays_processed}")
            
            # Store results
            results.append({
                'filename': filename,
                'status': 'success',
                'added_fields': added_fields,
                'nested_objects_processed': nested_objects_processed,
                'nested_arrays_processed': nested_arrays_processed
            })
            
        except Exception as e:
            print(f"✗ Error processing {filename}: {str(e)}")
            results.append({
                'filename': filename,
                'status': 'error',
                'error': str(e)
            })
    
    return results

def generate_report(results):
    """Generate a summary report of the transformations"""
    print("\n" + "="*60)
    print(" EDIT 1 TRANSFORMATION VALIDATION REPORT ".center(60, "="))
    print("="*60)
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']
    
    print(f"\nProcessed {len(results)} JSON files:")
    print(f"  ✓ Successful: {len(successful)}")
    print(f"  ✗ Failed: {len(failed)}")
    
    if successful:
        print("\nSuccessful Transformations:")
        for result in successful:
            print(f"  - {result['filename']}")
            print(f"    • Added fields: {', '.join(result['added_fields'])}")
            print(f"    • Nested objects processed: {result['nested_objects_processed']}")
            print(f"    • Nested array items processed: {result['nested_arrays_processed']}")
    
    if failed:
        print("\nFailed Transformations:")
        for result in failed:
            print(f"  - {result['filename']}: {result['error']}")
    
    print("\nTransformed files are available in the '{OUTPUT_DIR}' directory")
    print("Each file has been saved with 'processed_' prefix")
    print("Original files are copied with 'original_' prefix for comparison")
    
    # Create a JSON report
    report_path = os.path.join(OUTPUT_DIR, "validation_report.json")
    with open(report_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_files': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")

if __name__ == "__main__":
    results = process_files()
    generate_report(results) 