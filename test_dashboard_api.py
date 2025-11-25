"""
Test Dashboard API Endpoints
"""
import requests

BASE_URL = "https://diabetes-predictor-ai.azurewebsites.net"

print("=" * 60)
print("🧪 TESTING DASHBOARD API ENDPOINTS")
print("=" * 60)

# Create a session to maintain cookies
session = requests.Session()

# Test 1: Check if session works
print("\n1️⃣ Testing /api/session endpoint...")
try:
    response = session.get(f"{BASE_URL}/api/session")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Login
print("\n2️⃣ Testing login...")
try:
    login_data = {
        "username": "admin",  # Change to your username
        "password": "admin123"  # Change to your password
    }
    response = session.post(f"{BASE_URL}/api/login", json=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Check session after login
print("\n3️⃣ Testing /api/session after login...")
try:
    response = session.get(f"{BASE_URL}/api/session")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Authenticated: {data.get('authenticated')}")
    if data.get('user'):
        print(f"   User: {data['user'].get('username')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Get all predictions
print("\n4️⃣ Testing /api/user/all_predictions...")
try:
    response = session.get(f"{BASE_URL}/api/user/all_predictions")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Success: {data.get('success')}")
    print(f"   Total Predictions: {data.get('total', len(data.get('predictions', [])))}")
    if data.get('predictions'):
        print(f"   First prediction: {data['predictions'][0].get('patient_name')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Get latest prediction
print("\n5️⃣ Testing /api/user/latest_prediction...")
try:
    response = session.get(f"{BASE_URL}/api/user/latest_prediction")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Success: {data.get('success')}")
    if data.get('prediction'):
        pred = data['prediction']
        print(f"   Patient: {pred.get('patient_name')}")
        print(f"   Risk: {pred.get('risk_level')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: Get reports
print("\n6️⃣ Testing /api/user/reports...")
try:
    response = session.get(f"{BASE_URL}/api/user/reports")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Success: {data.get('success')}")
    print(f"   Total Reports: {data.get('total', len(data.get('reports', [])))}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ TEST COMPLETE")
print("=" * 60)
