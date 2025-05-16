import requests
import json
import sys
import time
import traceback

# Make sure we have the requests module
try:
    import requests
except ImportError:
    print("The 'requests' module is not installed. Installing now...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    print("Requests module installed successfully.")
    import requests

# URLs
BASE_URL = "http://localhost:5000/api"
LOGIN_URL = f"{BASE_URL}/login"
USER_URL = f"{BASE_URL}/user"
DIVIDENDS_URL = f"{BASE_URL}/dividends"

# Credentials - Default test user
credentials = {
    "email": "root@example.com",
    "password": "password123"  # Correct password from auth_service.py
}

try:
    # Create a session to maintain cookies
    session = requests.Session()
      # Step 1: Wait for server to be ready
    print("Waiting for server to be ready...")
    max_attempts = 10
    for i in range(max_attempts):
        try:
            # Try a different endpoint that should be available
            health_check = session.get(f"{BASE_URL}/system-status", timeout=2)
            if health_check.status_code == 200:
                print("Server is ready!")
                break
            print(f"Attempt {i+1}/{max_attempts}: Server responded with status {health_check.status_code}, waiting...")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i+1}/{max_attempts}: Server not ready yet ({str(e)}), waiting...")
        time.sleep(3)
    else:
        print("Warning: Could not confirm server is ready, proceeding anyway...")
      # Step 2: Login
    print("\nAttempting login...")
    login_response = session.post(LOGIN_URL, json=credentials)
    print(f"Login Status Code: {login_response.status_code}")
    
    try:
        login_data = login_response.json()
        print(f"Login Response: {json.dumps(login_data, indent=2)}")
    except ValueError:
        print(f"Login Response (not JSON): {login_response.text}")
    
    # Print detailed information about cookies
    print("\nDetailed Cookie Information:")
    for cookie in session.cookies:
        print(f"  {cookie.name}: {cookie.value}")
        print(f"    Domain: {cookie.domain}")
        print(f"    Path: {cookie.path}")
        print(f"    Expires: {cookie.expires}")
        print(f"    Secure: {cookie.secure}")
        print(f"    HttpOnly: {cookie.has_nonstandard_attr('HttpOnly')}")
        print(f"    SameSite: {cookie.get_nonstandard_attr('SameSite')}")
    
    print(f"\nSession headers: {session.headers}")
    
    # Step 3: Check current user
    print("\nChecking current user...")
    user_response = session.get(USER_URL)
    print(f"User Status Code: {user_response.status_code}")
    
    try:
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"User Response: {json.dumps(user_data, indent=2)}")
        else:
            print(f"User Response: {user_response.text}")
    except ValueError:
        print(f"User Response (not JSON): {user_response.text}")
    
    # Step 4: Try to access dividends
    print("\nAttempting to access dividends...")
    dividends_response = session.get(DIVIDENDS_URL)
    print(f"Dividends Status Code: {dividends_response.status_code}")
    
    try:
        if dividends_response.status_code == 200:
            dividends_data = dividends_response.json()
            print(f"Dividends Response: {json.dumps(dividends_data, indent=2)}")
        else:
            print(f"Dividends Response: {dividends_response.text}")
    except ValueError:
        print(f"Dividends Response (not JSON): {dividends_response.text}")

except Exception as e:
    print(f"An error occurred: {str(e)}")
    traceback.print_exc()
