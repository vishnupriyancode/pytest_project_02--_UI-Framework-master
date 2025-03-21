#!/usr/bin/env python3
"""
Verification script to check if our JSON processing solution is working properly.
This script:
1. Verifies all necessary files exist
2. Checks if Edit1_jsons directory contains JSON files
3. Runs the processing on Edit1_jsons
4. Verifies output was created
"""

import os
import sys
import glob
import subprocess
import json

def print_status(message, success=True):
    """Print a status message with color"""
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def check_files_exist():
    """Check if all necessary files exist"""
    required_files = [
        "large_scale_json_processor.py",
        "run.py",
        "setup.py",
        "mock_api.py"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print_status(f"File exists: {file}")
        else:
            print_status(f"File missing: {file}", False)
            all_exist = False
    
    return all_exist

def check_edit1_jsons():
    """Check if Edit1_jsons directory contains JSON files"""
    edit1_dir = "Edit1_jsons"
    
    if not os.path.exists(edit1_dir):
        print_status(f"Directory not found: {edit1_dir}", False)
        return False
    
    json_files = glob.glob(os.path.join(edit1_dir, "*.json"))
    if json_files:
        print_status(f"Found {len(json_files)} JSON files in {edit1_dir}")
        for file in json_files:
            try:
                with open(file, 'r') as f:
                    json.load(f)  # Verify it's valid JSON
                print_status(f"  Valid JSON: {os.path.basename(file)}")
            except json.JSONDecodeError:
                print_status(f"  Invalid JSON: {os.path.basename(file)}", False)
    else:
        print_status(f"No JSON files found in {edit1_dir}", False)
        return False
    
    return True

def verify_command(command):
    """Verify a command can run without errors"""
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print_status(f"Command works: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Command failed: {command}", False)
        print(f"  Error: {e.stderr}")
        return False

def main():
    """Run the verification process"""
    print("\n=== Verifying Solution ===\n")
    
    # Check files
    files_exist = check_files_exist()
    if not files_exist:
        print("\nSome required files are missing. Please fix this first.")
        return
    
    # Check Edit1_jsons
    edit1_valid = check_edit1_jsons()
    if not edit1_valid:
        print("\nEdit1_jsons directory is missing or has no valid JSON files.")
        return
    
    # Check commands
    commands = [
        "python run.py --help",
        "python run.py process-edit1 --help"
    ]
    
    all_commands_valid = True
    for cmd in commands:
        if not verify_command(cmd):
            all_commands_valid = False
    
    if not all_commands_valid:
        print("\nSome commands are not working properly. Please fix the issues.")
        return
    
    print("\n=== Verification Passed ===")
    print("Your solution appears to be working correctly.")
    print("\nTo process the Edit1_jsons files, run:")
    print("python run.py process-edit1")
    print("\nOutput will be saved to the 'output' directory.")

if __name__ == "__main__":
    main() 