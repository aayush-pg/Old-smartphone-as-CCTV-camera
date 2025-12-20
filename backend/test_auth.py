"""
Test script for Login API
This script tests the auth.py API
"""
import requests
import json

# Server URL
BASE_URL = "http://localhost:5000"

def test_login_success():
    """Test with correct credentials"""
    print("\n" + "="*50)
    print("TEST 1: Correct Credentials (Success Case)")
    print("="*50)
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": "admin",
        "password": "123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("SUCCESS: Login successful!")
        else:
            print("FAILED: Expected 200, got", response.status_code)
    except Exception as e:
        print(f"ERROR: {e}")

def test_login_failure():
    """Test with wrong credentials"""
    print("\n" + "="*50)
    print("TEST 2: Wrong Credentials (Error Case)")
    print("="*50)
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": "admin",
        "password": "wrong_password"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("SUCCESS: Correctly rejected invalid credentials!")
        else:
            print("FAILED: Expected 401, got", response.status_code)
    except Exception as e:
        print(f"ERROR: {e}")

def test_health_check():
    """Test server health"""
    print("\n" + "="*50)
    print("TEST 0: Server Health Check")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Server is running!")
        else:
            print("FAILED: Server issue!")
    except Exception as e:
        print(f"ERROR: Server not running! {e}")
        print("   Make sure server is running: python app.py")

if __name__ == "__main__":
    print("\nStarting API Tests...")
    print("Make sure server is running on http://localhost:5000")
    
    # Health check first
    test_health_check()
    
    # Then test login
    test_login_success()
    test_login_failure()
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("="*50)

