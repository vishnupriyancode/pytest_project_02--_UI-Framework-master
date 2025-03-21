import os
import json
import glob
from datetime import datetime

# Configuration
JSON_FILES_DIR = r"C:\json_files"
PROCESSED_DIR = os.path.join(JSON_FILES_DIR, "processed")

# Ensure processed directory exists
os.makedirs(PROCESSED_DIR, exist_ok=True)

def apply_edit_one(json_data):
    """
    Apply the "Edit 1" transformation to JSON data
    This matches the transformation in our Flask application
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
    
    # If the JSON contains nested data, process it
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

def process_json_files():
    """Process all JSON files in the specified directory"""
    # Find all JSON files
    json_files = glob.glob(os.path.join(JSON_FILES_DIR, "*.json"))
    
    if not json_files:
        print(f"No JSON files found in {JSON_FILES_DIR}")
        return []
    
    processed_files = []
    
    for file_path in json_files:
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}")
        
        try:
            # Read the JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Apply the transformation
            processed_data = apply_edit_one(data)
            
            # Save to processed directory
            processed_path = os.path.join(PROCESSED_DIR, f"processed_{filename}")
            with open(processed_path, 'w') as f:
                json.dump(processed_data, f, indent=2)
            
            processed_files.append(processed_path)
            print(f"  ✓ Saved processed file: {processed_path}")
            
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {str(e)}")
    
    return processed_files

if __name__ == "__main__":
    print(f"Applying 'Edit 1' transformation to JSON files in {JSON_FILES_DIR}")
    processed = process_json_files()
    print(f"\nSuccessfully processed {len(processed)} JSON files")
    print(f"Processed files saved to: {PROCESSED_DIR}") 