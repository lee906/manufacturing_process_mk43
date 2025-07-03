import requests
import json

# Test if the backend is running
try:
    # Test the factory summary endpoint
    response = requests.get('http://localhost:8080/api/kpi/factory/summary', timeout=10)
    print(f"Factory Summary - Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Factory Summary endpoint is working!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Factory Summary endpoint failed with status {response.status_code}")
        print(f"Error: {response.text}")
except requests.exceptions.ConnectRefused:
    print("❌ Backend is not running - Connection refused")
except requests.exceptions.ConnectionError:
    print("❌ Backend is not running - Connection error")
except Exception as e:
    print(f"❌ Error testing Factory Summary: {e}")

print("\n" + "="*50 + "\n")

try:
    # Test the latest KPI endpoint
    response = requests.get('http://localhost:8080/api/kpi/latest', timeout=10)
    print(f"Latest KPI - Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Latest KPI endpoint is working!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Latest KPI endpoint failed with status {response.status_code}")
        print(f"Error: {response.text}")
except requests.exceptions.ConnectRefused:
    print("❌ Backend is not running - Connection refused")
except requests.exceptions.ConnectionError:
    print("❌ Backend is not running - Connection error")
except Exception as e:
    print(f"❌ Error testing Latest KPI: {e}")