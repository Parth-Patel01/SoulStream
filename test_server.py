#!/usr/bin/env python3
"""
Test script for SoulStream Media Server
This script tests all endpoints and functionality
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
SERVER_URL = "http://192.168.18.20:8080"
TEST_FILE = "test_movie.mp4"

def print_status(message, status="INFO"):
    """Print colored status message"""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"     # Reset
    }
    print(f"{colors.get(status, colors['INFO'])}[{status}]{colors['RESET']} {message}")

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_status("Health check passed", "SUCCESS")
            print(f"  Status: {data.get('status')}")
            print(f"  Upload folder: {data.get('upload_folder')}")
            print(f"  Folder exists: {data.get('upload_folder_exists')}")
            return True
        else:
            print_status(f"Health check failed with status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Health check error: {str(e)}", "ERROR")
        return False

def test_files_endpoint():
    """Test the files listing endpoint"""
    try:
        response = requests.get(f"{SERVER_URL}/files", timeout=10)
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            print_status(f"Files endpoint working - found {len(files)} files", "SUCCESS")
            for file in files:
                print(f"  - {file.get('name')} ({file.get('size')})")
            return True
        else:
            print_status(f"Files endpoint failed with status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Files endpoint error: {str(e)}", "ERROR")
        return False

def test_main_page():
    """Test the main page endpoint"""
    try:
        response = requests.get(SERVER_URL, timeout=10)
        if response.status_code == 200:
            print_status("Main page accessible", "SUCCESS")
            return True
        else:
            print_status(f"Main page failed with status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Main page error: {str(e)}", "ERROR")
        return False

def create_test_file():
    """Create a small test file for upload testing"""
    try:
        # Create a small test file (1KB)
        with open(TEST_FILE, 'wb') as f:
            f.write(b'0' * 1024)  # 1KB of zeros
        print_status(f"Created test file: {TEST_FILE}", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Failed to create test file: {str(e)}", "ERROR")
        return False

def test_upload():
    """Test file upload functionality"""
    if not os.path.exists(TEST_FILE):
        print_status("Test file not found, skipping upload test", "WARNING")
        return False
    
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {'file': (TEST_FILE, f, 'video/mp4')}
            response = requests.post(f"{SERVER_URL}/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_status("Upload test passed", "SUCCESS")
            print(f"  Uploaded: {data.get('filename')}")
            print(f"  Size: {data.get('size')}")
            return True
        else:
            print_status(f"Upload test failed with status {response.status_code}", "ERROR")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_status(f"Upload test error: {str(e)}", "ERROR")
        return False

def cleanup_test_file():
    """Clean up the test file"""
    try:
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)
            print_status(f"Cleaned up test file: {TEST_FILE}", "SUCCESS")
    except Exception as e:
        print_status(f"Failed to cleanup test file: {str(e)}", "WARNING")

def test_server_connectivity():
    """Test basic server connectivity"""
    try:
        response = requests.get(SERVER_URL, timeout=5)
        print_status("Server is reachable", "SUCCESS")
        return True
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to server - is it running?", "ERROR")
        return False
    except Exception as e:
        print_status(f"Connectivity test error: {str(e)}", "ERROR")
        return False

def main():
    """Run all tests"""
    print_status("🎬 SoulStream Media Server Test Suite", "INFO")
    print("=" * 50)
    
    tests = [
        ("Server Connectivity", test_server_connectivity),
        ("Health Endpoint", test_health_endpoint),
        ("Files Endpoint", test_files_endpoint),
        ("Main Page", test_main_page),
        ("Upload Test", test_upload),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print_status(f"{test_name} failed", "ERROR")
    
    # Cleanup
    cleanup_test_file()
    
    # Summary
    print("\n" + "=" * 50)
    print_status(f"Test Results: {passed}/{total} tests passed", 
                "SUCCESS" if passed == total else "WARNING")
    
    if passed == total:
        print_status("🎉 All tests passed! Your SoulStream server is working correctly.", "SUCCESS")
    else:
        print_status("⚠️  Some tests failed. Check the server configuration and logs.", "WARNING")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 