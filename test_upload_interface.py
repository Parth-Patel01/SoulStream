#!/usr/bin/env python3
"""
Test script to check SoulStream upload interface accessibility
"""

import requests
import sys

def test_upload_interface():
    """Test if the upload interface is accessible"""
    
    base_url = "http://192.168.18.20:8080"
    endpoints = [
        "/",
        "/index.html",
        "/upload"
    ]
    
    print("🎬 Testing SoulStream Upload Interface")
    print("=" * 40)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=10)
            print(f"\n📡 Testing: {url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                if "SoulStream" in content and "upload" in content.lower():
                    print("✅ Upload interface found!")
                    print(f"URL to use: {url}")
                    return url
                elif "SoulStream" in content:
                    print("ℹ️  Server status page found")
                else:
                    print("❓ Unknown page content")
            else:
                print(f"❌ Failed with status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {url}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    return None

def check_server_health():
    """Check server health endpoint"""
    try:
        response = requests.get("http://192.168.18.20:8080/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🏥 Server Health:")
            print(f"Status: {data.get('status')}")
            print(f"Upload folder: {data.get('upload_folder')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 SoulStream Upload Interface Test")
    print("=" * 40)
    
    # Test server health first
    if check_server_health():
        # Test upload interface
        upload_url = test_upload_interface()
        
        if upload_url:
            print(f"\n🎉 Success! Use this URL for uploading:")
            print(f"   {upload_url}")
        else:
            print("\n❌ Upload interface not found")
            print("Try these URLs manually:")
            print("   http://192.168.18.20:8080/")
            print("   http://192.168.18.20:8080/index.html")
            print("   http://192.168.18.20:8080/upload")
    else:
        print("\n❌ Server is not responding")
        print("Check if the service is running:")
        print("   sudo systemctl status soulstream") 