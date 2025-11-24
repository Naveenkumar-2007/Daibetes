#!/usr/bin/env python3
"""
Startup Test - Verify all imports work before launching Flask app
"""
import sys
import os

print("=" * 60)
print("STARTUP TEST - Verifying Dependencies")
print("=" * 60)

# Test 1: Python Version
print(f"\n✓ Python Version: {sys.version}")

# Test 2: Core imports
try:
    import flask
    print(f"✓ Flask: {flask.__version__}")
except Exception as e:
    print(f"✗ Flask import failed: {e}")
    sys.exit(1)

# Test 3: Firebase
try:
    import firebase_admin
    print(f"✓ Firebase Admin: {firebase_admin.__version__}")
except Exception as e:
    print(f"✗ Firebase import failed: {e}")
    sys.exit(1)

# Test 4: ML Libraries
try:
    import numpy as np
    import sklearn
    import xgboost as xgb
    print(f"✓ NumPy: {np.__version__}")
    print(f"✓ Scikit-learn: {sklearn.__version__}")
    print(f"✓ XGBoost: {xgb.__version__}")
except Exception as e:
    print(f"✗ ML library import failed: {e}")
    sys.exit(1)

# Test 5: LangChain
try:
    from langchain_groq import ChatGroq
    print(f"✓ LangChain Groq imported successfully")
except Exception as e:
    print(f"✗ LangChain import failed: {e}")
    sys.exit(1)

# Test 6: Environment Variables
env_vars = ['GROQ_API_KEY', 'FIREBASE_API_KEY', 'FIREBASE_PROJECT_ID']
for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"✓ {var}: {'*' * 10} (set)")
    else:
        print(f"⚠ {var}: not set")

# Test 7: Try importing the main Flask app
print("\n" + "=" * 60)
print("Attempting to import flask_app.py...")
print("=" * 60)

try:
    import flask_app
    print("✓ flask_app.py imported successfully!")
    print(f"✓ Flask app object: {flask_app.app}")
    print("\n🎉 ALL TESTS PASSED! App should start successfully.")
except Exception as e:
    print(f"\n✗ FAILED to import flask_app.py")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
