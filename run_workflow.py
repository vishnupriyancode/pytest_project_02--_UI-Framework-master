import os
import subprocess
import time
import sys

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def run_command(command, description):
    """Run a command and print its output"""
    print_header(description)
    
    try:
        # Run the command and capture output
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
        
        # Wait for process to complete
        process.wait()
        
        if process.returncode != 0:
            print(f"\nWarning: Command exited with code {process.returncode}")
            return False
        
        return True
    
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return False

def check_api_running():
    """Check if the Flask API is running"""
    import requests
    
    try:
        response = requests.get("http://localhost:5000/")
        return True
    except:
        return False

def main():
    """Run the complete workflow"""
    print_header("JSON Processing Workflow")
    print("This script will run the entire workflow:\n")
    print("1. Generate sample JSON files")
    print("2. Apply 'Edit 1' transformation to the JSON files")
    print("3. Test the API with the processed files")
    print("4. Save results to Excel\n")
    
    # Check if Python is installed
    if not run_command("python --version", "Checking Python Installation"):
        print("Python is not installed or not in PATH.")
        return
    
    # Check if Flask API is running
    print_header("Checking if Flask API is Running")
    if check_api_running():
        print("✓ Flask API is running on http://localhost:5000")
    else:
        print("✗ Flask API is not running")
        start_api = input("Do you want to start the Flask API? (y/n): ").lower().strip()
        
        if start_api == 'y':
            # Start Flask API in a new process
            print("Starting Flask API in a new window...")
            
            if sys.platform == 'win32':
                subprocess.Popen("start cmd /k python app.py", shell=True)
            else:
                subprocess.Popen("python app.py &", shell=True)
            
            print("Waiting for API to start...")
            time.sleep(5)  # Give the API time to start
        else:
            print("\nNOTE: The API testing part will fail if the API is not running.")
            proceed = input("Do you want to proceed with the workflow anyway? (y/n): ").lower().strip()
            if proceed != 'y':
                print("Workflow aborted.")
                return
    
    # 1. Generate sample JSON files
    run_command("python sample_edit.py", "Generating Sample JSON Files")
    
    # 2. Apply 'Edit 1' transformation
    run_command("python apply_edit1.py", "Applying 'Edit 1' Transformation")
    
    # 3. Test the API with processed files
    run_command("python test_api.py", "Testing API with Processed Files")
    
    print_header("Workflow Complete")
    print("The workflow has been completed.\n")
    print("Results directories:")
    print(f"  - Original JSON files: C:\\json_files\\")
    print(f"  - Processed JSON files: C:\\json_files\\processed\\")
    print(f"  - Test results: {os.path.join(os.path.dirname(__file__), 'results')}")
    print(f"  - Excel exports: {os.path.join(os.path.dirname(__file__), 'output')}")

if __name__ == "__main__":
    main() 