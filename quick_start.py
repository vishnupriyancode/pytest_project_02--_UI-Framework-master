#!/usr/bin/env python3
"""
Quick Start script to help users get started with the Large JSON Processing system.
This script will guide you through the installation and running of the system.
"""

import os
import sys
import subprocess
import time
import webbrowser
import platform

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def run_command(command, wait=True):
    """Run a command and return the output"""
    print(f"Running: {command}")
    
    try:
        if wait:
            result = subprocess.run(command, shell=True, check=True, text=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout
        else:
            # Start process without waiting
            if platform.system() == "Windows":
                subprocess.Popen(f"start cmd /k {command}", shell=True)
            else:
                subprocess.Popen(f"gnome-terminal -- {command}", shell=True)
            return "Process started in new window"
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("Error: Python 3.7 or higher is required.")
        print(f"Your current Python version is {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"Python version {version.major}.{version.minor}.{version.micro} is compatible.")
    return True

def check_dependencies():
    """Check if dependencies are installed"""
    print("Checking dependencies...")
    
    try:
        # Check if pip is available
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("Error: pip is not available. Please install pip first.")
        return False
    
    # Check for key dependencies
    dependencies = ["aiohttp", "pandas", "flask"]
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        choice = input("Would you like to install missing dependencies now? (y/n): ")
        
        if choice.lower() == 'y':
            print("Installing dependencies...")
            run_command(f"{sys.executable} setup.py")
            return True
        else:
            print("Please install the missing dependencies before continuing.")
            return False
    
    print("All dependencies are installed.")
    return True

def main_menu():
    """Display the main menu"""
    while True:
        print_header("Large JSON Processing System - Quick Start")
        print("1. Setup environment (Install dependencies)")
        print("2. Generate test JSON files")
        print("3. Start mock API server")
        print("4. Process JSON files")
        print("5. Process Edit1_jsons folder")
        print("6. Process custom folder")
        print("7. Run everything (Generate + Process)")
        print("8. View README")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-8): ")
        
        if choice == '0':
            print("Exiting...")
            sys.exit(0)
        elif choice == '1':
            run_command(f"{sys.executable} setup.py")
            input("\nPress Enter to continue...")
        elif choice == '2':
            run_command(f"{sys.executable} run.py generate")
            input("\nPress Enter to continue...")
        elif choice == '3':
            print("Starting mock API server in a new window...")
            run_command(f"{sys.executable} mock_api.py", wait=False)
            print("Mock API server should be running at http://localhost:5000")
            time.sleep(2)  # Give the server time to start
            input("\nPress Enter to continue...")
        elif choice == '4':
            print("Processing JSON files...")
            run_command(f"{sys.executable} run.py process")
            input("\nPress Enter to continue...")
        elif choice == '5':
            print("Processing Edit1_jsons folder...")
            run_command(f"{sys.executable} run.py process-edit1")
            input("\nPress Enter to continue...")
        elif choice == '6':
            # Process custom folder
            folder_path = input("\nEnter the folder path containing JSON files: ")
            if folder_path:
                print(f"Processing folder: {folder_path}...")
                run_command(f"{sys.executable} run.py process-folder --folder-path \"{folder_path}\"")
            else:
                print("No folder path provided.")
            input("\nPress Enter to continue...")
        elif choice == '7':
            print("Running complete workflow...")
            print("First, starting mock API server...")
            run_command(f"{sys.executable} mock_api.py", wait=False)
            time.sleep(2)  # Give the server time to start
            print("Now generating and processing files...")
            run_command(f"{sys.executable} run.py all")
            input("\nPress Enter to continue...")
        elif choice == '8':
            # Show README
            if os.path.exists("README.md"):
                print("\nOpening README in browser (if possible)...")
                try:
                    # Convert markdown to HTML and display in browser
                    readme_path = os.path.abspath("README.md")
                    webbrowser.open(f"file://{readme_path}")
                except:
                    # If that fails, just print it
                    with open("README.md", "r") as f:
                        print("\n" + f.read())
            else:
                print("README.md not found.")
            input("\nPress Enter to continue...")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    print_header("Large JSON Processing System - Quick Start")
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        choice = input("Would you like to continue anyway? (y/n): ")
        if choice.lower() != 'y':
            sys.exit(1)
    
    # Show main menu
    main_menu() 