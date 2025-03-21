#!/usr/bin/env python3
"""
Setup script for installing all required dependencies for the 
Large-Scale JSON Processing & API Integration project
"""

import subprocess
import sys
import os
import platform

def main():
    """Install all required dependencies"""
    print("Setting up Large-Scale JSON Processing & API Integration project...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        print("Error: pip is not available. Please install pip first.")
        sys.exit(1)
    
    # Install dependencies from requirements.txt if it exists
    if os.path.exists("requirements.txt"):
        print("\nInstalling dependencies from requirements.txt...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✓ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("Error: Failed to install dependencies from requirements.txt")
            
            # Try installing critical packages individually
            print("\nTrying to install critical packages individually...")
            critical_packages = [
                "aiohttp",
                "pandas",
                "openpyxl",
                "sqlalchemy",
                "tenacity",
                "requests"
            ]
            
            for package in critical_packages:
                try:
                    print(f"Installing {package}...")
                    subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                    print(f"✓ {package} installed successfully!")
                except subprocess.CalledProcessError:
                    print(f"× Failed to install {package}")
    else:
        # If requirements.txt doesn't exist, install critical packages
        print("\nNo requirements.txt found. Installing critical packages...")
        critical_packages = [
            "aiohttp",
            "pandas",
            "openpyxl",
            "sqlalchemy",
            "tenacity",
            "requests"
        ]
        
        for package in critical_packages:
            try:
                print(f"Installing {package}...")
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                print(f"✓ {package} installed successfully!")
            except subprocess.CalledProcessError:
                print(f"× Failed to install {package}")
    
    # Create necessary directories
    print("\nCreating necessary directories...")
    os.makedirs("logs", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # Create sample directory for JSON files
    json_dir = r"C:\json_files"
    try:
        os.makedirs(json_dir, exist_ok=True)
        print(f"✓ Created directory: {json_dir}")
    except Exception as e:
        print(f"× Could not create {json_dir}: {str(e)}")
        print("You may need to create this directory manually.")
    
    print("\nSetup complete!")
    print("\nYou can now run the project using:")
    print("python run.py generate   # Generate test JSON files")
    print("python run.py process    # Process JSON files")
    print("python run.py all        # Do everything")

if __name__ == "__main__":
    main() 