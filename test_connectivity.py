import requests
import socket
import os
import json
import sys

def test_server_running():
    """Test if the server is running on localhost:5000"""
    try:
        response = requests.get('http://localhost:5000/test-connection', timeout=5)
        print(f"✅ Server is running on localhost:5000. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not accessible on localhost:5000: {e}")
        return False

def test_folder_processing():
    """Test folder processing API directly"""
    try:
        # Get the Edit1_jsons folder path
        base_path = os.path.abspath(os.path.dirname(__file__))
        edit1_folder = os.path.join(base_path, "Edit1_jsons")
        
        # Ensure the path exists
        if not os.path.exists(edit1_folder):
            print(f"❌ Folder not found: {edit1_folder}")
            return False
        
        # Escape backslashes for JSON
        json_path = edit1_folder.replace('\\', '\\\\')
        
        # Make the API request
        headers = {'Content-Type': 'application/json'}
        data = {
            'folder_path': json_path,
            'edit_id': 'Test Edit'
        }
        
        print(f"Sending request to process folder: {json_path}")
        response = requests.post(
            'http://localhost:5000/process-folder',
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"✅ API response status code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")  # Show first 500 chars
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error making API request: {e}")
        return False

def check_network_config():
    """Check network configuration for any issues"""
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    print(f"Host: {host_name}")
    print(f"IP Address: {ip_address}")
    
    # Check if localhost resolves properly
    try:
        localhost_ip = socket.gethostbyname('localhost')
        print(f"localhost resolves to: {localhost_ip}")
        if localhost_ip != '127.0.0.1':
            print("⚠️ Warning: localhost does not resolve to 127.0.0.1")
    except socket.error:
        print("❌ Error: Cannot resolve 'localhost'")

def main():
    """Run all tests"""
    print("📝 Testing Flask API Connectivity\n")
    
    print("1. Checking network configuration...")
    check_network_config()
    print("\n")
    
    print("2. Testing if server is running...")
    server_running = test_server_running()
    print("\n")
    
    if server_running:
        print("3. Testing folder processing API...")
        test_folder_processing()
    else:
        print("❌ Skipping API tests because server is not running.")
    
    print("\n📝 Testing completed.")

if __name__ == "__main__":
    main() 