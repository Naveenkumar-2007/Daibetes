"""Test Firebase Statistics"""
from firebase_config import db, get_statistics
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*60)
print("🔥 Firebase Statistics Test")
print("="*60 + "\n")

# Test 1: Check if Firebase is initialized
print("1️⃣ Testing Firebase initialization...")
try:
    users_ref = db.reference('users')
    users_data = users_ref.get()
    
    if users_data:
        print(f"   ✅ Firebase connected!")
        print(f"   👥 Total users in database: {len(users_data)}")
        
        # Show sample user
        sample_user = list(users_data.items())[0]
        print(f"   📝 Sample user: {sample_user[1].get('username', 'N/A')}")
    else:
        print("   ⚠️ No users found in Firebase")
except Exception as e:
    print(f"   ❌ Firebase error: {e}")

# Test 2: Check predictions
print("\n2️⃣ Testing predictions...")
try:
    pred_ref = db.reference('predictions')
    pred_data = pred_ref.get()
    
    if pred_data:
        print(f"   ✅ Predictions found!")
        print(f"   📊 Total predictions: {len(pred_data)}")
        
        # Count high risk
        high_risk = sum(1 for p in pred_data.values() if isinstance(p, dict) and p.get('risk_level') == 'high')
        print(f"   🚨 High risk: {high_risk}")
    else:
        print("   ⚠️ No predictions found")
except Exception as e:
    print(f"   ❌ Predictions error: {e}")

# Test 3: Check reports
print("\n3️⃣ Testing reports...")
try:
    reports_ref = db.reference('reports')
    reports_data = reports_ref.get()
    
    if reports_data:
        total_reports = 0
        for user_reports in reports_data.values():
            if isinstance(user_reports, dict):
                total_reports += len(user_reports)
        
        print(f"   ✅ Reports found!")
        print(f"   📄 Total reports: {total_reports}")
    else:
        print("   ⚠️ No reports found")
except Exception as e:
    print(f"   ❌ Reports error: {e}")

# Test 4: Use get_statistics function
print("\n4️⃣ Testing get_statistics() function...")
try:
    stats = get_statistics()
    print(f"   ✅ Statistics:")
    print(f"      • Total predictions: {stats.get('total_predictions', 0)}")
    print(f"      • High risk: {stats.get('high_risk_count', 0)}")
    print(f"      • Low risk: {stats.get('low_risk_count', 0)}")
except Exception as e:
    print(f"   ❌ Statistics error: {e}")

print("\n" + "="*60 + "\n")
