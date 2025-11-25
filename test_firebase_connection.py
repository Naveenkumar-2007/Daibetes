"""
Test Firebase connection and verify data storage
"""
from firebase_config import db_ref, firebase_initialized, use_rest_api
import requests

print('='*60)
print('🔥 FIREBASE CONNECTION TEST')
print('='*60)

print(f'✓ Firebase Initialized: {firebase_initialized}')
print(f'✓ Using REST API: {use_rest_api}')
print(f'✓ Database type: {type(db_ref).__name__}')

# Test Firebase connection
try:
    resp = requests.get('https://diabetes-prediction-22082-default-rtdb.firebaseio.com/.json')
    print(f'✓ Connection test: {resp.status_code} - {"✅ Connected" if resp.status_code == 200 else "❌ Failed"}')
    
    if resp.status_code == 200:
        data = resp.json()
        if data:
            print(f'✓ Database has data: {len(data)} root keys')
            if 'predictions' in data:
                print(f'  - Predictions: {len(data["predictions"])} records')
            if 'users' in data:
                print(f'  - Users: {len(data["users"])} users')
        else:
            print('⚠️ Database is empty (new database)')
    else:
        print(f'❌ HTTP {resp.status_code}: {resp.text[:200]}')
        
except Exception as e:
    print(f'❌ Connection error: {e}')

print('='*60)

# Test prediction save
print('\n📝 Testing Prediction Save...')
try:
    from firebase_config import save_patient_data
    
    test_patient = {
        'name': 'Test Patient',
        'age': 45,
        'sex': 'Male',
        'contact': '9999999999',
        'address': 'Test Address'
    }
    
    test_prediction = {
        'prediction': 'Low Risk / No Diabetes',
        'risk_level': 'low',
        'confidence': 92.5,
        'features': [0, 120, 80, 20, 100, 25.5, 0.5, 45, 1147.5, 1.2]
    }
    
    doc_id = save_patient_data(test_patient, test_prediction, user_id='test_user_123')
    
    if doc_id:
        print(f'✅ Test prediction saved: {doc_id}')
        
        # Verify it's in Firebase
        verify_resp = requests.get(f'https://diabetes-prediction-22082-default-rtdb.firebaseio.com/predictions/{doc_id}.json')
        if verify_resp.status_code == 200:
            saved_data = verify_resp.json()
            if saved_data:
                print(f'✅ Verified in Firebase:')
                print(f'   - Patient: {saved_data.get("patient_name")}')
                print(f'   - Risk: {saved_data.get("risk_level")}')
                print(f'   - User ID: {saved_data.get("user_id")}')
            else:
                print(f'⚠️ Document exists but empty')
        else:
            print(f'❌ Could not verify: HTTP {verify_resp.status_code}')
    else:
        print('❌ Failed to save test prediction')
        
except Exception as e:
    print(f'❌ Save test error: {e}')
    import traceback
    traceback.print_exc()

print('='*60)
print('✅ TEST COMPLETE')
print('='*60)
